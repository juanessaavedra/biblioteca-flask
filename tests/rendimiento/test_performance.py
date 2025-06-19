"""
# Instalar pytest-benchmark
pip install pytest-benchmark

# O agregar a requirements.txt:
# pytest-benchmark==4.0.0
# """

# tests/performance/test_performance.py
import pytest
import json
from app import create_app
from app.models import db, Usuario, Libro, Prestamo
from config import TestConfig

@pytest.fixture(scope="module")
def app_with_db():
    """Fixture para crear una app Flask con base de datos en memoria para performance."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # Crear datos iniciales para las pruebas de performance
        # Usuario de prueba
        usuario_test = Usuario(nombre="Usuario Performance", email="performance@test.com")
        db.session.add(usuario_test)
        
        # Varios libros de prueba
        libros_test = [
            Libro(titulo="Libro 1", autor="Autor 1", isbn="1111111111111"),
            Libro(titulo="Libro 2", autor="Autor 2", isbn="2222222222222"),
            Libro(titulo="Libro 3", autor="Autor 3", isbn="3333333333333"),
            Libro(titulo="Libro 4", autor="Autor 4", isbn="4444444444444"),
            Libro(titulo="Libro 5", autor="Autor 5", isbn="5555555555555"),
        ]
        for libro in libros_test:
            db.session.add(libro)
        
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app_with_db):
    """Fixture para obtener un cliente de prueba."""
    return app_with_db.test_client()

# ============= PRUEBAS DE PERFORMANCE DE ENDPOINTS =============

def test_health_check_performance(benchmark, client):
    """Medir rendimiento del endpoint de salud."""
    result = benchmark(client.get, '/health')
    assert result.status_code == 200

def test_listar_usuarios_performance(benchmark, client):
    """Medir rendimiento de listado de usuarios."""
    result = benchmark(client.get, '/usuarios')
    assert result.status_code == 200
    # Verificar que devuelve datos
    data = json.loads(result.data)
    assert len(data) >= 1

def test_listar_libros_performance(benchmark, client):
    """Medir rendimiento de listado de libros."""
    result = benchmark(client.get, '/libros')
    assert result.status_code == 200
    data = json.loads(result.data)
    assert len(data) >= 5

def test_libros_disponibles_performance(benchmark, client):
    """Medir rendimiento del endpoint de libros disponibles."""
    result = benchmark(client.get, '/libros/disponibles')
    assert result.status_code == 200
    data = json.loads(result.data)
    assert len(data) >= 5

def test_listar_prestamos_performance(benchmark, client):
    """Medir rendimiento de listado de préstamos."""
    result = benchmark(client.get, '/prestamos')
    assert result.status_code == 200

# ============= PRUEBAS DE PERFORMANCE DE OPERACIONES CRUD =============

def test_crear_usuario_performance(benchmark, client):
    """Medir rendimiento de creación de usuario."""
    def crear_usuario():
        data = {
            "nombre": "Usuario Benchmark",
            "email": "benchmark@test.com"
        }
        return client.post('/usuarios', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    result = benchmark(crear_usuario)
    assert result.status_code == 201

def test_crear_libro_performance(benchmark, client):
    """Medir rendimiento de creación de libro."""
    def crear_libro():
        data = {
            "titulo": "Libro Benchmark",
            "autor": "Autor Benchmark",
            "isbn": "9999999999999"
        }
        return client.post('/libros',
                          data=json.dumps(data),
                          content_type='application/json')
    
    result = benchmark(crear_libro)
    assert result.status_code == 201

def test_crear_prestamo_performance(benchmark, client):
    """Medir rendimiento de creación de préstamo."""
    def crear_prestamo():
        data = {
            "usuario_id": 1,  # Usuario creado en el fixture
            "libro_id": 1     # Libro creado en el fixture
        }
        return client.post('/prestamos',
                          data=json.dumps(data),
                          content_type='application/json')
    
    result = benchmark(crear_prestamo)
    assert result.status_code == 201

def test_devolver_libro_performance(benchmark, client, app_with_db):
    """Medir rendimiento de devolución de libro."""
    # Crear un préstamo primero
    with app_with_db.app_context():
        prestamo = Prestamo(usuario_id=1, libro_id=2)
        db.session.add(prestamo)
        db.session.commit()
        prestamo_id = prestamo.id
        
        # Marcar libro como no disponible
        libro = db.session.get(Libro, 2)
        libro.disponible = False
        db.session.commit()
    
    def devolver_libro():
        return client.put(f'/prestamos/{prestamo_id}/devolver',
                         content_type='application/json')
    
    result = benchmark(devolver_libro)
    assert result.status_code == 200

# ============= PRUEBAS DE CARGA CON MÚLTIPLES OPERACIONES =============

def test_flujo_completo_performance(benchmark, client):
    """Medir rendimiento del flujo completo: crear usuario, libro y préstamo."""
    def flujo_completo():
        # 1. Crear usuario
        usuario_data = {
            "nombre": "Usuario Flujo",
            "email": "flujo@test.com"
        }
        resp_usuario = client.post('/usuarios',
                                  data=json.dumps(usuario_data),
                                  content_type='application/json')
        
        if resp_usuario.status_code != 201:
            return resp_usuario
        
        usuario = json.loads(resp_usuario.data)
        
        # 2. Crear libro
        libro_data = {
            "titulo": "Libro Flujo",
            "autor": "Autor Flujo",
            "isbn": "8888888888888"
        }
        resp_libro = client.post('/libros',
                                data=json.dumps(libro_data),
                                content_type='application/json')
        
        if resp_libro.status_code != 201:
            return resp_libro
        
        libro = json.loads(resp_libro.data)
        
        # 3. Crear préstamo
        prestamo_data = {
            "usuario_id": usuario['id'],
            "libro_id": libro['id']
        }
        resp_prestamo = client.post('/prestamos',
                                   data=json.dumps(prestamo_data),
                                   content_type='application/json')
        
        return resp_prestamo
    
    result = benchmark(flujo_completo)
    assert result.status_code == 201

# ============= PRUEBAS DE ESTRÉS SIMULADAS =============

def test_multiples_consultas_performance(benchmark, client):
    """Simular múltiples consultas consecutivas para medir degradación."""
    def multiples_consultas():
        resultados = []
        # Simular 10 consultas rápidas consecutivas
        for _ in range(10):
            resp1 = client.get('/usuarios')
            resp2 = client.get('/libros/disponibles')
            resp3 = client.get('/prestamos')
            resultados.extend([resp1, resp2, resp3])
        return resultados
    
    resultados = benchmark(multiples_consultas)
    # Verificar que todas las consultas fueron exitosas
    assert all(r.status_code == 200 for r in resultados)

# ============= CONFIGURACIÓN DE BENCHMARK =============

# Configuración personalizada para pytest-benchmark
pytest_plugins = ['pytest_benchmark']

def pytest_benchmark_group_stats(stats):
    """Agrupar estadísticas de benchmark por tipo de operación."""
    return stats