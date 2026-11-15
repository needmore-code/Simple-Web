from flask import Flask
from markupsafe import Markup
import webbrowser

app = Flask(__name__)

@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Simple Website</title>
        <style>
            body {
                background-color: turquoise;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
            }
            .container {
                text-align: center;
                background-color: rgba(255, 255, 255, 0.9);
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            img {
                max-width: 300px;
                height: auto;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            h1 {
                color: #333;
                margin-top: 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to My Website</h1>
            <img src="https://via.placeholder.com/300x200?text=Sample+Image" alt="Sample Image">
            <p>This is a simple website with a turquoise background and an imported image.</p>
        </div>
    </body>
    </html>
    """
    return Markup(html_content)

if __name__ == '__main__':
    webbrowser.open('http://localhost:5000')
    app.run(debug=True)
