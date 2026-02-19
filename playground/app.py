"""
Simple web playground for MeriLang using Flask.
Allows users to write and execute MeriLang code in the browser.
"""

from flask import Flask, render_template, request, jsonify
import subprocess
import tempfile
import os
import sys
from pathlib import Path

app = Flask(__name__)

# Maximum execution time (seconds)
MAX_EXECUTION_TIME = 5

# Maximum output size (characters)
MAX_OUTPUT_SIZE = 10000


@app.route('/')
def index():
    """Serve the playground homepage."""
    return render_template('index.html')


@app.route('/api/execute', methods=['POST'])
def execute_code():
    """Execute MeriLang code and return the result."""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({
                'success': False,
                'error': 'No code provided'
            })
        
        # Create temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.MeriLang', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute the code in a subprocess with timeout
            # Use sys.executable to ensure we use the same Python interpreter
            result = subprocess.run(
                [sys.executable, '-m', 'MeriLang', 'run', temp_file],
                capture_output=True,
                text=True,
                timeout=MAX_EXECUTION_TIME,
                encoding='utf-8'
            )
            
            output = result.stdout
            error = result.stderr
            
            # Limit output size
            if len(output) > MAX_OUTPUT_SIZE:
                output = output[:MAX_OUTPUT_SIZE] + '\n... (output truncated)'
            
            if len(error) > MAX_OUTPUT_SIZE:
                error = error[:MAX_OUTPUT_SIZE] + '\n... (error truncated)'
            
            return jsonify({
                'success': result.returncode == 0,
                'output': output,
                'error': error,
                'exitCode': result.returncode
            })
        
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'error': f'Execution timeout ({MAX_EXECUTION_TIME}s limit exceeded)'
            })
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        })


@app.route('/api/examples')
def get_examples():
    """Return list of example programs."""
    examples = [
        {
            'name': 'Hello World',
            'code': '''shuru
dikhao "Hello, World!"
dikhao "Welcome to MeriLang!"
khatam'''
        },
        {
            'name': 'Variables',
            'code': '''shuru
x = 10
y = 20
sum = x + y
dikhao "Sum: " + str(sum)
khatam'''
        },
        {
            'name': 'FizzBuzz',
            'code': '''shuru
chalao i se 1 tak 21 {
    agar i % 15 == 0 {
        dikhao "FizzBuzz"
    } warna {
        agar i % 3 == 0 {
            dikhao "Fizz"
        } warna {
            agar i % 5 == 0 {
                dikhao "Buzz"
            } warna {
                dikhao i
            } bas
        } bas
    } bas
}
khatam'''
        },
        {
            'name': 'Factorial',
            'code': '''shuru
vidhi factorial(n) {
    agar n <= 1 {
        vapas 1
    } bas
    vapas n * factorial(n - 1)
} samapt

dikhao factorial(5)
dikhao factorial(10)
khatam'''
        },
        {
            'name': 'List Operations',
            'code': '''shuru
numbers = [5, 2, 8, 1, 9]
dikhao "Original: " + str(numbers)

sorted_nums = sort(numbers)
dikhao "Sorted: " + str(sorted_nums)

dikhao "Sum: " + str(sum(numbers))
dikhao "Max: " + str(max(numbers))
dikhao "Min: " + str(min(numbers))
khatam'''
        }
    ]
    
    return jsonify(examples)


if __name__ == '__main__':
    print("Starting MeriLang Playground...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
