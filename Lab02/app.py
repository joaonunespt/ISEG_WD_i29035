from flask import Flask, render_template, make_response
from flask import request

app = Flask(__name__)

# @app.route('/')
# def index():
#     response = make_response('Hello World!')
#     response.headers['Content-Type'] = 'text/plain'
#     return response

@app.route('/')
def index():
    name = 'John'
    return render_template('index.html', name=name)

@app.route('/users/<username>')
def show_user(username):
    return f'User: {username}'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
            
        if username == 'test' and password == 'test':
            return 'Login successful'
        else:
            return 'Invalid username or password'
    else:
        return render_template('login.html')

if __name__ == '__main__':
    app.run(debug = True)
    
