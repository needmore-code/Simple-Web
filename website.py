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
            .link-btn {
                display: inline-block;
                margin-top: 20px;
                background: #0d4d6d;
                color: white;
                text-decoration: none;
                padding: 12px 22px;
                border-radius: 8px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to My Website</h1>
            <img src="https://via.placeholder.com/300x200?text=Sample+Image" alt="Sample Image">
            <p>This is a simple website with a turquoise background and an imported image.</p>
            <a class="link-btn" href="/calculator">Open Calculator</a>
        </div>
    </body>
    </html>
    """
    return Markup(html_content)

@app.route('/calculator')
def calculator_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Windows Calculator</title>
        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #dfe9f3, #c9d9ee);
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            }

            .calc-shell {
                width: 360px;
                background: #d7d7d7;
                border: 2px solid #9b9b9b;
                border-top-color: #f4f4f4;
                border-left-color: #f4f4f4;
                padding: 10px;
                box-shadow: 8px 8px 20px rgba(0, 0, 0, 0.25);
            }

            .title-bar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: linear-gradient(#ffffff, #e6e6e6);
                border: 1px solid #b2b2b2;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 10px;
            }

            .window-buttons {
                display: flex;
                gap: 6px;
            }

            .dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                border: 1px solid rgba(0,0,0,0.4);
            }

            .dot.red { background: #ff6b5b; }
            .dot.yellow { background: #f3c653; }
            .dot.green { background: #4ecb5e; }

            .calc-body {
                background: #d9d9d9;
                border: 2px solid #7e7e7e;
                border-top-color: #f3f3f3;
                border-left-color: #f3f3f3;
                padding: 12px;
            }

            .display-wrap {
                background: #dfe7d8;
                border: 2px solid #7e7e7e;
                border-top-color: #f9f9f9;
                border-left-color: #f9f9f9;
                margin-bottom: 12px;
                padding: 10px;
            }

            .display {
                min-height: 52px;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                font-size: clamp(28px, 5vw, 42px);
                font-weight: 500;
                color: #111;
                letter-spacing: 1px;
                overflow: hidden;
                word-break: break-all;
            }

            .buttons {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 8px;
            }

            button {
                height: 52px;
                border: 2px solid #8b8b8b;
                border-top-color: #f2f2f2;
                border-left-color: #f2f2f2;
                background: linear-gradient(#f9f9f9, #dfdfdf);
                font-size: 22px;
                font-weight: 600;
                cursor: pointer;
                color: #111;
            }

            button:active {
                border-top-color: #7a7a7a;
                border-left-color: #7a7a7a;
                border-right-color: #f3f3f3;
                border-bottom-color: #f3f3f3;
            }

            .operator {
                background: linear-gradient(#f7e6d0, #e9c88e);
            }

            .equals {
                background: linear-gradient(#dce9f7, #9cb9d6);
            }

            .wide {
                grid-column: span 2;
            }
        </style>
    </head>
    <body>
        <div class="calc-shell">
            <div class="title-bar">
                <span>Calculator</span>
                <div class="window-buttons">
                    <span class="dot red"></span>
                    <span class="dot yellow"></span>
                    <span class="dot green"></span>
                </div>
            </div>

            <div class="calc-body">
                <div class="display-wrap">
                    <div id="display" class="display">0</div>
                </div>

                <div class="buttons">
                    <button class="operator" data-action="clear">C</button>
                    <button class="operator" data-action="toggle-sign">±</button>
                    <button class="operator" data-action="percent">%</button>
                    <button class="operator" data-action="divide">÷</button>

                    <button data-value="7">7</button>
                    <button data-value="8">8</button>
                    <button data-value="9">9</button>
                    <button class="operator" data-action="multiply">×</button>

                    <button data-value="4">4</button>
                    <button data-value="5">5</button>
                    <button data-value="6">6</button>
                    <button class="operator" data-action="subtract">−</button>

                    <button data-value="1">1</button>
                    <button data-value="2">2</button>
                    <button data-value="3">3</button>
                    <button class="operator" data-action="add">+</button>

                    <button class="wide" data-value="0">0</button>
                    <button data-value=".">.</button>
                    <button class="equals" data-action="equals">=</button>
                </div>
            </div>
        </div>

        <script>
            const display = document.getElementById('display');

            let currentValue = '0';
            let storedValue = null;
            let operator = null;
            let waitingForSecondOperand = false;

            function formatNumber(value) {
                if (!Number.isFinite(value)) {
                    return 'Error';
                }

                const absValue = Math.abs(value);
                if (absValue >= 1e12 || (absValue > 0 && absValue < 1e-10)) {
                    return Number(value).toExponential(8).replace(/\.0+e/, 'e');
                }

                const rounded = Number(value.toFixed(10));
                return String(rounded);
            }

            function updateDisplay() {
                display.textContent = currentValue;
            }

            function resetCalculator() {
                currentValue = '0';
                storedValue = null;
                operator = null;
                waitingForSecondOperand = false;
                updateDisplay();
            }

            function inputDigit(digit) {
                if (waitingForSecondOperand) {
                    currentValue = digit;
                    waitingForSecondOperand = false;
                } else {
                    currentValue = currentValue === '0' ? digit : currentValue + digit;
                }
                updateDisplay();
            }

            function inputDecimal() {
                if (waitingForSecondOperand) {
                    currentValue = '0.';
                    waitingForSecondOperand = false;
                } else if (!currentValue.includes('.')) {
                    currentValue += '.';
                }
                updateDisplay();
            }

            function performCalculation() {
                const input = Number(currentValue);
                const previous = Number(storedValue);

                if (operator === '+') {
                    return previous + input;
                }
                if (operator === '−') {
                    return previous - input;
                }
                if (operator === '×') {
                    return previous * input;
                }
                if (operator === '÷') {
                    if (input === 0) return 'Error';
                    return previous / input;
                }

                return input;
            }

            function handleOperator(nextOperator) {
                const inputValue = Number(currentValue);

                if (storedValue === null) {
                    storedValue = inputValue;
                } else if (operator && !waitingForSecondOperand) {
                    const result = performCalculation();
                    currentValue = formatNumber(result);
                    storedValue = result;
                }

                waitingForSecondOperand = true;
                operator = nextOperator;
                updateDisplay();
            }

            function handleEquals() {
                if (!operator || waitingForSecondOperand) {
                    return;
                }

                const result = performCalculation();
                currentValue = formatNumber(result);
                storedValue = result;
                operator = null;
                waitingForSecondOperand = true;
                updateDisplay();
            }

            function handlePercent() {
                const value = Number(currentValue) / 100;
                currentValue = formatNumber(value);
                updateDisplay();
            }

            function handleToggleSign() {
                const value = Number(currentValue);
                currentValue = formatNumber(-value);
                updateDisplay();
            }

            document.querySelectorAll('button').forEach((button) => {
                button.addEventListener('click', () => {
                    const value = button.dataset.value;
                    const action = button.dataset.action;

                    if (value !== undefined) {
                        if (value === '.') {
                            inputDecimal();
                        } else {
                            inputDigit(value);
                        }
                        return;
                    }

                    switch (action) {
                        case 'clear':
                            resetCalculator();
                            break;
                        case 'toggle-sign':
                            handleToggleSign();
                            break;
                        case 'percent':
                            handlePercent();
                            break;
                        case 'add':
                            handleOperator('+');
                            break;
                        case 'subtract':
                            handleOperator('−');
                            break;
                        case 'multiply':
                            handleOperator('×');
                            break;
                        case 'divide':
                            handleOperator('÷');
                            break;
                        case 'equals':
                            handleEquals();
                            break;
                        default:
                            break;
                    }
                });
            });

            document.addEventListener('keydown', (event) => {
                const key = event.key;

                if (/^[0-9]$/.test(key)) {
                    event.preventDefault();
                    inputDigit(key);
                    return;
                }

                if (key === '.') {
                    event.preventDefault();
                    inputDecimal();
                    return;
                }

                if (key === '+') {
                    event.preventDefault();
                    handleOperator('+');
                    return;
                }

                if (key === '-') {
                    event.preventDefault();
                    handleOperator('−');
                    return;
                }

                if (key === '*') {
                    event.preventDefault();
                    handleOperator('×');
                    return;
                }

                if (key === '/') {
                    event.preventDefault();
                    handleOperator('÷');
                    return;
                }

                if (key === 'Enter' || key === '=') {
                    event.preventDefault();
                    handleEquals();
                    return;
                }

                if (key === 'Backspace') {
                    event.preventDefault();
                    currentValue = currentValue.length <= 1 || (currentValue.length === 2 && currentValue.startsWith('-'))
                        ? '0'
                        : currentValue.slice(0, -1);
                    updateDisplay();
                    return;
                }

                if (key === 'Escape') {
                    event.preventDefault();
                    resetCalculator();
                }
            });
        </script>
    </body>
    </html>
    """
    return Markup(html_content)

if __name__ == '__main__':
    webbrowser.open('http://localhost:5000')
    app.run(debug=True)
