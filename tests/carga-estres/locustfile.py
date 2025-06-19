# locustfile.py - Pruebas de Performance para Biblioteca Digital
from locust import HttpUser, task, between
import json
import random

class BibliotecaUser(HttpUser):
    """
    Simula un usuario que usa la aplicación de biblioteca digital
    """
    # Tiempo de espera entre tareas (1-3 segundos)
    wait_time = between(1, 3)
    
    def on_start(self):
        """
        Se ejecuta una vez cuando el usuario "virtual" inicia
        Aquí creamos datos de prueba que usaremos en las tareas
        """
        # Crear un usuario de prueba
        self.usuario_data = {
            "nombre": f"Usuario Test {random.randint(1000, 9999)}",
            "email": f"test{random.randint(1000, 9999)}@test.com"
        }
        
        # Crear un libro de prueba
        self.libro_data = {
            "titulo": f"Libro Test {random.randint(1000, 9999)}",
            "autor": f"Autor Test {random.randint(100, 999)}",
            "isbn": f"123456789{random.randint(1000, 9999)}"
        }
        
        # Variables para almacenar IDs creados
        self.usuario_id = None
        self.libro_id = None
        self.prestamo_id = None
        
        # Crear usuario y libro al inicio
        self.crear_usuario_inicial()
        self.crear_libro_inicial()
    
    def crear_usuario_inicial(self):
        """Crea un usuario al inicio para usar en préstamos"""
        response = self.client.post("/usuarios", 
                                  json=self.usuario_data,
                                  name="Crear Usuario Inicial")
        if response.status_code == 201:
            self.usuario_id = response.json()['id']
    
    def crear_libro_inicial(self):
        """Crea un libro al inicio para usar en préstamos"""
        response = self.client.post("/libros",
                                  json=self.libro_data,
                                  name="Crear Libro Inicial")
        if response.status_code == 201:
            self.libro_id = response.json()['id']

    @task(3)  # Esta tarea se ejecuta 3 veces más frecuentemente
    def verificar_salud(self):
        """Prueba el endpoint de salud - la operación más común"""
        self.client.get("/health", name="Health Check")

    @task(2)  # Se ejecuta 2 veces más frecuentemente que las de peso 1
    def listar_libros_disponibles(self):
        """Obtiene la lista de libros disponibles - operación común"""
        self.client.get("/libros/disponibles", name="Listar Libros Disponibles")

    @task(2)
    def listar_usuarios(self):
        """Obtiene la lista de usuarios"""
        self.client.get("/usuarios", name="Listar Usuarios")

    @task(2)
    def listar_prestamos(self):
        """Obtiene la lista de préstamos"""
        self.client.get("/prestamos", name="Listar Préstamos")

    @task(1)  # Se ejecuta con menor frecuencia
    def crear_usuario(self):
        """Crea un nuevo usuario"""
        nuevo_usuario = {
            "nombre": f"Usuario {random.randint(10000, 99999)}",
            "email": f"user{random.randint(10000, 99999)}@test.com"
        }
        self.client.post("/usuarios", 
                        json=nuevo_usuario,
                        name="Crear Usuario")

    @task(1)
    def crear_libro(self):
        """Crea un nuevo libro"""
        nuevo_libro = {
            "titulo": f"Libro {random.randint(10000, 99999)}",
            "autor": f"Autor {random.randint(1000, 9999)}",
            "isbn": f"978{random.randint(1000000000, 9999999999)}"
        }
        self.client.post("/libros",
                        json=nuevo_libro,
                        name="Crear Libro")

    @task(1)
    def ciclo_prestamo_completo(self):
        """
        Simula un ciclo completo: crear préstamo y devolverlo
        Esta es la operación más compleja y crítica del sistema
        """
        if self.usuario_id and self.libro_id:
            # 1. Crear préstamo
            prestamo_data = {
                "usuario_id": self.usuario_id,
                "libro_id": self.libro_id
            }
            
            response = self.client.post("/prestamos",
                                      json=prestamo_data,
                                      name="Crear Préstamo")
            
            if response.status_code == 201:
                prestamo_id = response.json()['id']
                
                # 2. Devolver libro inmediatamente (para liberar recursos)
                self.client.put(f"/prestamos/{prestamo_id}/devolver",
                              name="Devolver Libro")

# ===== CLASE ADICIONAL PARA PRUEBAS DE ESTRÉS =====
class UsuarioEstres(HttpUser):
    """
    Usuario más agresivo para pruebas de estrés
    Hace peticiones más rápido y con más carga
    """
    wait_time = between(0.1, 0.5)  # Espera muy poco entre peticiones
    
    @task(5)
    def health_check_rapido(self):
        """Health checks muy frecuentes"""
        self.client.get("/health")
    
    @task(3)
    def operaciones_lectura(self):
        """Operaciones de lectura intensiva"""
        endpoints = ["/usuarios", "/libros/disponibles", "/prestamos"]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)
    
    @task(1)
    def operaciones_escritura(self):
        """Operaciones de escritura para generar carga en BD"""
        # Alterna entre crear usuario y libro
        if random.choice([True, False]):
            usuario_data = {
                "nombre": f"Stress User {random.randint(100000, 999999)}",
                "email": f"stress{random.randint(100000, 999999)}@test.com"
            }
            self.client.post("/usuarios", json=usuario_data)
        else:
            libro_data = {
                "titulo": f"Stress Book {random.randint(100000, 999999)}",
                "autor": f"Stress Author {random.randint(10000, 99999)}",
                "isbn": f"999{random.randint(1000000000, 9999999999)}"
            }
            self.client.post("/libros", json=libro_data)