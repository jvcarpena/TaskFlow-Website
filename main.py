import os
from dotenv import load_dotenv
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, TaskForm, EditForm
from flask_wtf.csrf import CSRFProtect

# Load .env file containing sensitive information such as the Flask secret key and database URI
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_KEY")  # Secret key for session management
csrf = CSRFProtect(app)  # Protect against CSRF attacks
Bootstrap5(app)  # Integrate Bootstrap for styling

# For temporary profile of the user, Gravatar is used to generate user avatars
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


def authenticated_user_only(function):
    """
    Decorator to restrict access to a route for authenticated users only.
    """
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:  # Check if the user is logged in
            return abort(403)  # Forbidden access for unauthenticated users
        return function(*args, **kwargs)
    return decorated_function


# Configure Flask-Login using the LoginManager Class for user session management
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """
    Reload the user object from the user ID stored in the session.
    """
    return db.session.get(User, user_id)


# This class creates a base for ORM models using SQLAlchemy's declarative base
class Base(DeclarativeBase):
    pass


# Configure the SQLite database URI from the environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLITE_DB_URI")
db = SQLAlchemy(model_class=Base)  # Initialize SQLAlchemy
db.init_app(app)


# Configure database tables

class Tasks(db.Model):
    """
    Define the Tasks table for user tasks, with fields for task details.
    Includes a relationship with the User table.
    """
    __tablename__ = "user_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # Primary key for task ID
    title: Mapped[str] = mapped_column(String(1000), nullable=False)  # Task title
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)  # Task completion status
    is_in_progress: Mapped[bool] = mapped_column(Boolean, default=False)  # Task progress status

    # Foreign Key linking to the User table
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user_data.id"))

    # Define relationship with the User table
    task_author = relationship("User", back_populates="tasks")


class User(UserMixin, db.Model):
    """
    Define the User table, which contains user details such as name, email, and password.
    Includes a relationship with the Tasks table for user tasks.
    """
    __tablename__ = "user_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # Primary key for user ID
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # User's name
    email: Mapped[str] = mapped_column(String(150), nullable=False)  # User's email
    password: Mapped[str] = mapped_column(String(150), nullable=False)  # Hashed user password

    # Define relationship with the Tasks table
    tasks = relationship("Tasks", back_populates="task_author")


# Initialize the database with tables
with app.app_context():
    db.create_all()


# Routes and view functions

@app.route('/')
def home():
    """
    Home page route.
    """
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    """
    Route for user registration. Handles form submission and account creation.
    If the user already exists, redirects to the login page.
    """
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        plain_password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        if user:  # Check if the user email already exists in the database
            flash("You've already registered with that email, login instead!")
            return redirect(url_for("login"))

        # Hash the password before storing it
        strong_password = generate_password_hash(password=plain_password,
                                                 method='pbkdf2:sha256',
                                                 salt_length=8)

        # Add new user to the database
        new_user = User(
            name=name,
            email=email,
            password=strong_password
        )
        db.session.add(new_user)
        db.session.commit()

        # Log in the user and redirect to task dashboard
        login_user(new_user)
        return redirect(url_for("get_all_tasks"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    Route for user login. Handles form submission and user authentication.
    """
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Get the user by email
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        if not user:  # Check if the user exists
            flash("That email does not exist.")
            return redirect(url_for("login"))
        if not check_password_hash(pwhash=user.password, password=password):  # Verify password
            flash("Incorrect password!")
            return redirect(url_for("login"))

        # Log in the user and redirect to task dashboard
        login_user(user)
        return redirect(url_for("get_all_tasks"))
    return render_template("login.html", form=form, current_user=current_user)


@app.route("/logout")
def logout():
    """
    Route for user logout. Ends the user's session and redirects to the home page.
    """
    logout_user()
    return redirect(url_for("home"))


@app.route("/dashboard", methods=["POST", "GET"])
@authenticated_user_only
def get_all_tasks():
    """
    Route for the user's task dashboard. Handles displaying tasks, adding new tasks and editing
    current task.
    """
    form = TaskForm()
    form_edit = None  # Initialize edit form (it will be populated when editing)

    # Handle adding new tasks
    if form.validate_on_submit():
        new_task = Tasks(title=form.task.data,
                         author_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("get_all_tasks"))

    # Handle task editing
    task_to_edit = None
    if request.args.get('task_id'):
        task_to_edit = db.get_or_404(Tasks, request.args['task_id'])
        form_edit = EditForm(title_to_edit=task_to_edit.title)  # Pre-populate form with task details

        if form_edit.validate_on_submit():
            task_to_edit.title = form_edit.title_to_edit.data
            db.session.commit()
            return redirect(url_for("get_all_tasks"))

    result = db.session.execute(db.select(Tasks).order_by(Tasks.is_in_progress.desc(), Tasks.is_completed.asc()))
    tasks = result.scalars().all()
    return render_template("to-do-list.html", current_user=current_user, all_task=tasks, form=form, form_edit=form_edit, task_to_edit=task_to_edit)


@app.route("/delete/<int:task_id>")
@authenticated_user_only
def delete_task(task_id):
    """
    Route for deleting a task from the database.
    """
    task_to_delete = db.get_or_404(Tasks, task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_tasks"))


@app.route("/mark-as-completed/<int:task_id>", methods=["POST", "GET"])
@authenticated_user_only
def mark_as_completed(task_id):
    """
    Route to mark a task as completed. Sets the task status to completed and stops progress.
    """
    task_to_mark = db.get_or_404(Tasks, task_id)
    if not task_to_mark.is_completed:
        task_to_mark.is_completed = True
        task_to_mark.is_in_progress = False
        db.session.commit()
    return redirect(url_for("get_all_tasks"))


@app.route("/mark-as-in-progress/<int:task_id>", methods=["POST", "GET"])
@authenticated_user_only
def mark_as_in_progress(task_id):
    """
    Route to mark a task as in progress. Sets the task status to in progress and stops completion.
    """
    task_to_mark = db.get_or_404(Tasks, task_id)
    if not task_to_mark.is_in_progress:
        task_to_mark.is_completed = False
        task_to_mark.is_in_progress = True
        db.session.commit()
    return redirect(url_for("get_all_tasks"))


# Run the app in debug mode
if __name__ == "__main__":
    app.run(debug=False)
