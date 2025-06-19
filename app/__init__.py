# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    from app.models import db
    db.init_app(app)
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    Migrate(app, db)

    
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app