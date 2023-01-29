from flask import Flask, render_template
from flask import request
from flask import make_response

app = Flask(__name__)

@app.route('/')
def index():
    name = 'John'
    return render_template('index.html', name = name)

@app.route('/users/<username>')
def show_user(username):
    return f'User: {username}'

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

if __name__ == '__main__':
    app.run()
    
