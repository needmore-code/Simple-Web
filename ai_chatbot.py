import os

from flask import Flask, jsonify, render_template_string, request
from openai import OpenAI, APIError

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    api_key="ollama",
)

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Chatbot</title>
  <style>
    * { box-sizing: border-box; }
    body {
      max-width: 760px;
      margin: 30px auto;
      padding: 0 16px;
      font: 16px system-ui, sans-serif;
      background: #f5f7fa;
      color: #17202a;
    }
    h1 { margin-bottom: 16px; }
    #messages {
      min-height: 300px;
      max-height: 60vh;
      overflow-y: auto;
      border: 1px solid #ccd4dc;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 12px;
      background: white;
    }
    .message { white-space: pre-wrap; overflow-wrap: anywhere; margin: 0 0 14px; }
    form { display: flex; gap: 8px; }
    input {
      flex: 1;
      min-width: 0;
      padding: 12px;
      border: 1px solid #ccd4dc;
      border-radius: 6px;
    }
    button {
      padding: 12px 18px;
      border: 0;
      border-radius: 6px;
      background: #2563eb;
      color: white;
      cursor: pointer;
    }
    button:disabled { background: #94a3b8; cursor: wait; }
    #status { min-height: 24px; color: #555; }
  </style>
</head>
<body>
  <h1>AI Chatbot</h1>
  <div id="messages" aria-live="polite"></div>
  <p id="status"></p>
  <form id="chat-form">
    <input id="message-input" maxlength="4000" placeholder="Ask something..." autocomplete="off" required>
    <button id="send-button" type="submit">Send</button>
  </form>
  <script>
    const history = [];
    const messagesEl = document.getElementById("messages");
    const statusEl = document.getElementById("status");
    const input = document.getElementById("message-input");
    const button = document.getElementById("send-button");

    function showMessage(role, text) {
      const row = document.createElement("p");
      row.className = "message";
      const label = document.createElement("strong");
      label.textContent = role + ": ";
      row.append(label, document.createTextNode(text));
      messagesEl.appendChild(row);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    document.getElementById("chat-form").addEventListener("submit", async event => {
      event.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      input.value = "";
      showMessage("You", text);
      history.push({role: "user", content: text});
      statusEl.textContent = "Thinking...";
      button.disabled = true;

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({messages: history.slice(-20)})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "The request failed.");

        history.push({role: "assistant", content: data.reply});
        showMessage("Assistant", data.reply);
        statusEl.textContent = "";
      } catch (error) {
        statusEl.textContent = error.message;
      } finally {
        button.disabled = false;
        input.focus();
      }
    });
  </script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages")

    if not isinstance(messages, list) or not messages:
        return jsonify(error="Send a non-empty messages list."), 400

    clean_messages = []

    for item in messages[-20:]:
        if not isinstance(item, dict):
            return jsonify(error="Each message must be an object."), 400

        role = item.get("role")
        content = item.get("content")

        if role not in ("user", "assistant"):
            return jsonify(error="Messages must use the user or assistant role."), 400

        if not isinstance(content, str):
            return jsonify(error="Message content must be text."), 400

        content = content.strip()
        if not content or len(content) > 4000:
            return jsonify(error="Messages must contain 1–4000 characters."), 400

        clean_messages.append({"role": role, "content": content})

    if clean_messages[-1]["role"] != "user":
        return jsonify(error="The latest message must be from the user."), 400

    try:
        result = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful and clear assistant. "
                        "Answer user questions directly. If you do not know "
                        "something, say so clearly rather than inventing an answer."
                    ),
                },
                *clean_messages,
            ],
            max_tokens=500,
        )

        if not result.choices:
            return jsonify(reply="I couldn't generate a response. Please try again.")

        reply = result.choices[0].message.content
        if not reply or not reply.strip():
            reply = "I couldn't generate a response. Please try again."

        return jsonify(reply=reply.strip())

    except APIError:
        app.logger.exception("Ollama API request failed")
        return jsonify(
            error=(
                "Could not reach Ollama. Make sure Ollama is running "
                "and llama3.2:3b is installed."
            )
        ), 502

    except Exception:
        app.logger.exception("Unexpected chatbot error")
        return jsonify(error="The chatbot encountered an unexpected error."), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
