from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/notas_colegio_2'
app.config['SECRET_KEY'] = 'tu_clave_secreta'

# Inicializar extensiones
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# MODELOS
class Grado(db.Model):
    __tablename__ = 'grado'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    cursos = db.relationship('Curso', backref='grado', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'cursos': [curso.to_dict() for curso in self.cursos]
        }

class Curso(db.Model):
    __tablename__ = 'curso'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    grado_id = db.Column(db.Integer, db.ForeignKey('grado.id'), nullable=False)
    estudiantes = db.relationship('Estudiante', backref='curso', lazy=True, cascade="all, delete-orphan")
    notas = db.relationship('Nota', backref='curso', lazy=True)
    materias = db.relationship('Materia', backref='curso', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'grado_id': self.grado_id,
            'estudiantes': [e.to_dict() for e in self.estudiantes],
            'notas': [n.to_dict() for n in self.notas]
        }

class Estudiante(db.Model):
    __tablename__ = 'estudiante'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    documento = db.Column(db.String(100), nullable=False, unique=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    notas = db.relationship('Nota', backref='estudiante', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'correo': self.correo,
            'documento': self.documento,
            'curso_id': self.curso_id
        }

class Materia(db.Model):
    __tablename__ = 'materia'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    intensidad_horaria = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'))

class Nota(db.Model):
    __tablename__ = 'nota'
    id = db.Column(db.Integer, primary_key=True)
    nota = db.Column(db.String(5), nullable=False)
    periodo = db.Column(db.String(100), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nota': self.nota,
            'periodo': self.periodo,
            'estudiante_id': self.estudiante_id,
            'curso_id': self.curso_id,
            'estudiante': {
            'nombre': self.estudiante.nombre,
            'apellido': self.estudiante.apellido
        } if self.estudiante else None,
        'curso': {
            'nombre': self.curso.nombre,
            'grado': {
                'id': self.curso.grado.id,
                'nombre': self.curso.grado.nombre
            } if self.curso and self.curso.grado else None
        } if self.curso else None
    }


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(120), nullable=False)

# RUTAS PRINCIPALES
@app.route('/')
def index():
    return render_template('index.html')

from flask import session

from werkzeug.security import check_password_hash  # Asegúrate de importar esto

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')

        if correo and contrasena:
            usuario = Usuario.query.filter_by(correo=correo).first()
            if usuario and check_password_hash(usuario.contrasena, contrasena):  # Verificación con hash
                # Si la contraseña es correcta, guarda el id del usuario en la sesión
                session['usuario_id'] = usuario.id
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('index'))
            else:
                flash('Correo o contraseña incorrectos', 'danger')
        else:
            flash('Por favor, completa todos los campos', 'warning')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)  # Elimina la sesión del usuario
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))



@app.route('/registro_usuario', methods=['GET', 'POST'])
def registro_usuario():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')

        # Verifica que todos los campos estén completos
        if not correo or not contrasena or not confirmar_contrasena:
            flash('Todos los campos son obligatorios.', 'danger')
        
        # Verifica si el usuario ya existe
        elif Usuario.query.filter_by(correo=correo).first():
            flash('El usuario ya existe.', 'danger')
        
        # Verifica si las contraseñas coinciden
        elif contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden.', 'danger')
        
        else:
            # Cifra la contraseña antes de guardarla
            contrasena_hash = generate_password_hash(contrasena)
            # Agrega el nuevo usuario a la base de datos
            db.session.add(Usuario(correo=correo, contrasena=contrasena_hash))
            db.session.commit()
            flash('Usuario registrado correctamente.', 'success')
            return redirect(url_for('login'))

    return render_template('registro_usuario.html')


@app.route('/registro_grado', methods=['GET', 'POST'])
def registro_grado():
    if request.method == 'POST':
        nombre = request.form['nombre']
        if not nombre:
            flash('El nombre del grado es obligatorio', 'danger')
        else:
            db.session.add(Grado(nombre=nombre))
            db.session.commit()
            flash('Grado registrado exitosamente', 'success')
            return redirect(url_for('index'))
    return render_template('registro_grado.html')

@app.route('/registrar_nota', methods=['GET', 'POST'])
def registrar_nota():
    if request.method == 'POST':
        grado_id = request.form['grado']
        curso_id = request.form['curso']
        estudiante_id = request.form['estudiante']
        nota = request.form['nota']
        periodo = request.form['periodo']
        
        # Guardar la nueva nota en la base de datos
        nueva_nota = Nota(
            curso_id=curso_id,
            estudiante_id=estudiante_id,
            nota=nota,
            periodo=periodo
        )
        db.session.add(nueva_nota)
        db.session.commit()
        
        # Redirigir a la página de notas registradas
        return redirect(url_for('notas_registradas'))
    
    # Consultar todos los grados con cursos y estudiantes
    grados = Grado.query.options(db.joinedload(Grado.cursos).joinedload(Curso.estudiantes)).all()

    # Transformar los datos en un formato adecuado para JavaScript
    grados_data = [
        {
            'id': g.id,
            'nombre': g.nombre,
            'cursos': [{'id': c.id, 'nombre': c.nombre, 'estudiantes': [{'id': e.id, 'nombre': e.nombre, 'apellido': e.apellido} for e in c.estudiantes]} for c in g.cursos]
        }
        for g in grados
    ]
    
    return render_template('registrar_nota.html', grados=grados_data)



@app.route('/ingreso_curso', methods=['GET', 'POST'])
def ingreso_curso():
    if request.method == 'POST':
        grado_id = request.form['grado']
        curso_nombre = request.form['curso']
        if not grado_id or not curso_nombre:
            flash('Todos los campos son obligatorios.', 'danger')
        elif Curso.query.filter_by(nombre=curso_nombre, grado_id=grado_id).first():
            flash('El curso ya existe en este grado.', 'danger')
        else:
            db.session.add(Curso(nombre=curso_nombre, grado_id=grado_id))
            db.session.commit()
            flash('Curso registrado exitosamente.', 'success')
            return redirect(url_for('consulta'))
    grados = Grado.query.all()
    return render_template('ingreso_curso.html', grados=grados)

@app.route('/ingreso_estudiante', methods=['GET', 'POST'])
def ingreso_estudiante():
    if request.method == 'POST':
        nuevo = Estudiante(
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            correo=request.form['correo'],
            documento=request.form['documento'],
            curso_id=request.form['id_curso']
        )
        try:
            db.session.add(nuevo)
            db.session.commit()
            flash('Estudiante registrado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {e}', 'danger')
        return redirect(url_for('ingreso_estudiante'))
    return render_template('ingreso_estudiante.html', grados=Grado.query.all(), estudiantes=Estudiante.query.all())

@app.route('/ingreso_materia', methods=['GET', 'POST'])
def ingreso_materia():
    if request.method == 'POST':
        materia = Materia(
            nombre=request.form['nombre'],
            intensidad_horaria=request.form['intensidad_horaria'],
            descripcion=request.form['descripcion'],
            curso_id=request.form['curso_id']
        )
        db.session.add(materia)
        db.session.commit()
        flash('Materia registrada exitosamente', 'success')
        return redirect(url_for('materias_registradas'))
    return render_template('ingreso_materia.html', grados=Grado.query.options(db.joinedload(Grado.cursos)).all())

@app.route('/ingreso_notas', methods=['GET', 'POST'])
def ingreso_notas():
    if request.method == 'POST':
        nueva = Nota(
            estudiante_id=request.form['estudiante'],
            curso_id=request.form['curso'],
            nota=request.form['nota'],
            periodo=request.form['periodo']
        )
        db.session.add(nueva)
        db.session.commit()
        flash('Nota ingresada correctamente', 'success')
        return redirect(url_for('ingreso_notas'))
    return render_template('ingreso_notas.html', estudiantes=Estudiante.query.all(), cursos=Curso.query.all(), grados=Grado.query.all())

@app.route('/consulta')
def consulta():
    grados = Grado.query.options(db.joinedload(Grado.cursos).joinedload(Curso.estudiantes).joinedload(Estudiante.notas)).all()
    return render_template('consulta.html', grados=grados)

@app.route('/notas_registradas')
def notas_registradas():
    grados = Grado.query.options(db.joinedload(Grado.cursos)).all()
    grados_data = [g.to_dict() for g in grados]
    grado_id = request.args.get('grado')
    curso_id = request.args.get('curso')
    buscar = request.args.get('buscar', '').strip().lower()

    query = Nota.query.join(Estudiante).join(Curso).join(Grado)
    if grado_id:
        query = query.filter(Curso.grado_id == grado_id)
    if curso_id:
        query = query.filter(Nota.curso_id == curso_id)
    if buscar:
        query = query.filter(
            (Estudiante.nombre.ilike(f'%{buscar}%')) |
            (Estudiante.apellido.ilike(f'%{buscar}%'))
        )
    notas = [n.to_dict() for n in query.all()]
    return render_template('notas_registradas.html', notas=notas, grados=grados_data, grado_id=grado_id, curso_id=curso_id, buscar=buscar)

@app.route('/materias_registradas')
def materias_registradas():
    grados = Grado.query.options(db.joinedload(Grado.cursos).joinedload(Curso.materias)).all()
    return render_template('materias_registradas.html', grados=grados)

@app.route('/cursos_por_grado/<int:grado_id>')
def cursos_por_grado(grado_id):
    cursos = Curso.query.filter_by(grado_id=grado_id).all()
    return jsonify([{'id': c.id, 'nombre': c.nombre} for c in cursos])

@app.route('/estudiantes_por_curso/<int:curso_id>')
def estudiantes_por_curso(curso_id):
    estudiantes = Estudiante.query.filter_by(curso_id=curso_id).all()
    return jsonify([{'id': e.id, 'nombre': e.nombre, 'apellido': e.apellido} for e in estudiantes])

@app.route('/consulta_estudiantes')
def consulta_estudiantes():
    estudiantes = Estudiante.query.join(Curso).join(Grado).all()
    return render_template('consulta_estudiantes.html', estudiantes=estudiantes)

@app.route('/lista_estudiantes')
def lista_estudiantes():
    # Código para obtener la lista de estudiantes
    return render_template('lista_estudiantes.html')


# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)




