from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class NewPostForm(FlaskForm):
    body = TextAreaField('Enter post', validators=[DataRequired(), Length(max=1024)])
    picture = FileField("Enter image", validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField('Sign in')

class ChangeDisplayNameForm(FlaskForm):
    display_name = StringField('New display name', validators=[DataRequired(), Length(min=3, max=16)])
    submit = SubmitField('Update')

class ChangeDisplayNameForm(FlaskForm):
    display_name = StringField('New display name', validators=[DataRequired(), Length(min=3, max=16)])
    submit = SubmitField('Update')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    submit = SubmitField('Update')