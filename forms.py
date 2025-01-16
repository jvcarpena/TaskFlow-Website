from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class TaskForm(FlaskForm):
    task = StringField("", validators=[DataRequired()])
    submit = SubmitField("Add Task")


class EditForm(FlaskForm):
    title_to_edit = StringField("", validators=[DataRequired()])
    submit = SubmitField("Save Changes")
