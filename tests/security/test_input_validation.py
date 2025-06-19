# tests/security/test_input_validation.py
import pytest
import json
from app import create_app
from app.models import db
from config import TestConfig

@pytest.fixture(scope="module")
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# ============= PRUEBAS DE VALIDACIÓN DE ENTRADA =============

def test_campos_requeridos_usuario(client):
    """Test 1: Validación de campos requeridos en usuarios"""
    # Campo nombre vacío
    data = {"nombre": "", "email": "test@test.com"}
    response = client.post('/usuarios', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    
    # Campo email vacío
    data = {"nombre": "Test User", "email": ""}
    response = client.post('/usuarios', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    
    # Ambos campos vacíos
    data = {"nombre": "", "email": ""}
    response = client.post('/usuarios', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400

def test_campos_requeridos_libro(client):
    """Test 2: Validación de campos requeridos en libros"""
    # Sin título
    data = {"autor": "Autor Test", "isbn": "1234567890123"}
    response = client.post('/libros', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    
    # Sin autor
    data = {"titulo": "Libro Test", "isbn": "1234567890123"}
    response = client.post('/libros', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    
    # Sin ISBN
    data = {"titulo": "Libro Test", "autor": "Autor Test"}
    response = client.post('/libros', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400

def test_validacion_email_formato(client):
    """Test 3: Validación de formato de email"""
    invalid_emails = [
        "email_sin_arroba",
        "email@",
        "@domain.com",
        "email@domain",
        "email.domain.com",
        "email@domain.",
        ""
    ]
    
    for invalid_email in invalid_emails:
        data = {"nombre": "Test User", "email": invalid_email}
        response = client.post('/usuarios', data=json.dumps(data), content_type='application/json')
        # Debe rechazar emails inválidos
        assert response.status_code in [400, 422], f"Email inválido aceptado: {invalid_email}"

def test_validacion_duplicados(client):
    """Test 4: Validación de duplicados"""
    # Crear usuario
    data = {"nombre": "Usuario Test", "email": "duplicado@test.com"}
    response1 = client.post('/usuarios', data=json.dumps(data), content_type='application/json')
    assert response1.status_code == 201
    
    # Intentar crear usuario con mismo email
    response2 = client.post('/usuarios', data=json.dumps(data), content_type='application/json')
    assert response2.status_code == 400
    
    # Crear libro
    data = {"titulo": "Libro Test", "autor": "Autor Test", "isbn": "1234567890123"}
    response1 = client.post('/libros', data=json.dumps(data), content_type='application/json')
    assert response1.status_code == 201
    
    # Intentar crear libro con mismo ISBN
    response2 = client.post('/libros', data=json.dumps(data), content_type='application/json')
    assert response2.status_code == 400

def test_validacion_tipos_datos(client):
    """Test 5: Validación de tipos de datos"""
    # IDs deben ser números en préstamos
    invalid_data = [
        {"usuario_id": "texto", "libro_id": 1},
        {"usuario_id": 1, "libro_id": "texto"},
        {"usuario_id": "abc", "libro_id": "def"},
        {"usuario_id": None, "libro_id": 1},
        {"usuario_id": 1, "libro_id": None}
    ]
    
    for data in invalid_data:
        response = client.post('/prestamos', data=json.dumps(data), content_type='application/json')
        # Debe rechazar tipos de datos incorrectos
        assert response.status_code in [400, 422, 404]

def test_validacion_longitud_campos(client):
    """Test 6: Validación de longitud de campos"""
    # Nombre muy largo (más de 100 caracteres)
    nombre_largo = "a" * 150
    data = {"nombre": nombre_largo, "email": "test@test.com"}
    response = client.post('/usuarios', data=json.dumps(data), content_type='application/json')
    # Podría ser aceptado pero truncado, o rechazado
    assert response.status_code in [201, 400]
    
    # Email muy largo (más de 120 caracteres)
    email_largo = "a" * 100 + "@test.com"
    data = {"nombre": "Test User", "email": email_largo}
    response = client.post('/usuarios', data=json.dumps(data), content_type='application/json')
    assert response.status_code in [201, 400]

def test_validacion_caracteres_especiales(client):
    """Test 7: Manejo de caracteres especiales"""
    caracteres_especiales = [
        "Nombre con 'comillas'",
        'Nombre con "comillas dobles"',
        "Nombre con ñ y acentós",
        "Nombre con símbolos @#$%",
        "Nombre\ncon\nsaltos\nde\nlínea",
        "Nombre\tcon\ttabs"
    ]
    
    for nombre in caracteres_especiales:
        data = {"nombre": nombre, "email": f"test{hash(nombre) % 10000}@test.com"}
        response = client.post('/usuarios', data=json.dumps(data), content_type='application/json')
        # Debe manejar caracteres especiales sin fallar
        assert response.status_code in [201, 400]

def test_json_malformado(client):
    """Test 8: Validación de JSON malformado"""
    # JSON inválido
    invalid_json = '{"nombre": "Test", "email": "test@test.com"'  # Falta }
    response = client.post('/usuarios', data=invalid_json, content_type='application/json')
    assert response.status_code == 400
    
    # Contenido no-JSON
    response = client.post('/usuarios', data="esto no es json", content_type='application/json')
    assert response.status_code == 400
    
    # JSON vacío
    response = client.post('/usuarios', data="{}", content_type='application/json')
    assert response.status_code == 400