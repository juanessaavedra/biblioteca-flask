"""Factory pattern para crear la aplicación Flask."""

from flask import Flask
from flask_cors import CORS # Importa CORS (Cross-Origin Resource Sharing) para permitir peticiones desde otros dominios
from flask_migrate import Migrate # Importa Migrate para manejar migraciones de base de datos
from flask_jwt_extended import JWTManager  # Importa JWTManager para manejar autenticación JWT
from config import Config  #Importa la clase de config.py

def create_app(): #Funcion que construye y configura la aplicación Flask
    app = Flask(__name__) # Crea una instancia de la aplicación Flask usando el nombre del módulo actual


    app.config.from_object(Config)  #Carga todas las configuraciones desde la clase Config (SECRET_KEY, DATABASE_URL, etc.)
    
    """Importa la instancia de SQLAlchemy desde models.py
Inicializa la base de datos con la aplicación Flask"""

    from app.models import db
    db.init_app(app)
    
    # Configura CORS para permitir peticiones desde cualquier origen (*)
    #r"/*" significa "todas las rutas"
    # En producción deberías especificar dominios específicos


    CORS(app, resources={r"/*": {"origins": "*"}})  # Para permitir frontend
    Migrate(app, db)  # Inicializa Flask-Migrate para manejar migraciones de base de datos
    # Conecta la app con la instancia de SQLAlchemy



    JWTManager(app)  # Inicializa el manejador de JWT con la aplicación
# Usa la configuración JWT_SECRET_KEY del config
    
    #Importa el blueprint (conjunto de rutas) desde routes.py
    # Registra las rutas en la aplicación


    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app # Retorna la aplicación configurada y lista para usar

"""El blueprint es como una plantilla de rutas para reutilizar
- En este caso app:register_blueprint(mainp) toma todas las rutas del main_bp y las conecta a la aplicacion Flask.
"""