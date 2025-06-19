# tests/conftest.py

"""Un fixture es una funcion especial que prepara datos antes de que se ejecuten los tests. Opcionalmente limpia despues. Es como un asistente que configura todo lo que el test necesita"""


import pytest
import uuid
from app import create_app
from app.models import db, Usuario, Libro, Prestamo
from config import TestConfig # Importa para tener la configuracion de pruebas

@pytest.fixture(scope='session') # Se ejecuta una vez por toda la sesión de pruebas
def app():
    app = create_app(TestConfig) # Crea la aplicación Flask con la configuración de pruebas
    
    with app.app_context():
        db.create_all()
        yield app # Pausa aca, entrega la app a los tests y espera a que terminen todos
        db.drop_all() # Al final elimina todas las tablas de la base de datos

@pytest.fixture # Sin cope, se ejecuta para cada test individual
def client(app): # Recibe la app creada por el fixture app
    return app.test_client() #Crea un cliente HTTP falso para hacer peticiones a la aplicación durante las pruebas

@pytest.fixture(autouse=True) # Se ejecuta antes y después de cada test automaticamente
def clean_db(app):
    with app.app_context():
        db.session.query(Prestamo).delete()
        db.session.query(Libro).delete()
        db.session.query(Usuario).delete()
        db.session.commit()
        yield #  pausa, deja que el test se ejecute con BD limpia
        db.session.rollback()  #deshace cambios no confirmados (red de seguridad)

@pytest.fixture
def sample_usuario(app):
    with app.app_context():
        email = f'test_{uuid.uuid4().hex[:8]}@test.com'
        usuario = Usuario(nombre='Test User', email=email)
        db.session.add(usuario)
        db.session.commit()
        db.session.refresh(usuario)
        return usuario

@pytest.fixture
def sample_libro(app):
    with app.app_context():
        isbn = f'123456789{uuid.uuid4().hex[:4]}'
        libro = Libro(titulo='Test Book', autor='Test Author', isbn=isbn)
        db.session.add(libro)
        db.session.commit()
        db.session.refresh(libro)
        return libro