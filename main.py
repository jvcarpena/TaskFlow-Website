import os
from dotenv import load_dotenv
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from flask_wtf.csrf import CSRFProtect

# Load .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_KEY")
csrf = CSRFProtect(app)
Bootstrap5(app)

# For temporary profile of the user
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# Configure the flask_login using the LoginManager Class
# and it needs secret key to be set
# login_manager = LoginManager()
# login_manager.init_app(app)
#
#
# # Create a user_loader callback. This callback will reload the user object from the database.
# @login_manager.user_loader
# def load_user(user_id):
#     return db.session.get(User, user_id)


# This creates a Base that inherits from the Declarative Base
# Create an ORM to define the table for the database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLITE_DB_URI")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES FOR THE DATABASE
class Tasks(db.Model):
    __tablename__ = "user_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Create Foreign Key, "user_data.id".
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user_data.id"))

    # ADD A CHILD RELATIONSHIP WITH USER.
    task_author = relationship("User", back_populates="tasks")


class User(db.Model):
    __tablename__ = "user_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    password: Mapped[str] = mapped_column(String(150), nullable=False)

    # ADD PARENT RELATIONSHIP FOR TASKS.
    tasks = relationship("Tasks", back_populates="task_author")


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Get the name, email, and password from the form.
        # Strengthen the password using generate password hash.
        name = form.name.data
        email = form.email.data
        plain_password = form.password.data
        strong_password = generate_password_hash(password=plain_password,
                                                 method='pbkdf2:sha256',
                                                 salt_length=8)

        # Add new user to the database.
        new_user = User(
            name=name,
            email=email,
            password=strong_password
        )
        db.session.add(new_user)
        db.session.commit()

        # login_user(new_user)
        return render_template("to-do-list.html")

    return render_template("register.html", form=form)


@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
