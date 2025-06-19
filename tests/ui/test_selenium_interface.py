# tests/ui/test_safari_simple.py
# Versión con Safari - no necesita descargar drivers externos

import pytest
import time
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.safari.options import Options

# ============= CONFIGURACIÓN CON SAFARI =============

@pytest.fixture(scope="module") 
def flask_server():
    """Iniciar servidor Flask usando subprocess"""
    process = subprocess.Popen([
        sys.executable, "-c",
        """
from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Base de datos inicializada")

print("🚀 Servidor iniciando en http://127.0.0.1:5003")
app.run(host='127.0.0.1', port=5003, debug=False)
        """
    ])
    
    # Esperar que el servidor inicie
    time.sleep(5)
    
    yield "http://127.0.0.1:5003"
    
    # Terminar el proceso al final
    process.terminate()
    process.wait()

@pytest.fixture
def driver():
    """Driver de Safari (ya viene incluido en macOS)"""
    safari_options = Options()
    
    try:
        driver = webdriver.Safari(options=safari_options)
        yield driver
        driver.quit()
    except Exception as e:
        pytest.skip(f"Safari WebDriver no disponible: {e}")

# ============= PRUEBAS SENCILLAS =============

def test_abrir_pagina_safari(driver, flask_server):
    """Test 1: Verificar que la página abre correctamente con Safari"""
    driver.get(f"{flask_server}/frontend/index.html")
    
    # Verificar que el título contiene "Biblioteca"
    assert "Biblioteca Digital" in driver.title or "Biblioteca" in driver.page_source

def test_crear_libro_safari(driver, flask_server):
    """Test 2: Crear un libro usando Safari"""
    driver.get(f"{flask_server}/frontend/index.html")
    
    wait = WebDriverWait(driver, 10)
    
    # Llenar formulario
    titulo_input = wait.until(EC.presence_of_element_located((By.ID, "titulo")))
    autor_input = driver.find_element(By.ID, "autor")
    isbn_input = driver.find_element(By.ID, "isbn")
    
    titulo_input.clear()
    titulo_input.send_keys("Harry Potter Safari")
    autor_input.clear()
    autor_input.send_keys("J.K. Rowling")
    isbn_input.clear()
    isbn_input.send_keys("9780747532699")
    
    # Enviar formulario
    submit_button = driver.find_element(By.CSS_SELECTOR, "#formLibro button[type='submit']")
    submit_button.click()
    
    # Verificar mensaje de éxito
    mensaje = wait.until(EC.presence_of_element_located((By.ID, "mensajeLibro")))
    assert "exitosamente" in mensaje.text.lower() or "creado" in mensaje.text.lower()

def test_campos_se_limpian_safari(driver, flask_server):
    """Test 3: Verificar que los campos se limpian después de crear"""
    driver.get(f"{flask_server}/frontend/index.html")
    wait = WebDriverWait(driver, 10)
    
    # Llenar formulario
    titulo_input = wait.until(EC.presence_of_element_located((By.ID, "titulo")))
    autor_input = driver.find_element(By.ID, "autor")
    isbn_input = driver.find_element(By.ID, "isbn")
    
    titulo_input.send_keys("Test Safari")
    autor_input.send_keys("Autor Safari")
    isbn_input.send_keys("1234567890123")
    
    # Enviar
    submit_button = driver.find_element(By.CSS_SELECTOR, "#formLibro button[type='submit']")
    submit_button.click()
    
    # Esperar mensaje de éxito
    wait.until(EC.text_to_be_present_in_element((By.ID, "mensajeLibro"), "exitosamente"))
    
    # Verificar campos vacíos
    assert titulo_input.get_attribute("value") == ""
    assert autor_input.get_attribute("value") == ""
    assert isbn_input.get_attribute("value") == ""