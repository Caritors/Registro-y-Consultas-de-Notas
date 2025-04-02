def ingreso_curso():
    print("Has seleccionado Ingreso de Curso")

def ingreso_estudiante():
    print("Has seleccionado Ingreso de Estudiante")

def ingreso_materia():
    print("Has seleccionado Ingreso de Materia")

def ingreso_notas():
    print("Has seleccionado Ingreso de Notas")

def login():
    print("Has seleccionado Login")

def registro():
    print("Has seleccionado Registro")

def mostrar_menu():
    print("\nMenú Principal")
    print("1. Ingreso de Curso")
    print("2. Ingreso de Estudiante")
    print("3. Ingreso de Materia")
    print("4. Ingreso de Notas")
    print("5. Login")
    print("6. Registro")
    print("7. Salir")

def main():
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            ingreso_curso()
        elif opcion == "2":
            ingreso_estudiante()
        elif opcion == "3":
            ingreso_materia()
        elif opcion == "4":
            ingreso_notas()
        elif opcion == "5":
            login()
        elif opcion == "6":
            registro()
        elif opcion == "7":
            print("Saliendo...")
            break
        else:
            print("Opción no válida, por favor ingresa una opción válida.")

if __name__ == "__main__":
    main()
