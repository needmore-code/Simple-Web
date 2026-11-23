from flask import Flask, render_template_string
import webbrowser

app = Flask(__name__)

PROJECTS = [
    {
        "icon": "🛩️",
        "name": "3D Flight Simulator",
        "description": "Fly a physics-based aircraft through a 3D world. Built with Pygame, OpenGL, and NumPy.",
        "kind": "Desktop app",
        "command": "python 3d_Flight_Sim.py",
        "file": "3d_Flight_Sim.py",
    },
    {
        "icon": "🌐",
        "name": "PyChromium Browser",
        "description": "A multi-tab desktop browser with navigation controls and a Chromium engine.",
        "kind": "Desktop app",
        "command": "python py_chromium_browser.py",
        "file": "py_chromium_browser.py",
    },
    {
        "icon": "💬",
        "name": "Messaging App",
        "description": "Create an account, chat privately, or join group conversations with live updates.",
        "kind": "Web app",
        "command": "python app.py",
        "file": "app.py",
    },
    {
        "icon": "📍",
        "name": "GPS Tracker",
        "description": "View your live location on an interactive map, with location accuracy details.",
        "kind": "Web app",
        "command": "python gps.py",
        "file": "gps.py",
    },
    {
        "icon": "🤖",
        "name": "Ollama AI Chatbot",
        "description": "A private, local AI chatbot powered by Ollama and the OpenAI-compatible Python API.",
        "kind": "Web app",
        "command": "python ai_chatbot.py",
        "file": "ai_chatbot.py",
    },
    {
        "icon": "🎨",

        "name": "Simple Website",
        "description": "The project hub you're viewing now—a simple Flask website connecting the repository projects.",
        "kind": "Web app",
        "command": "python website.py",
        "file": "website.py",
    },
]

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple-Web | Project Hub</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            padding: 48px 20px;
            color: #17323a;
            background: linear-gradient(145deg, #b9f1e8, #e5fbf6 55%, #c9e8f4);
            font-family: Arial, Helvetica, sans-serif;
        }
        .page { width: min(1050px, 100%); margin: 0 auto; }
        .hero {
            padding: 38px 28px;
            border-radius: 22px;
            background: rgba(255, 255, 255, .88);
            box-shadow: 0 16px 45px rgba(24, 76, 82, .13);
            text-align: center;
        }
        .eyebrow {
            color: #147d78;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: .14em;
            text-transform: uppercase;
        }
        h1 { margin: 10px 0; font-size: clamp(32px, 6vw, 52px); }
        .intro { max-width: 650px; margin: 0 auto; color: #526a70; line-height: 1.6; }
        .projects {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(245px, 1fr));
            gap: 18px;
            margin: 24px 0;
        }
        .card {
            display: flex;
            min-height: 270px;
            flex-direction: column;
            padding: 22px;
            border: 1px solid rgba(31, 112, 115, .12);
            border-radius: 16px;
            background: rgba(255, 255, 255, .94);
            box-shadow: 0 8px 24px rgba(24, 76, 82, .08);
        }
        .icon { font-size: 30px; }
        .kind {
            align-self: flex-start;
            margin-top: 12px;
            padding: 5px 9px;
            border-radius: 999px;
            color: #176d69;
            background: #e0f5ef;
            font-size: 12px;
            font-weight: 700;
        }
        h2 { margin: 12px 0 8px; font-size: 20px; }
        .description { margin: 0 0 18px; color: #526a70; line-height: 1.5; }
        .command {
            overflow-wrap: anywhere;
            margin-top: auto;
            padding: 10px 11px;
            border-radius: 8px;
            color: #e8fffa;
            background: #173b42;
            font: 13px Consolas, Monaco, monospace;
        }
        .source {
            display: inline-block;
            margin-top: 12px;
            color: #087c78;
            font-weight: 700;
            text-decoration: none;
        }
        .source:hover { text-decoration: underline; }
        .note {
            padding: 16px 18px;
            border-left: 4px solid #168d85;
            border-radius: 8px;
            color: #405c61;
            background: rgba(255, 255, 255, .75);
            line-height: 1.55;
        }
        footer { padding: 18px 0 0; color: #526a70; text-align: center; font-size: 14px; }
        footer a { color: #087c78; font-weight: 700; text-decoration: none; }
        @media (max-width: 560px) {
            body { padding: 22px 14px; }
            .hero { padding: 30px 18px; }
        }
    </style>
</head>
<body>
    <main class="page">
        <header class="hero">
            <div class="eyebrow">Simple-Web · Project collection</div>
            <h1>One home for all our projects</h1>
            <p class="intro">Explore the apps and experiments in this repository. Each project has its own source code and can be run separately.</p>
        </header>

        <section class="projects" aria-label="Repository projects">
            {% for project in projects %}
            <article class="card">
                <div class="icon" aria-hidden="true">{{ project.icon }}</div>
                <span class="kind">{{ project.kind }}</span>
                <h2>{{ project.name }}</h2>
                <p class="description">{{ project.description }}</p>
                <code class="command">{{ project.command }}</code>
                <a class="source" href="https://github.com/needmore-code/Simple-Web/blob/main/{{ project.file }}" target="_blank" rel="noopener noreferrer">View source on GitHub →</a>
            </article>
            {% endfor %}
        </section>

        <aside class="note">
            <strong>Running projects:</strong> Install each project's dependencies first, then run its command from the repository folder. Desktop projects open as local applications. Web apps start separate servers, so stop one server before starting another if they use the same port.
        </aside>

        <footer>Browse the complete <a href="https://github.com/needmore-code/Simple-Web" target="_blank" rel="noopener noreferrer">Simple-Web repository</a> on GitHub.</footer>
    </main>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE, projects=PROJECTS)


if __name__ == "__main__":
    webbrowser.open("http://localhost:5000")
    app.run(debug=True)
