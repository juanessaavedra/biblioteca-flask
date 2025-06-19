from flask_sqlalchemy import SQLAlchemy #ORM
from datetime import datetime #Para manejar fechas y horas

db = SQLAlchemy() #Instancia principal de SQLAlchemy para manejar la base de datos
#La cual se importa en __init__.py para inicializar la base de datos con la aplicación Flask

class Usuario(db.Model): #db.Model es la que proporciona SQLAlchemy para definir modelos de base de datos


# Cuando tu clase hereda de db.Model, SQLAlchemy automáticamente le añade varios atributos y métodos, incluyendo query.

    __tablename__ = 'usuarios' # Define el nombre de la tabla en la base de datos
    
    id = db.Column(db.Integer, primary_key=True)
    # Ese primary_key por defecto deja autoincremental, si no se desea que sea autoincremental, se puede poner autoincrement=False como tercer argumento
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self): # Método para convertir el objeto a un diccionario, útil para respuestas JSON
    #Ya que no se puede serializar directamente un objeto de SQLAlchemy a JSON
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email
        }

class Libro(db.Model):
    __tablename__ = 'libros'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    disponible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'autor': self.autor,
            'isbn': self.isbn,
            'disponible': self.disponible
        }

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    libro_id = db.Column(db.Integer, db.ForeignKey('libros.id'), nullable=False)
    fecha_prestamo = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_devolucion = db.Column(db.DateTime)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones para obtener datos fácilmente
    usuario = db.relationship('Usuario', backref='prestamos')
    libro = db.relationship('Libro', backref='prestamos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'libro_id': self.libro_id,
            'usuario_nombre': self.usuario.nombre,
            'libro_titulo': self.libro.titulo,
            'fecha_prestamo': self.fecha_prestamo.isoformat(),
            'fecha_devolucion': self.fecha_devolucion.isoformat() if self.fecha_devolucion else None,
            'activo': self.activo
        }