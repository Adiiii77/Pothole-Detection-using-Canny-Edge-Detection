from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

import os


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Set upload and static folders
    UPLOAD_FOLDER = os.path.join('website', 'static', 'uploads')
    STATIC_FOLDER = os.path.join('website', 'static')

    # Ensure folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(STATIC_FOLDER, exist_ok=True)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['STATIC_FOLDER'] = STATIC_FOLDER

    from .models import User

    create_db(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')

    return app


def create_db(app):
    if not os.path.exists("website/" + DB_NAME):
        with app.app_context():  # Use app context to bind the app to SQLAlchemy
            db.create_all()
            print("Database Created")

