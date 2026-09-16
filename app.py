from flask import Flask, render_template_string, jsonify, request
import os

app = Flask(__name__)

# STATIC & TEMPLATE DOSYALARINI OKUMA
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/')
def index():
    return read_file('index.html')

@app.route('/style.css')
def style():
    return app.response_class(read_file('style.css'), mimetype='text/css')

@app.route('/app.js')
def js():
    return app.response_class(read_file('app.js'), mimetype='application/javascript')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
