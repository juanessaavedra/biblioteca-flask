# tests/integration/test_api_endpoints.py
import json
import pytest
from app.models import db, Usuario, Libro, Prestamo

# ============= 3 PRUEBAS DE ENDPOINTS DE LA API =============

def test_endpoint_health_check(client):
    """Test 1: Endpoint de salud funciona correctamente"""
    response = client.get('/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'OK'

def test_endpoint_libros_disponibles(client, sample_libro):
    """Test 2: Endpoint de libros disponibles"""
    response = client.get('/libros/disponibles')
    
    assert response.status_code == 200
    libros = json.loads(response.data)
    assert len(libros) >= 1
    assert all(libro['disponible'] == True for libro in libros)

def test_endpoint_prestamos_crud(client, sample_usuario, sample_libro):
    """Test 3: Endpoints CRUD de préstamos"""
    # GET préstamos (vacío)
    response = client.get('/prestamos')
    assert response.status_code == 200
    
    # POST crear préstamo
    data = {"usuario_id": sample_usuario.id, "libro_id": sample_libro.id}
    response = client.post('/prestamos', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    prestamo_data = json.loads(response.data)
    
    # GET préstamos (con datos)
    response = client.get('/prestamos')
    assert response.status_code == 200
    prestamos = json.loads(response.data)
    assert len(prestamos) == 1

# ============= 2 PRUEBAS DE INTEGRACIÓN CON BASE DE DATOS =============

def test_integracion_prestamo_actualiza_disponibilidad(client, sample_usuario, sample_libro):
    """Test 4: Préstamo actualiza disponibilidad en BD"""
    # Verificar libro disponible inicialmente
    assert sample_libro.disponible == True
    
    # Crear préstamo
    data = {"usuario_id": sample_usuario.id, "libro_id": sample_libro.id}
    response = client.post('/prestamos', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    
    # Verificar en BD que libro ya no está disponible
    with client.application.app_context():
        libro_actualizado = db.session.get(Libro, sample_libro.id)
        assert libro_actualizado.disponible == False

def test_integracion_devolucion_restaura_disponibilidad(client, sample_usuario, sample_libro):
    """Test 5: Devolución restaura disponibilidad en BD"""
    # Crear préstamo
    with client.application.app_context():
        prestamo = Prestamo(usuario_id=sample_usuario.id, libro_id=sample_libro.id)
        db.session.add(prestamo)
        sample_libro.disponible = False
        db.session.commit()
        prestamo_id = prestamo.id
    
    # Devolver libro
    response = client.put(f'/prestamos/{prestamo_id}/devolver')
    assert response.status_code == 200
    
    # Verificar en BD que libro está disponible
    with client.application.app_context():
        libro_actualizado = db.session.get(Libro, sample_libro.id)
        assert libro_actualizado.disponible == True

# ============= 1 PRUEBA END-TO-END DEL FLUJO COMPLETO =============

def test_flujo_completo_prestamo_devolucion(client):
    """Test 6: Flujo completo end-to-end de préstamo y devolución"""
    
    # Crear usuario
    usuario_data = {"nombre": "Usuario E2E", "email": "e2e@test.com"}
    response = client.post('/usuarios', data=json.dumps(usuario_data), content_type='application/json')
    assert response.status_code == 201
    usuario = json.loads(response.data)
    
    # Crear libro
    libro_data = {"titulo": "Libro E2E", "autor": "Autor E2E", "isbn": "1234567890123"}
    response = client.post('/libros', data=json.dumps(libro_data), content_type='application/json')
    assert response.status_code == 201
    libro = json.loads(response.data)
    
    # Crear préstamo
    prestamo_data = {"usuario_id": usuario['id'], "libro_id": libro['id']}
    response = client.post('/prestamos', data=json.dumps(prestamo_data), content_type='application/json')
    assert response.status_code == 201
    prestamo = json.loads(response.data)
    
    # Verificar libro no disponible
    response = client.get('/libros/disponibles')
    libros_disponibles = json.loads(response.data)
    libro_ids = [l['id'] for l in libros_disponibles]
    assert libro['id'] not in libro_ids
    
    # Devolver libro
    response = client.put(f'/prestamos/{prestamo["id"]}/devolver')
    assert response.status_code == 200
    
    # Verificar libro disponible nuevamente
    response = client.get('/libros/disponibles')
    libros_disponibles = json.loads(response.data)
    libro_ids = [l['id'] for l in libros_disponibles]
    assert libro['id'] in libro_ids