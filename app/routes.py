from flask import Blueprint, request, jsonify # Jsonify convierte respuestas a JSON
# Tambien importo request para manejar peticiones HTTP
from app.models import db, Usuario, Libro, Prestamo
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__) #Crea un blueprint llamado 'main' para agrupar las rutas de la aplicación

# @main_bp viene del import de routes.py, que es donde se define el blueprint

# ============= ENDPOINT DE SALUD =============


@main_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'message': 'API funcionando correctamente'})




# ============= CRUD USUARIOS =============


@main_bp.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuarios = Usuario.query.all() #Lista de usuarios
    return jsonify([usuario.to_dict() for usuario in usuarios])#Lista comprehension para convertir cada usuario a un diccionario

@main_bp.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    
    if not data.get('nombre') or not data.get('email'): #If not es para hacer algo si el campo no existe o es None
        return jsonify({'error': 'Nombre y email son requeridos'}), 400
    
    # Verificar si email ya existe
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email ya existe'}), 400
    
    usuario = Usuario(nombre=data['nombre'], email=data['email']) # Puede recibir cualquier campo que hayas definido en el modelo, excepto los que tienen valores automáticos.
    db.session.add(usuario) #Carrito de compras que guarda los cambios en la base de datos
    db.session.commit() # Guarda los cambios en la base de datos
    return jsonify(usuario.to_dict()), 201

@main_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado'})



# ============= CRUD LIBROS =============


@main_bp.route('/libros', methods=['GET'])
def obtener_libros():
    libros = Libro.query.all()
    return jsonify([libro.to_dict() for libro in libros])

@main_bp.route('/libros', methods=['POST'])
def crear_libro():
    data = request.get_json()
    
    # Validaciones básicas
    campos_requeridos = ['titulo', 'autor', 'isbn']
    for campo in campos_requeridos:
        if not data.get(campo):
            return jsonify({'error': f'{campo} es requerido'}), 400
    
    # Verificar si ISBN ya existe
    if Libro.query.filter_by(isbn=data['isbn']).first():
        return jsonify({'error': 'ISBN ya existe'}), 400
    
    libro = Libro(
        titulo=data['titulo'],
        autor=data['autor'],
        isbn=data['isbn']
    )
    db.session.add(libro)
    db.session.commit()
    
    return jsonify(libro.to_dict()), 201

@main_bp.route('/libros/<int:id>', methods=['PUT'])
def actualizar_libro(id):
    libro = Libro.query.get_or_404(id)
    data = request.get_json()
    
    if 'titulo' in data:
        libro.titulo = data['titulo']
    if 'autor' in data:
        libro.autor = data['autor']
    if 'disponible' in data:
        libro.disponible = data['disponible']
    
    db.session.commit()
    return jsonify(libro.to_dict())

@main_bp.route('/libros/<int:id>', methods=['DELETE'])
def eliminar_libro(id):
    libro = Libro.query.get_or_404(id)
    db.session.delete(libro)
    db.session.commit()
    return jsonify({'message': 'Libro eliminado'})



# ============= GESTIÓN DE PRÉSTAMOS =============

@main_bp.route('/prestamos', methods=['GET'])
def obtener_prestamos():
    prestamos = Prestamo.query.all()
    return jsonify([prestamo.to_dict() for prestamo in prestamos])

@main_bp.route('/prestamos', methods=['POST'])
def crear_prestamo():
    data = request.get_json()
    
    usuario_id = data.get('usuario_id')
    libro_id = data.get('libro_id')
    
    if not usuario_id or not libro_id:
        return jsonify({'error': 'usuario_id y libro_id son requeridos'}), 400
    
    # Verificar que usuario existe
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    # Verificar que libro existe y está disponible
    libro = Libro.query.get(libro_id)
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    if not libro.disponible:
        return jsonify({'error': 'Libro no disponible'}), 400
    
    # Crear préstamo
    prestamo = Prestamo(
        usuario_id=usuario_id,
        libro_id=libro_id
    )
    
    # Marcar libro como no disponible
    libro.disponible = False
    
    db.session.add(prestamo)
    db.session.commit()
    
    return jsonify(prestamo.to_dict()), 201

@main_bp.route('/prestamos/<int:id>/devolver', methods=['PUT'])
def devolver_libro(id):
    prestamo = Prestamo.query.get_or_404(id)
    
    if not prestamo.activo:
        return jsonify({'error': 'Este préstamo ya fue devuelto'}), 400
    
    # Procesar devolución
    prestamo.fecha_devolucion = datetime.utcnow()
    prestamo.activo = False
    
    # Marcar libro como disponible
    libro = Libro.query.get(prestamo.libro_id)
    libro.disponible = True
    
    db.session.commit()
    
    return jsonify(prestamo.to_dict())

# ============= ENDPOINT PARA LISTAR LIBROS DISPONIBLES =============
@main_bp.route('/libros/disponibles', methods=['GET'])
def libros_disponibles():
    libros = Libro.query.filter_by(disponible=True).all()
    return jsonify([libro.to_dict() for libro in libros])