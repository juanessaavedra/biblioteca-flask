# tests/ui/conftest.py
# Configuración específica para las pruebas de UI con Selenium
# Este archivo evita conflictos con pytest-flask

import pytest

# Deshabilitar los fixtures automáticos de pytest-flask para estas pruebas UI
pytest_plugins = []