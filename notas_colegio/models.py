from app import db

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    materia = db.Column(db.String(100), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    cursos = db.relationship('Curso', backref='grado')


