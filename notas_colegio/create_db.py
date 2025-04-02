# create_db.py
from app import db

# Crear todas las tablas definidas en el modelo
db.create_all()

print("Base de datos creada con éxito.")
