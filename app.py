import sqlite3
from datetime import datetime

from flask import (
    Flask,
    g,
    jsonify,
    redirect,
    render_template_string,
    request,
    url_for,
    flash,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "replace-this-with-a-long-random-secret"

login_manager = LoginManager(app)
login_manager.login_view = "login"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    manage_session=True,
)

DATABASE = "chat.db"

# user_id -> set of Socket.IO session IDs
online_users = {}


class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = str(user_id)
        self.username = username

    @staticmethod
    def from_id(user_id):
        db = get_db()
        row = db.execute(
            "SELECT id, username FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

        if row:
            return User(row["id"], row["username"])

        return None

    @staticmethod
    def from_username(username):
        db = get_db()
        row = db.execute(
            "SELECT id, username FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if row:
            return User(row["id"], row["username"])

        return None


@login_manager.user_loader
def load_user(user_id):
    return User.from_id(user_id)


def get_db():
    if "database" not in g:
        g.database = sqlite3.connect(DATABASE)
        g.database.row_factory = sqlite3.Row

    return g.database


@app.teardown_appcontext
def close_db(error=None):
    database = g.pop("database", None)

    if database is not None:
        database.close()


def init_db():
    database = get_db()

    database.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS group_members (
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            UNIQUE(group_id, user_id),
            FOREIGN KEY (group_id) REFERENCES groups(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            chat_type TEXT NOT NULL,
            group_id INTEGER,
            recipient_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (group_id) REFERENCES groups(id),
            FOREIGN KEY (recipient_id) REFERENCES users(id)
        );
        """
    )

    database.commit()


def now():
    return datetime.now().strftime("%H:%M")


def user_is_in_group(user_id, group_id):
    database = get_db()

    row = database.execute(
        """
        SELECT 1
        FROM group_members
        WHERE group_id = ? AND user_id = ?
        """,
        (group_id, user_id),
    ).fetchone()

    return row is not None


def get_user_status(user_id):
    return bool(online_users.get(str(user_id)))


def message_to_dict(row):
    return {
        "id": row["id"],
        "sender_id": row["sender_id"],
        "sender": row["sender"],
        "message": row["message"],
        "chat_type": row["chat_type"],
        "group_id": row["group_id"],
        "recipient_id": row["recipient_id"],
        "time": row["created_at"],
    }


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("chat"))

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("chat"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.from_username(username)

        if user:
            database = get_db()
            row = database.execute(
                "SELECT password_hash FROM users WHERE id = ?",
                (user.id,),
            ).fetchone()

            if row and check_password_hash(row["password_hash"], password):
                login_user(user)
                return redirect(url_for("chat"))

        flash("Invalid username or password.")

    return render_template_string(AUTH_HTML, register=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("chat"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 3:
            flash("Username must be at least 3 characters.")
            return render_template_string(AUTH_HTML, register=True)

        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return render_template_string(AUTH_HTML, register=True)

        if User.from_username(username):
            flash("That username is already taken.")
            return render_template_string(AUTH_HTML, register=True)

        database = get_db()
        database.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, generate_password_hash(password)),
        )
        database.commit()

        flash("Account created. You can now log in.")
        return redirect(url_for("login"))

    return render_template_string(AUTH_HTML, register=True)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/chat")
@login_required
def chat():
    return render_template_string(
        CHAT_HTML,
        username=current_user.username,
    )


@app.route("/api/users")
@login_required
def users_api():
    database = get_db()

    rows = database.execute(
        """
        SELECT id, username
        FROM users
        WHERE id != ?
        ORDER BY username COLLATE NOCASE
        """,
        (current_user.id,),
    ).fetchall()

    return jsonify(
        [
            {
                "id": row["id"],
                "username": row["username"],
                "online": get_user_status(row["id"]),
            }
            for row in rows
        ]
    )


@app.route("/api/groups")
@login_required
def groups_api():
    database = get_db()

    rows = database.execute(
        """
        SELECT g.id, g.name, g.owner_id
        FROM groups g
        JOIN group_members gm ON gm.group_id = g.id
        WHERE gm.user_id = ?
        ORDER BY g.name COLLATE NOCASE
        """,
        (current_user.id,),
    ).fetchall()

    return jsonify(
        [
            {
                "id": row["id"],
                "name": row["name"],
                "owner_id": row["owner_id"],
            }
            for row in rows
        ]
    )


@app.route("/api/groups", methods=["POST"])
@login_required
def create_group():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()[:50]

    if not name:
        return jsonify({"error": "Group name is required"}), 400

    database = get_db()

    cursor = database.execute(
        """
        INSERT INTO groups (name, owner_id)
        VALUES (?, ?)
        """,
        (name, current_user.id),
    )

    group_id = cursor.lastrowid

    database.execute(
        """
        INSERT INTO group_members (group_id, user_id)
        VALUES (?, ?)
        """,
        (group_id, current_user.id),
    )

    database.commit()

    join_room(f"group:{group_id}")

    return jsonify(
        {
            "id": group_id,
            "name": name,
            "owner_id": int(current_user.id),
        }
    )


@app.route("/api/groups/<int:group_id>/members", methods=["POST"])
@login_required
def add_group_member(group_id):
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()

    database = get_db()

    group = database.execute(
        "SELECT owner_id FROM groups WHERE id = ?",
        (group_id,),
    ).fetchone()

    if not group:
        return jsonify({"error": "Group not found"}), 404

    if int(group["owner_id"]) != int(current_user.id):
        return jsonify({"error": "Only the group owner can add members"}), 403

    user = User.from_username(username)

    if not user:
        return jsonify({"error": "User not found"}), 404

    database.execute(
        """
        INSERT OR IGNORE INTO group_members (group_id, user_id)
        VALUES (?, ?)
        """,
        (group_id, user.id),
    )
    database.commit()

    socketio.emit(
        "group_added",
        {
            "id": group_id,
            "name": database.execute(
                "SELECT name FROM groups WHERE id = ?",
                (group_id,),
            ).fetchone()["name"],
        },
        room=f"user:{user.id}",
    )

    return jsonify({"success": True})


@app.route("/api/messages")
@login_required
def messages_api():
    chat_type = request.args.get("type", "")
    chat_id = request.args.get("id", type=int)

    if chat_type not in ("group", "private") or not chat_id:
        return jsonify({"error": "Invalid chat"}), 400

    database = get_db()

    if chat_type == "group":
        if not user_is_in_group(current_user.id, chat_id):
            return jsonify({"error": "You are not in this group"}), 403

        rows = database.execute(
            """
            SELECT
                m.*,
                u.username AS sender
            FROM messages m
            JOIN users u ON u.id = m.sender_id
            WHERE m.chat_type = 'group' AND m.group_id = ?
            ORDER BY m.id ASC
            LIMIT 200
            """,
            (chat_id,),
        ).fetchall()

    else:
        other_user = User.from_id(chat_id)

        if not other_user:
            return jsonify({"error": "User not found"}), 404

        rows = database.execute(
            """
            SELECT
                m.*,
                u.username AS sender
            FROM messages m
            JOIN users u ON u.id = m.sender_id
            WHERE m.chat_type = 'private'
              AND (
                    (m.sender_id = ? AND m.recipient_id = ?)
                 OR (m.sender_id = ? AND m.recipient_id = ?)
              )
            ORDER BY m.id ASC
            LIMIT 200
            """,
            (
                current_user.id,
                chat_id,
                chat_id,
                current_user.id,
            ),
        ).fetchall()

    return jsonify([message_to_dict(row) for row in rows])


@socketio.on("connect")
def handle_connect():
    if not current_user.is_authenticated:
        return False

    user_id = str(current_user.id)

    online_users.setdefault(user_id, set()).add(request.sid)

    join_room(f"user:{user_id}")

    database = get_db()
    groups = database.execute(
        """
        SELECT group_id
        FROM group_members
        WHERE user_id = ?
        """,
        (current_user.id,),
    ).fetchall()

    for group in groups:
        join_room(f"group:{group['group_id']}")

    socketio.emit(
        "presence",
        {
            "user_id": int(user_id),
            "online": True,
        },
    )


@socketio.on("disconnect")
def handle_disconnect():
    if not current_user.is_authenticated:
        return

    user_id = str(current_user.id)

    if user_id in online_users:
        online_users[user_id].discard(request.sid)

        if not online_users[user_id]:
            del online_users[user_id]

            socketio.emit(
                "presence",
                {
                    "user_id": int(user_id),
                    "online": False,
                },
            )


@socketio.on("send_message")
def handle_send_message(data):
    if not current_user.is_authenticated:
        return

    chat_type = data.get("type")
    chat_id = data.get("id")
    message = str(data.get("message", "")).strip()[:1000]

    try:
        chat_id = int(chat_id)
    except (TypeError, ValueError):
        return

    if not message or chat_type not in ("group", "private"):
        return

    database = get_db()
    recipient_id = None
    group_id = None

    if chat_type == "group":
        if not user_is_in_group(current_user.id, chat_id):
            return

        group_id = chat_id
        room = f"group:{chat_id}"

    else:
        recipient = User.from_id(chat_id)

        if not recipient or int(recipient.id) == int(current_user.id):
            return

        recipient_id = int(recipient.id)

        room_a = f"user:{current_user.id}"
        room_b = f"user:{recipient_id}"

        database.execute(
            """
            INSERT INTO messages
            (sender_id, message, chat_type, group_id, recipient_id, created_at)
            VALUES (?, ?, 'private', NULL, ?, ?)
            """,
            (
                current_user.id,
                message,
                recipient_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        database.commit()

        payload = {
            "sender_id": int(current_user.id),
            "sender": current_user.username,
            "message": message,
            "chat_type": "private",
            "group_id": None,
            "recipient_id": recipient_id,
            "time": now(),
        }

        socketio.emit("new_message", payload, room=room_a)
        socketio.emit("new_message", payload, room=room_b)
        return

    database.execute(
        """
        INSERT INTO messages
        (sender_id, message, chat_type, group_id, recipient_id, created_at)
        VALUES (?, ?, 'group', ?, NULL, ?)
        """,
        (
            current_user.id,
            message,
            group_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    database.commit()

    emit(
        "new_message",
        {
            "sender_id": int(current_user.id),
            "sender": current_user.username,
            "message": message,
            "chat_type": "group",
            "group_id": group_id,
            "recipient_id": None,
            "time": now(),
        },
        room=room,
    )


AUTH_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ "Create account" if register else "Login" }}</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            background: #0f172a;
            color: white;
            font-family: Arial, sans-serif;
        }
        .card {
            width: min(400px, 92vw);
            background: #1e293b;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 20px 70px #0008;
        }
        h1 { text-align: center; }
        form { display: grid; gap: 12px; }
        input, button {
            width: 100%;
            padding: 13px;
            border-radius: 8px;
            font-size: 15px;
        }
        input {
            border: 1px solid #475569;
            background: #0f172a;
            color: white;
        }
        button {
            border: 0;
            background: #2563eb;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        a { color: #93c5fd; }
        .link { text-align: center; margin-top: 16px; }
        .flash {
            background: #991b1b;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 12px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>{{ "Create account" if register else "Login" }}</h1>

        {% with messages = get_flashed_messages() %}
            {% for message in messages %}
                <div class="flash">{{ message }}</div>
            {% endfor %}
        {% endwith %}

        <form method="POST">
            <input name="username" placeholder="Username" minlength="3" required>
            <input name="password" type="password" placeholder="Password" minlength="6" required>
            <button>{{ "Sign up" if register else "Log in" }}</button>
        </form>

        <div class="link">
            {% if register %}
                Already have an account?
                <a href="{{ url_for('login') }}">Log in</a>
            {% else %}
                Need an account?
                <a href="{{ url_for('register') }}">Sign up</a>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


CHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Chat</title>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            height: 100vh;
            background: #0f172a;
            color: #f8fafc;
            font-family: Arial, sans-serif;
        }
        .app {
            height: 100vh;
            display: grid;
            grid-template-columns: 280px 1fr;
        }
        aside {
            background: #111827;
            border-right: 1px solid #334155;
            padding: 16px;
            overflow-y: auto;
        }
        main {
            display: flex;
            min-width: 0;
            flex-direction: column;
        }
        .brand {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }
        h1, h2 { margin: 0; }
        h1 { font-size: 20px; }
        h2 { font-size: 18px; }
        .logout {
            color: #fca5a5;
            text-decoration: none;
            font-size: 13px;
        }
        .section-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #94a3b8;
            font-size: 12px;
            text-transform: uppercase;
            margin: 18px 0 8px;
        }
        .small-button {
            border: 0;
            border-radius: 5px;
            background: #2563eb;
            color: white;
            cursor: pointer;
            padding: 4px 8px;
        }
        .chat-item {
            display: flex;
            align-items: center;
            gap: 9px;
            width: 100%;
            padding: 10px;
            margin: 3px 0;
            border: 0;
            border-radius: 8px;
            text-align: left;
            color: #e2e8f0;
            background: transparent;
            cursor: pointer;
        }
        .chat-item:hover, .chat-item.selected {
            background: #334155;
        }
        .online-dot {
            width: 9px;
            height: 9px;
            flex: 0 0 9px;
            border-radius: 50%;
            background: #64748b;
        }
        .online-dot.online { background: #22c55e; }
        header {
            display: flex;
            align-items: center;
            padding: 18px 22px;
            border-bottom: 1px solid #334155;
            background: #1e293b;
        }
        header small {
            display: block;
            margin-top: 4px;
            color: #94a3b8;
        }
        #messages {
            flex: 1;
            overflow-y: auto;
            padding: 22px;
        }
        .message { margin-bottom: 16px; }
        .message-meta {
            display: flex;
            gap: 9px;
            align-items: center;
            margin-bottom: 4px;
        }
        .sender { color: #93c5fd; font-weight: bold; }
        .time { color: #94a3b8; font-size: 12px; }
        .message-text { overflow-wrap: anywhere; }
        form {
            display: flex;
            gap: 10px;
            padding: 16px;
            background: #111827;
            border-top: 1px solid #334155;
        }
        input {
            flex: 1;
            min-width: 0;
            padding: 13px;
            border: 1px solid #475569;
            border-radius: 8px;
            background: #1e293b;
            color: white;
            outline: none;
        }
        button.send {
            padding: 0 22px;
            border: 0;
            border-radius: 8px;
            background: #2563eb;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        .empty {
            color: #94a3b8;
            text-align: center;
            margin-top: 40px;
        }
        @media (max-width: 700px) {
            .app { grid-template-columns: 190px 1fr; }
            aside { padding: 10px; }
            header { padding: 14px; }
            #messages { padding: 14px; }
        }
    </style>
</head>
<body>
<div class="app">
    <aside>
        <div class="brand">
            <h1>ChatApp</h1>
            <a class="logout" href="/logout">Logout</a>
        </div>

        <div class="section-title">
            <span>Groups</span>
            <button class="small-button" onclick="createGroup()">+</button>
        </div>
        <div id="groups"></div>

        <div class="section-title">
            <span>People</span>
        </div>
        <div id="users"></div>
    </aside>

    <main>
        <header>
            <div>
                <h2 id="chat-title">Choose a chat</h2>
                <small id="chat-status">Select a group or person</small>
            </div>
        </header>

        <div id="messages">
            <div class="empty">Choose a group or person to start chatting.</div>
        </div>

        <form id="message-form">
            <input id="message-input" placeholder="Type a message..." maxlength="1000" autocomplete="off">
            <button class="send">Send</button>
        </form>
    </main>
</div>

<script>
    const socket = io();

    const groupsEl = document.getElementById("groups");
    const usersEl = document.getElementById("users");
    const messagesEl = document.getElementById("messages");
    const titleEl = document.getElementById("chat-title");
    const statusEl = document.getElementById("chat-status");
    const form = document.getElementById("message-form");
    const input = document.getElementById("message-input");

    let currentChat = null;
    let users = [];

    function escapeHtml(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    async function loadSidebar() {
        const [groupsResponse, usersResponse] = await Promise.all([
            fetch("/api/groups"),
            fetch("/api/users")
        ]);

        const groups = await groupsResponse.json();
        users = await usersResponse.json();

        groupsEl.innerHTML = "";

        groups.forEach(group => {
            const button = document.createElement("button");
            button.className = "chat-item";
            button.dataset.chatKey = `group-${group.id}`;
            button.textContent = `# ${group.name}`;
            button.onclick = () => openChat({
                type: "group",
                id: group.id,
                name: group.name
            });
            groupsEl.appendChild(button);
        });

        usersEl.innerHTML = "";

        users.forEach(user => {
            const button = document.createElement("button");
            button.className = "chat-item";
            button.dataset.chatKey = `private-${user.id}`;

            const dot = document.createElement("span");
            dot.className = "online-dot" + (user.online ? " online" : "");

            const name = document.createElement("span");
            name.textContent = user.username;

            button.appendChild(dot);
            button.appendChild(name);

            button.onclick = () => openChat({
                type: "private",
                id: user.id,
                name: user.username,
                online: user.online
            });

            usersEl.appendChild(button);
        });
    }

    async function openChat(chat) {
        currentChat = chat;

        document.querySelectorAll(".chat-item").forEach(item => {
            item.classList.remove("selected");
        });

        const selected = document.querySelector(
            `[data-chat-key="${chat.type}-${chat.id}"]`
        );

        if (selected) {
            selected.classList.add("selected");
        }

        titleEl.textContent = chat.type === "group"
            ? `# ${chat.name}`
            : chat.name;

        statusEl.textContent = chat.type === "group"
            ? "Group chat"
            : (chat.online ? "Online" : "Offline");

        const response = await fetch(
            `/api/messages?type=${chat.type}&id=${chat.id}`
        );

        const messages = await response.json();

        messagesEl.innerHTML = "";
        messages.forEach(addMessage);
        scrollDown();
    }

    function addMessage(message) {
        if (!currentChat) return;

        if (message.chat_type !== currentChat.type) return;

        if (currentChat.type === "group") {
            if (message.group_id !== currentChat.id) return;
        } else {
            const matchesPrivateChat =
                (
                    message.sender_id === currentChat.id ||
                    message.recipient_id === currentChat.id
                );

            if (!matchesPrivateChat) return;
        }

        const div = document.createElement("div");
        div.className = "message";

        div.innerHTML = `
            <div class="message-meta">
                <span class="sender">${escapeHtml(message.sender)}</span>
                <span class="time">${escapeHtml(message.time)}</span>
            </div>
            <div class="message-text">${escapeHtml(message.message)}</div>
        `;

        messagesEl.appendChild(div);
    }

    function scrollDown() {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    form.addEventListener("submit", event => {
        event.preventDefault();

        if (!currentChat) {
            alert("Choose a chat first.");
            return;
        }

        const message = input.value.trim();

        if (!message) return;

        socket.emit("send_message", {
            type: currentChat.type,
            id: currentChat.id,
            message: message
        });

        input.value = "";
        input.focus();
    });

    socket.on("new_message", message => {
        addMessage(message);
        scrollDown();
    });

    socket.on("presence", data => {
        const user = users.find(item => item.id === data.user_id);

        if (user) {
            user.online = data.online;
            loadSidebar();

            if (
                currentChat &&
                currentChat.type === "private" &&
                currentChat.id === data.user_id
            ) {
                currentChat.online = data.online;
                statusEl.textContent = data.online ? "Online" : "Offline";
            }
        }
    });

    socket.on("group_added", async () => {
        await loadSidebar();
    });

    async function createGroup() {
        const name = prompt("Enter a group name:");

        if (!name || !name.trim()) return;

        const response = await fetch("/api/groups", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name: name.trim()})
        });

        if (!response.ok) {
            alert("Could not create group.");
            return;
        }

        const group = await response.json();
        await loadSidebar();

        openChat({
            type: "group",
            id: group.id,
            name: group.name
        });

        const invite = prompt(
            "Optional: enter another username to add to this group, or press Cancel."
        );

        if (invite && invite.trim()) {
            await fetch(`/api/groups/${group.id}/members`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username: invite.trim()})
            });
        }
    }

    loadSidebar();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    with app.app_context():
        init_db()

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True,
    )