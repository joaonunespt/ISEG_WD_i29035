from flask import Flask, render_template
from flask import request
from flask import make_response

from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)

crsf = CSRFProtect(app)
app.config["SECRET_KEY"] = "chave_secreta"

class NameForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

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

@app.route('/form', methods=['GET','POST'])
def form():
    form = NameForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        return "Hello " + name
    return render_template('form.html', form=form)

if __name__ == '__main__':
    app.run()
    
