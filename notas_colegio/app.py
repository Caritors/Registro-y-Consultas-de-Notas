from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from app import db
#from models import db, Curso, Estudiante, Nota 

# Inicialización de la app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/notas_colegio_2'
app.config['SECRET_KEY'] = 'tu_clave_secreta'

# Inicializa la base de datos
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelos
class Grado(db.Model):
    __tablename__ = 'grado'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    
    # Relación con Curso
    cursos = db.relationship('Curso', backref='grado', lazy=True)

class Curso(db.Model):
    __tablename__ = 'curso'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    grado_id = db.Column(db.Integer, db.ForeignKey('grado.id'), nullable=False)

    # Relación con Estudiante
    estudiantes = db.relationship('Estudiante', backref='curso', lazy=True)


class Estudiante(db.Model):
    __tablename__ = 'estudiante'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    documento = db.Column(db.String(100), nullable=False, unique=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)

class Materia(db.Model):
    __tablename__ = 'materia'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    intensidad_horaria = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

class Nota(db.Model):
    __tablename__ = 'nota'
    
    id = db.Column(db.Integer, primary_key=True)
    nota = db.Column(db.String(5), nullable=False)
    periodo = db.Column(db.String(100), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)

# Rutas de la aplicación
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/ingreso_estudiante', methods=['GET', 'POST'])
def ingreso_estudiante():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        documento = request.form['documento']
        id_curso = request.form['id_curso']

        # Crear nuevo estudiante
        nuevo_estudiante = Estudiante(
            nombre=nombre, apellido=apellido, correo=correo,
            documento=documento, curso_id=id_curso
        )
        
        try:
            db.session.add(nuevo_estudiante)
            db.session.commit()
            flash('Estudiante registrado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al guardar el estudiante: {str(e)}', 'danger')
        
        return redirect(url_for('index'))
    
    cursos = Curso.query.all()
    return render_template('ingreso_estudiante.html', cursos=cursos)

@app.route('/ingreso_curso', methods=['GET', 'POST'])
def ingreso_curso():
    if request.method == 'POST':
        grado_id = request.form.get('grado')  # Obtener el ID del grado
        curso_nombre = request.form.get('curso')  # Obtener nombre del curso

        print(f"Grado recibido: {grado_id}, Curso: {curso_nombre}")  # Para depuración

        if not grado_id or not curso_nombre:
            flash('Error: Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('ingreso_curso'))

        if not grado_id.isdigit():  # Validar si es un número
            flash('Error: ID de grado inválido.', 'danger')
            return redirect(url_for('ingreso_curso'))

        grado_id = int(grado_id)

        # Verificar que el grado existe en la base de datos
        grado_existente = Grado.query.get(grado_id)
        if not grado_existente:
            flash('Error: El grado seleccionado no existe.', 'danger')
            return redirect(url_for('ingreso_curso'))

        # Verificar que el curso no exista ya en ese grado
        curso_existente = Curso.query.filter_by(nombre=curso_nombre, grado_id=grado_id).first()
        if curso_existente:
            flash('Error: El curso ya existe en este grado.', 'danger')
            return redirect(url_for('ingreso_curso'))

        # Crear el nuevo curso
        nuevo_curso = Curso(nombre=curso_nombre, grado_id=grado_id)
        db.session.add(nuevo_curso)
        db.session.commit()
        flash('Curso ingresado exitosamente', 'success')

        return redirect(url_for('consulta'))

    # Cargar los grados disponibles
    grados = Grado.query.all()
    return render_template('ingreso_curso.html', grados=grados)

@app.route('/ingreso_materia', methods=['GET', 'POST'])
def ingreso_materia():
    if request.method == 'POST':
        nombre = request.form['nombre']
        intensidad_horaria = request.form['intensidad_horaria']
        descripcion = request.form['descripcion']
        nueva_materia = Materia(nombre=nombre, intensidad_horaria=intensidad_horaria, descripcion=descripcion)
        db.session.add(nueva_materia)
        db.session.commit()
        flash('Materia registrada exitosamente', 'success')
        return redirect(url_for('index'))
    return render_template('ingreso_materia.html')



@app.route('/registro_usuario', methods=['GET', 'POST'])
def registro_usuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')

        if not nombre or not apellido or not correo or not contraseña:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('registro_usuario'))
        
        flash('Usuario registrado exitosamente', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro_usuario.html')


    


@app.route('/ingreso_notas', methods=['GET', 'POST'])
def ingreso_notas():
    if request.method == 'POST':
        estudiante_id = request.form.get('estudiante')
        curso_id = request.form.get('curso')
        nota = request.form.get('nota')
        periodo = request.form.get('periodo')

        if not estudiante_id or not curso_id or nota is None or not periodo:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for('ingreso_notas'))

        estudiante = Estudiante.query.get(estudiante_id)
        if not estudiante:
            flash("Error: Estudiante no encontrado.", "danger")
            return redirect(url_for('ingreso_notas'))

        curso = Curso.query.get(curso_id)
        if not curso:
            flash("Error: Curso no encontrado.", "danger")
            return redirect(url_for('ingreso_notas'))

        # Guardar en la base de datos
        nueva_nota = Nota(estudiante_id=estudiante_id, curso_id=curso_id, nota=nota, periodo=periodo)
        db.session.add(nueva_nota)
        db.session.commit()

        flash("Nota ingresada correctamente", "success")
        return redirect(url_for('ingreso_notas'))

    # Obtener los datos para los select
    estudiantes = Estudiante.query.all()
    cursos = Curso.query.all()  # <---- Agregado para cargar los cursos

    return render_template('ingreso_notas.html', estudiantes=estudiantes, cursos=cursos)



@app.route('/consulta')
def consulta():
    estudiantes = Estudiante.query.all()
    materias = Materia.query.all()
    cursos = Curso.query.all()
    notas = Nota.query.all()
    return render_template('consulta.html', materias=materias, cursos=cursos, estudiantes=estudiantes, notas=notas)

# Inicializar base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
