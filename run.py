from app import create_app # Se importa de __init__.py donde se define la función create_app
from app.models import db

app = create_app()

if __name__ == '__main__':  # Solo se ejecuta si corres este archivo directamente
# Esto significa: Si ejecutas python run.py, se ejecuta el código dentro del if.
    with app.app_context():  # Crea un contexto de aplicación
        # Crear tablas si no existen
        db.create_all()
        print("Base de datos inicializada")
    
    print("Servidor iniciando en http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000) # Inicia el servidor web