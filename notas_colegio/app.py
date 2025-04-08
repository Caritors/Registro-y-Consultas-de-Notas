from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/notas_colegio_2'
app.config['SECRET_KEY'] = 'tu_clave_secreta'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelos

class Grado(db.Model):
    __tablename__ = 'grado'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cursos = db.relationship('Curso', backref='grado', lazy=True)

    def __repr__(self):
        return f"<Grado {self.nombre}>"

    
class Curso(db.Model):
    __tablename__ = 'curso'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    grado_id = db.Column(db.Integer, db.ForeignKey('grado.id'), nullable=False)
    estudiantes = db.relationship('Estudiante', backref='curso', lazy=True)

class Estudiante(db.Model):
    __tablename__ = 'estudiante'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    documento = db.Column(db.String(100), nullable=False, unique=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    notas = db.relationship('Nota', backref='estudiante', lazy=True)

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
    curso = db.relationship('Curso', backref='notas')
    
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(120), nullable=False)
    

    def __repr__(self):
        return f"<Usuario {self.correo}>"
   

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        # Aquí podrías agregar lógica real de autenticación
        # Por ahora solo simulamos un login exitoso
        if correo == 'admin@colegio.com' and contraseña == 'admin123':
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/registro_grado', methods=['GET', 'POST'])
def registro_grado():
    if request.method == 'POST':
        nombre = request.form['nombre']
        if not nombre:
            flash('El nombre del grado es obligatorio', 'danger')
        else:
            nuevo_grado = Grado(nombre=nombre)
            db.session.add(nuevo_grado)
            db.session.commit()
            flash('Grado registrado exitosamente', 'success')
            return redirect(url_for('index'))
    return render_template('registro_grado.html')

@app.route('/registro_usuario', methods=['GET', 'POST'])
def registro_usuario():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        nuevo_usuario = Usuario(correo=correo, contraseña=contraseña)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario registrado exitosamente', 'success')
        return redirect(url_for('login'))

    return render_template('registro_usuario.html')


@app.route('/ingreso_curso', methods=['GET', 'POST'])
def ingreso_curso():
    if request.method == 'POST':
        grado_id = request.form.get('grado')
        curso_nombre = request.form.get('curso')

        if not grado_id or not curso_nombre:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('ingreso_curso'))

        grado = Grado.query.get(int(grado_id))
        if not grado:
            flash('Grado no encontrado.', 'danger')
            return redirect(url_for('ingreso_curso'))

        curso_existente = Curso.query.filter_by(nombre=curso_nombre, grado_id=grado.id).first()
        if curso_existente:
            flash('El curso ya existe en este grado.', 'danger')
            return redirect(url_for('ingreso_curso'))

        nuevo_curso = Curso(nombre=curso_nombre, grado_id=grado.id)
        db.session.add(nuevo_curso)
        db.session.commit()
        flash('Curso registrado exitosamente.', 'success')
        return redirect(url_for('consulta'))

    grados = Grado.query.all()
    print("Grados encontrados:, grados")
    return render_template('ingreso_curso.html', grados=grados)
    

@app.route('/ingreso_estudiante', methods=['GET', 'POST'])
def ingreso_estudiante():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        documento = request.form['documento']
        id_curso = request.form['id_curso']

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
            flash(f'Error al guardar el estudiante: {str(e)}', 'danger')

        return redirect(url_for('index'))

    cursos = Curso.query.all()
    return render_template('ingreso_estudiante.html', cursos=cursos)

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

        nueva_nota = Nota(
            estudiante_id=estudiante_id,
            curso_id=curso_id,
            nota=nota,
            periodo=periodo
        )
        db.session.add(nueva_nota)
        db.session.commit()
        flash("Nota ingresada correctamente", "success")
        return redirect(url_for('ingreso_notas'))

    estudiantes = Estudiante.query.all()
    cursos = Curso.query.all()
    return render_template('ingreso_notas.html', estudiantes=estudiantes, cursos=cursos)

@app.route('/ingreso_materia', methods=['GET', 'POST'])
def ingreso_materia():
    if request.method == 'POST':
        nombre = request.form['nombre']
        intensidad = request.form['intensidad_horaria']
        descripcion = request.form['descripcion']
        nueva = Materia(nombre=nombre, intensidad_horaria=intensidad, descripcion=descripcion)
        db.session.add(nueva)
        db.session.commit()
        flash('Materia registrada exitosamente', 'success')
        return redirect(url_for('index'))
    return render_template('ingreso_materia.html')



@app.route('/consulta')
def consulta():
    estudiantes = Estudiante.query.all()
    cursos = Curso.query.all()
    grados = Grado.query.all()
    print("Estudiantes:", estudiantes)
    print("Cursos:", cursos)
    print("Grados:", grados)
    return render_template('consulta.html', estudiantes=estudiantes, cursos=cursos, grados=grados)


    


# Inicialización
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

