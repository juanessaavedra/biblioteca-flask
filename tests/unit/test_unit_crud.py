# test_unitarios_crud.py - 8 Tests unitarios del CRUD
import json
import pytest

# ============= 4 PRUEBAS PARA LÓGICA DE NEGOCIO DEL BACKEND =============

class TestCRUDLibros:
    """Tests unitarios del CRUD de libros"""
    
    def test_crear_libro(self, client):
        """Test 1: Crear libro"""
        data = {
            "titulo": "El Quijote",
            "autor": "Miguel de Cervantes", 
            "isbn": "9781234567890"
        }
        response = client.post('/libros',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['titulo'] == "El Quijote"
        assert response_data['disponible'] == True

    def test_obtener_libros(self, client, sample_libro):
        """Test 2: Obtener lista de libros"""
        response = client.get('/libros')
        
        assert response.status_code == 200
        libros = json.loads(response.data)
        assert len(libros) >= 1
        assert libros[0]['titulo'] == sample_libro.titulo

    def test_actualizar_libro(self, client, sample_libro):
        """Test 3: Actualizar libro"""
        data = {
            "titulo": "Nuevo Título",
            "disponible": False
        }
        response = client.put(f'/libros/{sample_libro.id}',
                            data=json.dumps(data),
                            content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['titulo'] == "Nuevo Título"
        assert response_data['disponible'] == False

    def test_eliminar_libro(self, client, sample_libro):
        """Test 4: Eliminar libro"""
        response = client.delete(f'/libros/{sample_libro.id}')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'eliminado' in response_data['message']

class TestCRUDUsuarios:
    """Tests unitarios del CRUD de usuarios"""
    
    def test_crear_usuario(self, client):
        """Test 5: Crear usuario"""
        data = {
            "nombre": "Juan Pérez",
            "email": "juan@test.com"
        }
        response = client.post('/usuarios',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['nombre'] == "Juan Pérez"
        assert response_data['email'] == "juan@test.com"

    def test_obtener_usuarios(self, client, sample_usuario):
        """Test 6: Obtener lista de usuarios"""
        response = client.get('/usuarios')
        
        assert response.status_code == 200
        usuarios = json.loads(response.data)
        assert len(usuarios) >= 1
        assert usuarios[0]['email'] == sample_usuario.email

# ============= 2 PRUEBAS PARA VALIDACIONES DE DATOS =============

class TestValidaciones:
    """Tests unitarios de validaciones"""
    
    def test_validacion_email_duplicado(self, client, sample_usuario):
        """Test 7: Validación de email duplicado"""
        data = {
            "nombre": "Otro Usuario",
            "email": sample_usuario.email  # Email que ya existe
        }
        response = client.post('/usuarios',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Email ya existe' in response_data['error']

    def test_validacion_campos_requeridos_libro(self, client):
        """Test 8: Validación de campos requeridos en libro"""
        data = {
            "titulo": "Solo Título"
            # Faltan autor e isbn
        }
        response = client.post('/libros',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'requerido' in response_data['error']