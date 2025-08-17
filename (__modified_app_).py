# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # If you are using a database
from flask_login import LoginManager, current_user, login_required

from .auth import auth as auth_blueprint  # Import your auth blueprint

db = SQLAlchemy()  # If you are using a database

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Needed for session management
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' # Example: SQLite database URI
    
    db.init_app(app)  # Initialize your database connection if you are using one

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Specify the login route from your auth blueprint
    login_manager.init_app(app)

    # Register your auth blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')


    # User loader callback for Flask-Login
    from .models import User  # Assuming you have a User model in models.py
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Fetch user by ID


    # Protect all routes by default, except signup, login, and static files
    @app.before_request
    def check_authentication():
        if not current_user.is_authenticated and request.endpoint not in ['auth.login', 'auth.signup', 'static']:
            return redirect(url_for('auth.login'))  # Redirect to login page if not authenticated


    # Define other non-auth routes
    @app.route('/')
    def index():
        return 'Welcome to the home page!'

    @app.route('/protected_resource')
    @login_required  # This decorator will ensure the user is logged in
    def protected_resource():
        return f'Hello, {current_user.name}! You have access to this protected resource.'  # Access current user data


    return app

