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
        <title>JavaScript Calculator</title>
        <style>
            * {
                box-sizing: border-box;
            }

            body {
                background: linear-gradient(135deg, #1d3557, #457b9d);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
            }

            .container {
                background: rgba(255, 255, 255, 0.12);
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
                backdrop-filter: blur(10px);
            }

            h1 {
                text-align: center;
                color: #f1faee;
                margin-bottom: 20px;
                font-size: 2rem;
            }

            .calculator {
                width: 320px;
                background: #0f172a;
                border-radius: 18px;
                padding: 18px;
                box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.08);
            }

            .display {
                width: 100%;
                min-height: 70px;
                background: #111827;
                color: #f8fafc;
                border: none;
                border-radius: 12px;
                text-align: right;
                font-size: 2rem;
                padding: 16px;
                margin-bottom: 16px;
                overflow: hidden;
                word-break: break-all;
            }

            .buttons {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 10px;
            }

            .btn {
                border: none;
                border-radius: 12px;
                padding: 18px 0;
                font-size: 1.2rem;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.1s ease, opacity 0.1s ease;
                color: #0f172a;
            }

            .btn:hover {
                opacity: 0.95;
            }

            .btn:active {
                transform: scale(0.98);
            }

            .operator {
                background: #fbbf24;
            }

            .action {
                background: #94a3b8;
            }

            .number {
                background: #e2e8f0;
            }

            .equals {
                background: #34d399;
                grid-column: span 2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Calculator</h1>
            <div class="calculator">
                <div id="display" class="display">0</div>
                <div class="buttons">
                    <button class="btn action" data-value="clear">AC</button>
                    <button class="btn action" data-value="delete">DEL</button>
                    <button class="btn operator" data-value="%">%</button>
                    <button class="btn operator" data-value="/">÷</button>

                    <button class="btn number" data-value="7">7</button>
                    <button class="btn number" data-value="8">8</button>
                    <button class="btn number" data-value="9">9</button>
                    <button class="btn operator" data-value="*">×</button>

                    <button class="btn number" data-value="4">4</button>
                    <button class="btn number" data-value="5">5</button>
                    <button class="btn number" data-value="6">6</button>
                    <button class="btn operator" data-value="-">−</button>

                    <button class="btn number" data-value="1">1</button>
                    <button class="btn number" data-value="2">2</button>
                    <button class="btn number" data-value="3">3</button>
                    <button class="btn operator" data-value="+">+</button>

                    <button class="btn number" data-value="0" style="grid-column: span 2;">0</button>
                    <button class="btn number" data-value=".">.</button>
                    <button class="btn equals" data-value="=">=</button>
                </div>
            </div>
        </div>

        <script>
            const display = document.getElementById('display');
            let expression = '';

            function updateDisplay() {
                display.textContent = expression || '0';
            }

            function evaluateExpression() {
                try {
                    if (!expression) {
                        return;
                    }

                    if (!/^[0-9+\-*/%.\s()]+$/.test(expression)) {
                        throw new Error('Invalid expression');
                    }

                    const result = Function(`"use strict"; return (${expression})`)();

                    if (!Number.isFinite(result)) {
                        throw new Error('Division by zero');
                    }

                    expression = String(result);
                } catch (error) {
                    expression = 'Error';
                }

                updateDisplay();
            }

            document.querySelectorAll('.btn').forEach(button => {
                button.addEventListener('click', () => {
                    const value = button.dataset.value;

                    if (value === 'clear') {
                        expression = '';
                        updateDisplay();
                        return;
                    }

                    if (value === 'delete') {
                        expression = expression.slice(0, -1);
                        updateDisplay();
                        return;
                    }

                    if (value === '=') {
                        evaluateExpression();
                        return;
                    }

                    if (expression === 'Error') {
                        expression = '';
                    }

                    expression += value;
                    updateDisplay();
                });
            });
        </script>
    </body>
    </html>
    """
    return Markup(html_content)

if __name__ == '__main__':
    webbrowser.open('http://localhost:5000')
    app.run(debug=True)
