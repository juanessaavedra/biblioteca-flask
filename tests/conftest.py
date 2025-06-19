# conftest.py - Simple para tests unitarios
import pytest
from app import create_app
from app.models import db, Usuario, Libro, Prestamo

@pytest.fixture(scope='session')
def app():
    """Aplicación Flask para tests"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    
    with app.app_context():
        db.create_all()
        yield app

@pytest.fixture
def client(app):
    """Cliente HTTP para tests"""
    return app.test_client()

@pytest.fixture
def sample_usuario(app):
    """Usuario de ejemplo"""
    with app.app_context():
        usuario = Usuario(nombre='Test User', email='test@test.com')
        db.session.add(usuario)
        db.session.commit()
        return usuario

@pytest.fixture
def sample_libro(app):
    """Libro de ejemplo"""
    with app.app_context():
        libro = Libro(titulo='Test Book', autor='Test Author', isbn='1234567890123')
        db.session.add(libro)
        db.session.commit()
        return libro