# ============================================================
# Proyecto: Sistema de Horarios de Clases
# Autores: Denis Daniel & Capozzolo Roguer
# Materia: Algoritmos y Programacion (BPTSP05)
# Trimestre: 2526-2
# Universidad Metropolitana
# ============================================================

from datetime import datetime, time # Importar libreria de tiempo para guardar las horas de los bloques en type: datetime
import requests # Importar libreria de request para obtener los datos del github
import json # Importar libreria de Json para cuando tenga los datos del github los tenga en archivo .json
import os # Importar libreria de os para limpiar la pantalla de la consola
import csv # Importar libreria de csv para guardar y cargar archivos CSV
import matplotlib.pyplot as plt # Importar libreria de matplotlib para generar graficas de estadisticas

# URL base para descargar los archivos JSON del repositorio de GitHub
BASE_url = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-2/main"

def limpiar_pantalla():
    """
    Funcion que limpia la pantalla de la consola.
    Funciona tanto en Windows (cls) como en Mac/Linux (clear).
    """
    # os.name devuelve 'nt' en Windows y 'posix' en Mac/Linux
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

# Informacion de los bloques posibles

bloques_fijos = [
    ("Lunes y Miércoles", "7:00", "8:30"),
    ("Lunes y Miércoles", "8:45", "10:15"),
    ("Lunes y Miércoles", "10:30", "12:00"),
    ("Lunes y Miércoles", "12:15", "1:45"),
    ("Lunes y Miércoles", "2:00", "3:30"),
    ("Lunes y Miércoles", "3:45", "5:15"),
    ("Lunes y Miércoles", "5:30", "7:00"),
    ("Martes y Jueves", "7:00", "8:30"),
    ("Martes y Jueves", "8:45", "10:15"),
    ("Martes y Jueves", "10:30", "12:00"),
    ("Martes y Jueves", "12:15", "1:45"),
    ("Martes y Jueves", "2:00", "3:30"),
    ("Martes y Jueves", "3:45", "5:15"),
    ("Martes y Jueves", "5:30", "7:00"),
]


"""
=======================================================
CLASES
=======================================================
"""

class StatusSeccion():
    """
    Atributos: Assignada: str, Cerrada_no_prof: str, sin_asignar_clase: str

    Clase de tres estados en la cual puede estar la materia
    """
    Assignada = "Asignada"
    Cerrada_no_prof = "Cerrada_no_prof"
    sin_asignar_clase = "sin_asignar_clase"

class Materia:
    """
    Atributos de Materia: codigo_mat: str, nombre_mat: str, secciones_requeridas: int

    Metodos de Materia: Esta_abierta() => bool
    """
    def __init__(self, codigo_mat: str, nombre_mat: str, secciones_requeridas: int):
        self.codigo = codigo_mat
        self.nombre_mat = nombre_mat
        self.secciones_requeridas = secciones_requeridas
        self.secciones = []

    def Esta_abierta(self) -> bool:
        return self.secciones_requeridas > 0
    
    def __str__(self) -> str:
        return f"{self.codigo} - {self.nombre_mat} (Secciones: {self.secciones_requeridas})"


class Profesor:
    """
    Atributos de Profesor: nombre: str, cedula: str, email: str, max_materias: int

    Metodos de Profesor: Puede_Enseñar_Mas(int) => bool, Puede_dar_materia(Materia) => bool
    """
    def __init__(self, nombre: str, cedula: str, email: str, max_materias: int):
        self.nombre = nombre
        self.cedula = cedula
        self.email = email
        self.max_materias = max_materias
        self.List_materias = []

    def Puede_Enseñar_Mas(self, Asignado: int) -> bool:
        return Asignado < self.max_materias

    def Puede_dar_materia(self, materia: Materia) -> bool:
        return materia in self.List_materias

    def __str__(self) -> str:
        materias = ", ".join(m.codigo for m in self.List_materias) if self.List_materias else "Ninguna"
        return f"{self.cedula} | {self.nombre} | {self.email} | Max: {self.max_materias} | Materias: {materias}"


class Bloque:
    """Representa un bloque horario con días y rango de horas.

    Atributos:
        Dias_disp (str): Días disponibles, ej. ``"Lunes y miercoles"``.
        Hora_init (str): Hora de inicio en formato ``"HH:MM"``.
        Hora_fin (str): Hora de fin en formato ``"HH:MM"``.

    Métodos:
        Etiqueta: Retorna un título legible del bloque.
    """
    def __init__(self, Dias_disp: str, Hora_init: str, Hora_fin: str):
        self.Dias_disp = Dias_disp

        # Convertir str -> datetime.time
        self.Hora_init: time = datetime.strptime(Hora_init, "%H:%M").time()
        self.Hora_fin: time = datetime.strptime(Hora_fin, "%H:%M").time()

    def Etiqueta(self) -> str:
        """Retorna un título legible por la hora del bloque.

        Ejemplo:
            >>> bloque.Etiqueta()
            'Lunes y Miercoles 07:00 - 8:00'
        """
        inicio = self.Hora_init.strftime("%H:%M")
        fin = self.Hora_fin.strftime("%H:%M")

        return f"{self.Dias_disp} {inicio} - {fin}"

    def __str__(self) -> str:
        return self.Etiqueta()

class Seccion:
    """
    Atributos Necesarios: NumSeccion: int

    Atributos Propios: status: StatusSeccion, profesor: None, bloque: None, materia: None, id_salon: None

    Metodos: Id_salon() => int | None, Asig_prof(Profesor), Asig_Bloque(Bloque), Marcar_no_Prof(), Marcar_no_Materia()
    """
    def __init__(self, NumSeccion: int):
        self.NumSeccion = NumSeccion
        self.Status = StatusSeccion.Assignada
        self.profesor = None
        self.bloque = None
        self.materia = None
        self.id_salon = None

    def Id_salon(self) -> int | None:
        return self.id_salon

    def Asig_prof(self, profesor: Profesor):
        self.profesor = profesor

    def Asig_Bloque(self, bloque: Bloque):
        self.bloque = bloque

    def Marcar_no_Prof(self):
        """
        Funcion que vuelve None todos los valores: profesor, bloque, id_salon y le asigna Cerrada sin
        profesor a la clase Seccion 
        """
        self.Status = StatusSeccion.Cerrada_no_prof
        self.profesor = None
        self.bloque = None
        self.id_salon = None

    def Marcar_no_Materia(self):
        self.Status = StatusSeccion.sin_asignar_clase
        self.id_salon = None

    def __str__(self) -> str:
        materia = self.materia.codigo if self.materia else "N/A"
        prof = self.profesor.nombre if self.profesor else "N/A"
        bloque = self.bloque.Etiqueta() if self.bloque else "N/A"
        salon = self.id_salon if self.id_salon is not None else "N/A"
        return (
            f"Materia: {materia} | Sección: {self.NumSeccion} | "
            f"Profesor: {prof} | Bloque: {bloque} | Aula: {salon} | "
            f"Estado: {self.Status}"
        )
    
class Horario:
    """
    Atributos Necesarios: num_aulas: int

    Atributos Propios: secciones: list

    Metodos: Get_secciones_por_materia(Materia) => list, Get_secciones_por_prof(Profesor) => list, Aulas_ocupadas(Bloque) => int,
    Aula_abierta(Bloque) => int, Disponibilidad_prof(Profesor, Bloque) => bool
    """
    def __init__(self, num_aulas: int):
        self.num_aulas = num_aulas
        self.secciones = []
    
    def Get_secciones_por_materia(self, materia: Materia) -> list[Seccion]:
        """
        Devolver todas las secciones del horario que corresponden a una materia
        """
        resultado = []
        for s in self.secciones:
            if s.materia == materia:
                resultado.append(s)
        return resultado
    
    def Get_secciones_por_prof(self, profesor: Profesor) -> list[Seccion]:
        """
        Devuelve una lista con todas las secciones cuyo profesor sea igual al profesor recibido
        """
        resultado = []
        for s in self.secciones:
            if s.profesor == profesor:
                resultado.append(s)
        return resultado
    
    def Aulas_ocupadas(self, bloque: Bloque) -> int:
        """
        Devuelve la cantidad de secciones que que esten usando aulas en el bloque de horario

        Ej de un Bloque => Bloque: Lunes y Miércoles", "7:00", "8:30".
        Materia: Bases de datos Sec 1 => Aula 1
        Aulas ocupadas = 1  
        """
        contador = 0
        for s in self.secciones:
            if s.bloque == bloque and s.Status == StatusSeccion.Assignada:
                contador += 1
        return contador
    
    def Aula_abierta(self, bloque: Bloque) -> bool:
        """
        Funcion que devuelve un valor bool dependiendo de si todavia hay aulas disponibles en ese
        bloque de horario
        """
        return self.Aulas_ocupadas(bloque) < self.num_aulas
    
    def Disponibilidad_prof(self, profesor: Profesor, bloque: Bloque) -> bool:
        """
        Funcion que devuelve un valor bool si hay algun profesor disponible dentro de ese bloque de 
        horario
        """
        for s in self.secciones:
            if s.profesor == profesor and s.bloque == bloque and s.Status == StatusSeccion.Assignada:
                return False
        return True

    def Bloque_tiene_materia(self, bloque: Bloque, materia) -> bool:
        """
        Revisa si un bloque ya tiene una seccion de esa materia asignada.
        Se usa para no repetir la misma materia en el mismo bloque.
        Retorna True si ya hay una seccion de esa materia en el bloque.
        """
        for s in self.secciones:
            if s.bloque == bloque and s.materia == materia and s.Status == StatusSeccion.Assignada:
                return True
        return False

"""
 CLASE DEL SISTEMA
"""

class SistemaHorarios:
    """
    Clase principal que gestiona todo el sistema de horarios de clases.

    Atributos:
        profesores (list): Lista de objetos Profesor cargados en el sistema.
        materias (list): Lista de objetos Materia cargados en el sistema.
        bloques (list): Lista de objetos Bloque con los 14 bloques horarios fijos.
        horario (Horario | None): Objeto Horario generado, None si no se ha generado.

    Metodos principales:
        - Cargar datos desde GitHub o archivo CSV
        - Gestionar profesores (ver, agregar, eliminar, modificar materias)
        - Gestionar materias (ver, agregar, eliminar, modificar secciones)
        - Generar horarios asignando profesores, bloques y salones
        - Modificar la asignacion de horarios generada
        - Guardar y cargar horarios en formato CSV
    """
    def __init__(self):
        self.profesores = []
        self.materias = []
        # Crear la lista de bloques horarios a partir de los datos fijos
        # Recorre cada tupla de bloques_fijos y crea un objeto Bloque
        # Ejemplo: ("Lunes y Miércoles", "7:00", "8:30") se convierte en
        #          Bloque("Lunes y Miércoles", "7:00", "8:30")
        self.bloques = []
        for datos in bloques_fijos:
            bloque = Bloque(datos[0], datos[1], datos[2])
            self.bloques.append(bloque)
        self.horario = None

    """
    CARGA DE DATOS DESDE GITHUB
    """

    def Cargar_JSON(self, archivo: str):
        url = f"{BASE_url}/{archivo}"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        texto = r.text

        return json.loads(texto)
    
    def cargar_desde_github(self):
        """
        Funcion cuyo objetivo es descargar y cargar los datos necesarios del sistema desde el gihub
        """
        self.materias = []
        self.profesores = []
        self.horario = None
        profesores_raw = self.Cargar_JSON("profesores.json")

        print("\nSeleccione el archivo de materias a cargar:")
        print("1. materias2425-3.json")
        print("2. materias2526-1.json")
        print("3. materias2526-2.json")

        opcion = input("Opción: ").strip()

        if opcion == "1":
            archivo_materias = "materias2425-3.json"
        elif opcion == "2":
            archivo_materias = "materias2526-1.json"
        elif opcion == "3":
            archivo_materias = "materias2526-2.json"
        else:
            print("Opción inválida. No se cargaron las materias.")
            return

        materias_raw = self.Cargar_JSON(archivo_materias)

        # Crear materias
        for item in materias_raw:
            materia = Materia(
                codigo_mat=str(item.get("Código", "")).strip(),
                nombre_mat=str(item.get("Nombre", "")).strip(),
                secciones_requeridas=int(item.get("Secciones", 0))
            )
            self.materias.append(materia)

        # Mapa para enlazar materias por código
        mapa_materias = {m.codigo: m for m in self.materias}

        # Crear profesores
        for item in profesores_raw:
            nombre = f'{str(item.get("Nombre", "")).strip()} {str(item.get("Apellido", "")).strip()}'.strip()

            profesor = Profesor(
                nombre=nombre,
                cedula=str(item.get("Cedula", "")).strip(),
                email=str(item.get("Email", "")).strip(),
                max_materias=int(item.get("Max Carga", 0))
            )

            for codigo in item.get("Materias", []):
                codigo = str(codigo).strip()
                if codigo in mapa_materias:
                    profesor.List_materias.append(mapa_materias[codigo])

            self.profesores.append(profesor)

        print(f"Datos cargados correctamente desde GitHub usando {archivo_materias}.")

    """
    FUNCIONES DE BUSQUEDA
    """
    def buscar_materia(self, codigo: str): #Algoritmo de busqueda lineal simplificado
        """
        Busca una materia dentro de la lista de materias del sistema usando su codigo
        """
        for m in self.materias:
            if m.codigo == codigo:
                return m
        return None
            
    def buscar_profesor(self, cedula:str):
        """
        Busca un profesor usando su numero de cedula.
        """
        for p in self.profesores:
            if p.cedula == cedula:
                return p
        return None

    def contar_asignadas_profesor(self, profesor: Profesor) -> int:
        """
        Cuenta cuantas secciones tiene asigandas un profesor
        en el horario generado.
        """
        if self.horario is None:
            return 0 
        return len(self.horario.Get_secciones_por_prof(profesor))
    
    """
    VISTAS DE LAS LISTAS
    """
    def listar_materias(self):
        if not self.materias: #Revisar si la lista no esta vacia
            print("No hay materias")
            return
        for m in self.materias:
            print(m)

    def listar_profesores(self):
        if not self.profesores: # Revisar si la lista de profesores esta vacia
            print("No hay profesores.")
        for p in self.profesores:
            print(p)

    def mostrar_horarios_por_materia(self): 
        """ 
        Algoritmo de busqueda donde se itera por secciones
        """
        if self.horario is None: #Revisar si la lista de horarios tiene objetos
            print("No hay horario Disponible")
            return
        
        codigo = input("Codigo de la materia: ").strip()
        materia = self.buscar_materia(codigo)

        if materia is None:
            print("Materia no encontrada, Porfavor introducir un codigo Valido: ")
            return
        
        secciones = self.horario.Get_secciones_por_materia(materia)
        if not secciones:
            print("No hay secciones para esta materia")
            return
        
        for s in secciones:
            print(s)
    
    def mostrar_horario_por_profesor(self):
        """
        ALgoritmo de busqueda donde se itera por secciones buscando las que tengan el profesor buscado
        """
        if self.horario is None:
            print("No hay horario generado para ese profesor")
            return
        
        cedula = input("Introduzca cedula del profesor: ").strip()
        profesor = self.buscar_profesor(cedula)

        if profesor is None:
            print("Profesor no encontrado.")
            return
        secciones =self.horario.Get_secciones_por_prof(profesor)

        if not secciones:
            print("No hay secciones para este profesorr")
            return
        
        for s in secciones:
            print(s)

    def mostrar_bloques(self):
        """
        Recorre la lista de bloques de horario, Obtiene su indice usando enumerate(), 
        imprime cada bloque con su numero y horario
        """
        for i, bloque in enumerate(self.bloques):
            print(f"{i}. {bloque.Etiqueta()}")

    """
    FUNCIONES DEL MODULO DE PROFESORES
    """
    def ver_profesor_especifico(self):
        """
        Busca y muestra la informacion de un profesor especifico
        usando su numero de cedula.
        Complejidad: O(n) donde n es la cantidad de profesores.
        """
        if not self.profesores:
            print("No hay profesores cargados.")
            return

        cedula = input("Ingrese la cedula del profesor: ").strip()
        profesor = self.buscar_profesor(cedula)

        if profesor is None:
            print("Profesor no encontrado.")
            return

        print(profesor)

    def agregar_profesor(self):
        """
        Agrega un nuevo profesor a la lista del sistema.
        Solicita nombre, cedula, correo y maximo de materias por consola.
        Valida que la cedula no este repetida y que los datos sean validos.
        Complejidad: O(n) donde n es la cantidad de profesores (verificar cedula unica).
        """
        print("--- Agregar Profesor ---")

        # Solicitar el nombre completo del profesor
        nombre = input("Ingrese el nombre completo del profesor: ").strip()
        if nombre == "":
            print("Error: El nombre no puede estar vacio.")
            return

        # Solicitar la cedula del profesor
        cedula = input("Ingrese la cedula del profesor: ").strip()
        if cedula == "":
            print("Error: La cedula no puede estar vacia.")
            return

        # Verificar que la cedula no este repetida en la lista de profesores
        profesor_existente = self.buscar_profesor(cedula)
        if profesor_existente is not None:
            print(f"Error: Ya existe un profesor con la cedula {cedula}.")
            return

        # Solicitar el correo electronico del profesor
        email = input("Ingrese el correo del profesor: ").strip()
        if email == "":
            print("Error: El correo no puede estar vacio.")
            return

        # Solicitar el numero maximo de materias que puede dar
        try:
            max_materias = int(input("Ingrese el numero maximo de materias: ").strip())
            if max_materias <= 0:
                print("Error: El numero debe ser mayor a 0.")
                return
        except ValueError:
            print("Error: Debe ingresar un numero valido.")
            return

        # CREAR EL OBJETO PROFESOR CON LOS DATOS INGRESADOS
        nuevo_profesor = Profesor(
            nombre=nombre,
            cedula=cedula,
            email=email,
            max_materias=max_materias
        )

        # Preguntar si desea asignarle materias al profesor
        asignar = input("Desea asignar materias a este profesor? (s/n): ").strip().lower()
        if asignar == "s":
            # Verificar que haya materias cargadas
            if not self.materias:
                print("No hay materias cargadas en el sistema.")
            else:
                # Mostrar la lista de materias disponibles con su indice
                print("\nMaterias disponibles:")
                for i in range(len(self.materias)):
                    print(f"  {i + 1}. {self.materias[i]}")

                # Solicitar los codigos separados por coma
                print("\nIngrese los codigos de las materias separados por coma")
                print("Ejemplo: MAT101, FIS201")
                codigos_input = input("Codigos: ").strip()

                if codigos_input != "":
                    # Separar los codigos ingresados por coma
                    lista_codigos = codigos_input.split(",")

                    # Recorrer cada codigo y buscar la materia correspondiente
                    for codigo in lista_codigos:
                        codigo = codigo.strip()
                        materia = self.buscar_materia(codigo)
                        if materia is not None:
                            nuevo_profesor.List_materias.append(materia)
                            print(f"  Materia {codigo} asignada correctamente.")
                        else:
                            print(f"  Materia {codigo} no encontrada, se omite.")

        # Agregar el profesor a la lista del sistema
        self.profesores.append(nuevo_profesor)
        print(f"\nProfesor {nombre} agregado correctamente.")

    def eliminar_profesor(self):
        """
        Elimina un profesor de la lista del sistema.
        Antes de eliminar, revisa si alguna materia quedaria sin profesores.
        Si es asi, muestra advertencia y pide confirmacion al usuario.
        Complejidad: O(n * m) donde n es profesores y m es materias del profesor.
        """
        print("--- Eliminar Profesor ---")

        # Verificar que haya profesores en el sistema
        if not self.profesores:
            print("No hay profesores en el sistema.")
            return

        # Solicitar la cedula del profesor a eliminar
        cedula = input("Ingrese la cedula del profesor a eliminar: ").strip()
        profesor = self.buscar_profesor(cedula)

        # Verificar que el profesor exista
        if profesor is None:
            print("Profesor no encontrado.")
            return

        # Mostrar los datos del profesor encontrado
        print(f"\nProfesor encontrado: {profesor}")

        # Revisar si alguna materia del profesor quedara sin profesores disponibles
        # Recorremos cada materia que el profesor puede dar
        materias_en_riesgo = []
        for materia in profesor.List_materias:
            # Contar cuantos profesores en total pueden dar esta materia
            contador = 0
            for p in self.profesores:
                if materia in p.List_materias:
                    contador = contador + 1

            # Si solo este profesor la puede dar, la materia queda en riesgo
            if contador <= 1:
                materias_en_riesgo.append(materia)

        # Si hay materias en riesgo, mostrar advertencia al usuario
        if len(materias_en_riesgo) > 0:
            print("\n*** ADVERTENCIA ***")
            print("Las siguientes materias quedaran SIN profesor disponible:")
            for m in materias_en_riesgo:
                print(f"  - {m}")

        # Pedir confirmacion antes de eliminar
        confirmacion = input("\nDesea eliminar este profesor? (s/n): ").strip().lower()
        if confirmacion != "s":
            print("Operacion cancelada.")
            return

        # Eliminar el profesor de la lista del sistema
        self.profesores.remove(profesor)
        print(f"Profesor {profesor.nombre} eliminado correctamente.")

    def modificar_materias_profesor(self):
        """
        Permite agregar o quitar materias de la lista de un profesor.
        Si al quitar una materia esta queda sin profesores disponibles,
        muestra advertencia y pide confirmacion al usuario.
        Complejidad: O(n) donde n es la cantidad de materias del profesor.
        """
        print("--- Modificar Materias de Profesor ---")

        # Verificar que haya profesores en el sistema
        if not self.profesores:
            print("No hay profesores en el sistema.")
            return

        # Solicitar la cedula del profesor a modificar
        cedula = input("Ingrese la cedula del profesor: ").strip()
        profesor = self.buscar_profesor(cedula)

        # Verificar que el profesor exista
        if profesor is None:
            print("Profesor no encontrado.")
            return

        # Mostrar los datos del profesor y sus materias actuales
        print(f"\nProfesor: {profesor}")
        print("\nMaterias actuales:")
        if not profesor.List_materias:
            print("  (Ninguna)")
        else:
            # Recorrer la lista de materias del profesor con su indice
            for i in range(len(profesor.List_materias)):
                print(f"  {i + 1}. {profesor.List_materias[i]}")

        # Mostrar opciones de modificacion
        print("\n1. Agregar una materia")
        print("2. Quitar una materia")
        print("0. Cancelar")

        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            # --- AGREGAR MATERIA AL PROFESOR ---
            if profesor.max_materias <= len(profesor.List_materias):
                print("El profesor ya tiene asignado el numero maximo de materias.")
                return

            # Verificar que haya materias en el sistema
            if not self.materias:
                print("No hay materias cargadas en el sistema.")
                return

            # Filtrar las materias que el profesor NO tiene asignadas todavia
            materias_disponibles = []
            for materia in self.materias:
                if materia not in profesor.List_materias:
                    materias_disponibles.append(materia)

            # Verificar que haya materias por asignar
            if not materias_disponibles:
                print("El profesor ya tiene todas las materias asignadas.")
                return

            # Mostrar las materias disponibles para agregar
            print("\nMaterias disponibles para agregar:")
            for i in range(len(materias_disponibles)):
                print(f"  {i + 1}. {materias_disponibles[i]}")

            # Solicitar el codigo de la materia a agregar
            codigo = input("\nIngrese el codigo de la materia a agregar: ").strip()
            materia = self.buscar_materia(codigo)

            # Validar que la materia exista
            if materia is None:
                print("Materia no encontrada.")
                return

            # Validar que no la tenga ya asignada
            if materia in profesor.List_materias:
                print("El profesor ya tiene esta materia asignada.")
                return

            # Agregar la materia a la lista del profesor
            profesor.List_materias.append(materia)
            print(f"Materia {materia.codigo} agregada al profesor {profesor.nombre}.")

        elif opcion == "2":
            # --- QUITAR MATERIA DEL PROFESOR ---

            # Verificar que el profesor tenga materias asignadas
            if not profesor.List_materias:
                print("El profesor no tiene materias asignadas.")
                return

            # Solicitar el codigo de la materia a quitar
            codigo = input("\nIngrese el codigo de la materia a quitar: ").strip()

            # Buscar la materia dentro de la lista del profesor
            materia_encontrada = None
            for materia in profesor.List_materias:
                if materia.codigo == codigo:
                    materia_encontrada = materia
                    break

            # Verificar que la materia este en la lista del profesor
            if materia_encontrada is None:
                print("El profesor no tiene esa materia asignada.")
                return

            # Contar cuantos profesores pueden dar esta materia
            contador = 0
            for p in self.profesores:
                if materia_encontrada in p.List_materias:
                    contador = contador + 1

            # Si solo este profesor la da, mostrar advertencia
            if contador <= 1:
                print("\n*** ADVERTENCIA ***")
                print(f"La materia {materia_encontrada} quedara SIN profesor disponible.")
                confirmacion = input("Desea continuar? (s/n): ").strip().lower()
                if confirmacion != "s":
                    print("Operacion cancelada.")
                    return

            # Quitar la materia de la lista del profesor
            profesor.List_materias.remove(materia_encontrada)
            print(f"Materia {materia_encontrada.codigo} removida del profesor {profesor.nombre}.")

        elif opcion == "0":
            print("Operacion cancelada.")

        else:
            print("Opcion invalida.")

    """
    FUNCIONES DEL MODULO DE MATERIAS
    """
    def ver_detalle_materia(self):
        """
        Muestra los detalles de una materia especifica
        buscandola por su codigo.
        Complejidad: O(n) donde n es la cantidad de materias.
        """
        if not self.materias:
            print("No hay materias cargadas.")
            return

        codigo = input("Ingrese el codigo de la materia: ").strip()
        materia = self.buscar_materia(codigo)

        if materia is None:
            print("Materia no encontrada.")
            return

        print(materia)

    def ver_profesores_materia(self):
        """
        Muestra los profesores que pueden dar una materia especifica.
        Recorre la lista de profesores verificando si tienen la materia asignada.
        Complejidad: O(p * m) donde p es profesores y m es materias por profesor.
        """
        if not self.materias:
            print("No hay materias cargadas.")
            return

        codigo = input("Ingrese el codigo de la materia: ").strip()
        materia = self.buscar_materia(codigo)

        if materia is None:
            print("Materia no encontrada.")
            return

        # Recorrer la lista de profesores buscando quienes pueden dar esta materia
        encontrados = []
        for profesor in self.profesores:
            # Verificar si la materia esta en la lista del profesor
            if materia in profesor.List_materias:
                encontrados.append(profesor)

        if not encontrados:
            print("No hay profesores asociados a esta materia.")
            return

        # Mostrar cada profesor encontrado
        for p in encontrados:
            print(p)

    def agregar_materia(self):
        """
        Agrega una nueva materia a la lista del sistema.
        Solicita codigo, nombre y numero de secciones por consola.
        Valida que el codigo no este repetido y que las secciones sean un numero valido.
        Complejidad: O(n) donde n es la cantidad de materias (verificar codigo unico).
        """
        print("--- Agregar Materia ---")

        # Solicitar el codigo de la materia
        codigo = input("Ingrese el codigo de la materia: ").strip()
        if codigo == "":
            print("Error: El codigo no puede estar vacio.")
            return

        # Verificar que el codigo no este repetido en la lista de materias
        materia_existente = self.buscar_materia(codigo)
        if materia_existente is not None:
            print(f"Error: Ya existe una materia con el codigo {codigo}.")
            return

        # Solicitar el nombre de la materia
        nombre = input("Ingrese el nombre de la materia: ").strip()
        if nombre == "":
            print("Error: El nombre no puede estar vacio.")
            return

        # Solicitar el numero de secciones requeridas
        try:
            secciones = int(input("Ingrese el numero de secciones requeridas: ").strip())
            # Validar que no sea un numero negativo
            if secciones < 0:
                print("Error: El numero de secciones no puede ser negativo.")
                return
        except ValueError:
            print("Error: Debe ingresar un numero valido.")
            return

        # Si el usuario ingresa 0 secciones, advertir que la materia no se ofertara
        if secciones == 0:
            print("\n*** ADVERTENCIA ***")
            print("Con 0 secciones, esta materia NO se ofertara en el trimestre.")
            confirmacion = input("Desea continuar? (s/n): ").strip().lower()
            if confirmacion != "s":
                print("Operacion cancelada.")
                return

        # Crear el nuevo objeto Materia con los datos ingresados
        nueva_materia = Materia(
            codigo_mat=codigo,
            nombre_mat=nombre,
            secciones_requeridas=secciones
        )

        # Agregar la materia a la lista del sistema
        self.materias.append(nueva_materia)
        print(f"\nMateria {codigo} - {nombre} agregada correctamente.")

    def eliminar_materia(self):
        """
        Elimina una materia de la lista del sistema.
        Tambien la elimina de la lista de todos los profesores que la tengan.
        Si al eliminarla un profesor queda sin materias, muestra advertencia
        y pide confirmacion al usuario antes de proceder.
        Complejidad: O(n * m) donde n es profesores y m es materias por profesor.
        """
        print("--- Eliminar Materia ---")

        # Verificar que haya materias en el sistema
        if not self.materias:
            print("No hay materias en el sistema.")
            return

        # Solicitar el codigo de la materia a eliminar
        codigo = input("Ingrese el codigo de la materia a eliminar: ").strip()
        materia = self.buscar_materia(codigo)

        # Verificar que la materia exista
        if materia is None:
            print("Materia no encontrada.")
            return

        # Mostrar los datos de la materia encontrada
        print(f"\nMateria encontrada: {materia}")

        # Buscar que profesores tienen esta materia en su lista
        profesores_afectados = []
        for profesor in self.profesores:
            if materia in profesor.List_materias:
                profesores_afectados.append(profesor)

        # Revisar cuales profesores quedarian sin materias si se elimina esta
        profesores_sin_materias = []
        for profesor in profesores_afectados:
            # Si el profesor solo tiene esta materia, quedaria sin ninguna
            if len(profesor.List_materias) <= 1:
                profesores_sin_materias.append(profesor)

        # Si hay profesores que quedarian sin materias, mostrar advertencia
        if len(profesores_sin_materias) > 0:
            print("\n*** ADVERTENCIA ***")
            print("Los siguientes profesores quedaran SIN materias asignadas:")
            for p in profesores_sin_materias:
                print(f"  - {p.nombre} (Cedula: {p.cedula})")

        # Pedir confirmacion antes de eliminar
        confirmacion = input("\nDesea eliminar esta materia? (s/n): ").strip().lower()
        if confirmacion != "s":
            print("Operacion cancelada.")
            return

        # Eliminar la materia de la lista de cada profesor que la tenga
        for profesor in profesores_afectados:
            profesor.List_materias.remove(materia)

        # Eliminar la materia de la lista del sistema
        self.materias.remove(materia)
        print(f"Materia {codigo} eliminada correctamente.")

    def modificar_secciones_materia(self):
        """
        Modifica el numero de secciones requeridas de una materia.
        Si el nuevo valor es cero, muestra advertencia indicando que la materia
        no se ofertara en el trimestre y pide confirmacion al usuario.
        Complejidad: O(n) donde n es la cantidad de materias (busqueda lineal).
        """
        print("--- Modificar Secciones ---")

        # Verificar que haya materias en el sistema
        if not self.materias:
            print("No hay materias en el sistema.")
            return

        # Solicitar el codigo de la materia a modificar
        codigo = input("Ingrese el codigo de la materia: ").strip()
        materia = self.buscar_materia(codigo)

        # Verificar que la materia exista
        if materia is None:
            print("Materia no encontrada.")
            return

        # Mostrar los datos actuales de la materia
        print(f"\nMateria: {materia}")
        print(f"Secciones actuales: {materia.secciones_requeridas}")

        # Solicitar el nuevo numero de secciones
        try:
            nuevas_secciones = int(input("Ingrese el nuevo numero de secciones: ").strip())
            # Validar que no sea un numero negativo
            if nuevas_secciones < 0:
                print("Error: El numero de secciones no puede ser negativo.")
                return
        except ValueError:
            print("Error: Debe ingresar un numero valido.")
            return

        # Si el nuevo valor es 0, advertir que la materia no se ofertara
        if nuevas_secciones == 0:
            print("\n*** ADVERTENCIA ***")
            print("Con 0 secciones, esta materia NO se ofertara en el trimestre.")
            confirmacion = input("Desea continuar? (s/n): ").strip().lower()
            if confirmacion != "s":
                print("Operacion cancelada.")
                return

        # Actualizar el numero de secciones de la materia
        materia.secciones_requeridas = nuevas_secciones
        print(f"Secciones de {materia.codigo} actualizadas a {nuevas_secciones}.")

    """
    GENERAR LOS HORARIOS
    """
    def generar_horarios(self):
        """
        Genera la asignacion de horarios para todas las materias.
        Recorre la lista de materias en orden, asignando a cada seccion
        un bloque horario y un profesor disponible.

        Logica de asignacion:
        1. Para cada seccion, buscar un bloque con aula disponible (forma circular)
        2. Si no hay bloque sin esa materia, usar cualquier bloque con aula libre
        3. Si no hay aulas libres en ningun bloque, marcar seccion como sin asignar
        4. Buscar un profesor que pueda dar la materia y este libre en ese bloque
        5. Si no hay profesor directo, intentar reasignar secciones de otro profesor
        6. Si no se puede reasignar, marcar la seccion como cerrada sin profesor

        Al finalizar muestra un reporte con:
        - Materias con secciones cerradas por falta de profesores
        - Materias con secciones sin aula disponible
        - Bloques horarios con salones aun disponibles

        Complejidad: O(m * s * b * p) donde m=materias, s=secciones, b=bloques, p=profesores.
        """
        if not self.materias:
            print("No hay materias cargadas")
            return

        # Solicitar el numero de aulas disponibles al usuario
        try:
            num_aulas = int(input("Inserte numero de aulas disponibles: ").strip())
            if num_aulas <= 0:
                print("Inserte un numero mayor a 0.")
                return
        except ValueError:
            print("Numero invalido")
            return

        # Crear un nuevo objeto Horario con la cantidad de aulas
        self.horario = Horario(num_aulas)

        # Limpiar las secciones previas de cada materia
        for materia in self.materias:
            materia.secciones = []

        # Indice del bloque actual, se avanza de forma circular
        bloque_actual = 0

        # Recorrer cada materia en orden
        for materia in self.materias:
            # Si la materia no tiene secciones requeridas, saltarla
            if not materia.Esta_abierta():
                continue

            # Recorrer cada seccion que necesita esta materia
            for num_sec in range(1, materia.secciones_requeridas + 1):
                # Crear una nueva seccion con su numero
                seccion = Seccion(num_sec)
                seccion.materia = materia

                bloque_elegido = None

                # --- PASO 1: Buscar bloque con aula disponible que NO tenga esta materia ---
                # Crear lista reordenada empezando desde bloque_actual (recorrido circular)
                # Esto distribuye las secciones de distintas materias en bloques diferentes
                bloques_reordenados = self.bloques[bloque_actual:] + self.bloques[:bloque_actual]

                # Primero buscar un bloque que tenga aula libre Y que no tenga
                # ya una seccion de esta misma materia (para no repetir)
                for candidato in bloques_reordenados:
                    if not self.horario.Aula_abierta(candidato):
                        continue  # No hay aula libre, saltar
                    if self.horario.Bloque_tiene_materia(candidato, materia):
                        continue  # Ya tiene esta materia, saltar
                    bloque_elegido = candidato
                    break

                # --- PASO 2: Si no hay bloque sin esta materia, usar cualquiera con aula ---
                # Esto pasa cuando todos los bloques con aula ya tienen esta materia
                if bloque_elegido is None:
                    for candidato in bloques_reordenados:
                        if self.horario.Aula_abierta(candidato):
                            bloque_elegido = candidato
                            break

                # --- PASO 3: Si no hay aula libre en ningun bloque ---
                if bloque_elegido is None:
                    seccion.Marcar_no_Materia()
                    materia.secciones.append(seccion)
                    self.horario.secciones.append(seccion)
                    continue

                # --- PASO 4: Buscar profesor disponible para este bloque ---
                profesor_elegido = None
                for profesor in self.profesores:
                    # Verificar que el profesor pueda dar esta materia
                    if not profesor.Puede_dar_materia(materia):
                        continue
                    # Verificar que no haya alcanzado su maximo de materias
                    if not profesor.Puede_Enseñar_Mas(self.contar_asignadas_profesor(profesor)):
                        continue
                    # Verificar que este libre en el bloque elegido
                    if not self.horario.Disponibilidad_prof(profesor, bloque_elegido):
                        continue

                    profesor_elegido = profesor
                    break

                # --- PASO 5: Si no hay profesor directo, intentar reasignar ---
                # Buscar profesores que PUEDEN dar esta materia pero estan al maximo
                # e intentar liberar una de sus secciones reasignandola a otro profesor
                if profesor_elegido is None:
                    for prof_lleno in self.profesores:
                        # Debe poder dar esta materia
                        if not prof_lleno.Puede_dar_materia(materia):
                            continue
                        # Debe estar libre en este bloque horario
                        if not self.horario.Disponibilidad_prof(prof_lleno, bloque_elegido):
                            continue
                        # Solo considerar profesores que estan al maximo de carga
                        asignadas_prof = self.contar_asignadas_profesor(prof_lleno)
                        if asignadas_prof < prof_lleno.max_materias:
                            continue

                        # Obtener las secciones actualmente asignadas a este profesor
                        secciones_del_prof = self.horario.Get_secciones_por_prof(prof_lleno)

                        reasignado = False
                        # Intentar reasignar cada una de sus secciones a otro profesor
                        for sec_existente in secciones_del_prof:
                            # Buscar un profesor de reemplazo para esa seccion
                            for prof_reemplazo in self.profesores:
                                # No puede ser el mismo profesor
                                if prof_reemplazo == prof_lleno:
                                    continue
                                # Debe poder dar la materia de la seccion existente
                                if not prof_reemplazo.Puede_dar_materia(sec_existente.materia):
                                    continue
                                # Debe tener espacio para mas materias
                                if not prof_reemplazo.Puede_Enseñar_Mas(self.contar_asignadas_profesor(prof_reemplazo)):
                                    continue
                                # Debe estar libre en el bloque de la seccion existente
                                if not self.horario.Disponibilidad_prof(prof_reemplazo, sec_existente.bloque):
                                    continue

                                # Reasignar: la seccion existente pasa al profesor de reemplazo
                                sec_existente.Asig_prof(prof_reemplazo)
                                # Ahora prof_lleno tiene una vacante
                                profesor_elegido = prof_lleno
                                reasignado = True
                                break

                            # Si ya se logro reasignar, salir del ciclo
                            if reasignado:
                                break

                        # Si se encontro un profesor mediante reasignacion, salir
                        if reasignado:
                            break

                # --- PASO 6: Si aun no hay profesor, marcar como cerrada ---
                if profesor_elegido is None:
                    seccion.Marcar_no_Prof()
                    materia.secciones.append(seccion)
                    self.horario.secciones.append(seccion)
                    continue

                # --- PASO 7: Asignar profesor, bloque y salon a la seccion ---
                seccion.Asig_prof(profesor_elegido)
                seccion.Asig_Bloque(bloque_elegido)
                seccion.id_salon = self.horario.Aulas_ocupadas(bloque_elegido) + 1
                seccion.Status = StatusSeccion.Assignada

                materia.secciones.append(seccion)
                self.horario.secciones.append(seccion)

                # Avanzar al siguiente bloque para la proxima seccion
                bloque_actual = (self.bloques.index(bloque_elegido) + 1) % len(self.bloques)

        # --- REPORTE POST-GENERACION ---
        print("\n" + "=" * 50)
        print("   REPORTE DE GENERACION DE HORARIO")
        print("=" * 50)

        # 1. Materias con secciones cerradas por falta de profesores
        print("\n--- Secciones cerradas por falta de profesores ---")
        hay_cerradas_prof = False
        for materia in self.materias:
            # Contar cuantas secciones de esta materia fueron cerradas
            contador = 0
            for s in materia.secciones:
                if s.Status == StatusSeccion.Cerrada_no_prof:
                    contador = contador + 1
            if contador > 0:
                print(f"  {materia.codigo} - {materia.nombre_mat}: {contador} seccion(es)")
                hay_cerradas_prof = True
        if not hay_cerradas_prof:
            print("  Ninguna")

        # 2. Materias con secciones sin asignar por falta de salones
        print("\n--- Secciones sin asignar por falta de salones ---")
        hay_sin_salon = False
        for materia in self.materias:
            # Contar cuantas secciones no se pudieron asignar por falta de aulas
            contador = 0
            for s in materia.secciones:
                if s.Status == StatusSeccion.sin_asignar_clase:
                    contador = contador + 1
            if contador > 0:
                print(f"  {materia.codigo} - {materia.nombre_mat}: {contador} seccion(es)")
                hay_sin_salon = True
        if not hay_sin_salon:
            print("  Ninguna")

        # 3. Bloques horarios con salones disponibles
        print("\n--- Bloques con salones disponibles ---")
        hay_bloques_libres = False
        for bloque in self.bloques:
            ocupadas = self.horario.Aulas_ocupadas(bloque)
            disponibles = num_aulas - ocupadas
            if disponibles > 0:
                print(f"  {bloque.Etiqueta()}: {disponibles} salon(es) disponible(s)")
                hay_bloques_libres = True
        if not hay_bloques_libres:
            print("  Ninguno")

        print("\n" + "=" * 50)
        print("Horario generado correctamente.")


    """
    FUNCIONES POST-GENERACION DE HORARIO
    """
    def crear_listas_en_blanco(self):
        """
        Inicializa las listas de profesores y materias como listas vacias.
        Tambien limpia cualquier horario generado previamente.
        """
        self.profesores = []
        self.materias = []
        self.horario = None
        print("Listas creadas en blanco correctamente.")

    def ver_salones_por_hora(self):
        """
        Permite al usuario seleccionar un bloque horario y ver que secciones
        estan asignadas en cada salon durante ese bloque.
        Muestra materia, seccion, profesor y numero de aula.
        Complejidad: O(b + s) donde b=bloques y s=secciones del horario.
        """
        if self.horario is None:
            print("No hay horario generado.")
            return

        # Mostrar los bloques disponibles para que el usuario seleccione
        print("\nBloques horarios disponibles:")
        for i in range(len(self.bloques)):
            print(f"  {i + 1}. {self.bloques[i].Etiqueta()}")

        # Solicitar que bloque desea consultar
        try:
            seleccion = int(input("\nSeleccione un bloque (numero): ").strip())
            if seleccion < 1 or seleccion > len(self.bloques):
                print("Numero fuera de rango.")
                return
        except ValueError:
            print("Debe ingresar un numero valido.")
            return

        # Obtener el bloque seleccionado
        bloque = self.bloques[seleccion - 1]

        # Buscar las secciones asignadas en este bloque
        secciones_bloque = []
        for s in self.horario.secciones:
            if s.bloque == bloque and s.Status == StatusSeccion.Assignada:
                secciones_bloque.append(s)

        # Verificar si hay secciones en este bloque
        if not secciones_bloque:
            print(f"\nNo hay secciones asignadas en {bloque.Etiqueta()}")
            return

        # Mostrar las secciones ordenadas por numero de aula
        print(f"\n--- Salones en {bloque.Etiqueta()} ---")
        print(f"Ocupados: {len(secciones_bloque)} de {self.horario.num_aulas}")
        disponibles = self.horario.num_aulas - len(secciones_bloque)
        print(f"Disponibles: {disponibles}")
        print()

        # Recorrer cada seccion del bloque y mostrar su informacion
        for s in secciones_bloque:
            nombre_prof = s.profesor.nombre if s.profesor else "N/A"
            print(f"  Aula {s.id_salon}: {s.materia.codigo} - {s.materia.nombre_mat} "
                  f"| Sec {s.NumSeccion} | Prof: {nombre_prof}")

    def guardar_csv(self):
        """
        Guarda la asignacion de horarios generada en un archivo CSV.
        El archivo puede abrirse con Excel para visualizacion rapida
        y tambien puede cargarse luego para continuar modificando.
        Formato: primera fila contiene el numero de aulas, segunda fila
        los encabezados, y las siguientes filas los datos de cada seccion.
        Complejidad: O(n) donde n es el numero de secciones del horario.
        """
        if self.horario is None:
            print("No hay horario generado para guardar.")
            return

        # Solicitar el nombre del archivo al usuario
        nombre_archivo = input("Ingrese el nombre del archivo (sin extension): ").strip()
        if nombre_archivo == "":
            print("Error: El nombre no puede estar vacio.")
            return

        # Agregar la extension .csv al nombre
        nombre_archivo = nombre_archivo + ".csv"

        try:
            # Abrir el archivo para escritura
            archivo = open(nombre_archivo, "w", newline="", encoding="utf-8")
            escritor = csv.writer(archivo)

            # Escribir el numero de aulas como primera fila (metadato)
            escritor.writerow(["num_aulas", str(self.horario.num_aulas)])

            # Escribir la fila de encabezados
            encabezados = [
                "Codigo_Materia", "Nombre_Materia", "Num_Seccion",
                "Cedula_Profesor", "Nombre_Profesor",
                "Dias", "Hora_Inicio", "Hora_Fin",
                "Aula", "Estado"
            ]
            escritor.writerow(encabezados)

            # Recorrer cada seccion del horario y escribir una fila
            for seccion in self.horario.secciones:
                # Obtener los datos de la materia
                codigo_mat = ""
                nombre_mat = ""
                if seccion.materia is not None:
                    codigo_mat = seccion.materia.codigo
                    nombre_mat = seccion.materia.nombre_mat

                # Obtener los datos del profesor
                cedula_prof = ""
                nombre_prof = ""
                if seccion.profesor is not None:
                    cedula_prof = seccion.profesor.cedula
                    nombre_prof = seccion.profesor.nombre

                # Obtener los datos del bloque horario
                dias = ""
                hora_inicio = ""
                hora_fin = ""
                if seccion.bloque is not None:
                    dias = seccion.bloque.Dias_disp
                    hora_inicio = seccion.bloque.Hora_init.strftime("%H:%M")
                    hora_fin = seccion.bloque.Hora_fin.strftime("%H:%M")

                # Obtener aula y estado
                aula = ""
                if seccion.id_salon is not None:
                    aula = seccion.id_salon
                estado = seccion.Status

                # Construir la fila con todos los datos
                fila = [
                    codigo_mat, nombre_mat, seccion.NumSeccion,
                    cedula_prof, nombre_prof,
                    dias, hora_inicio, hora_fin,
                    aula, estado
                ]
                escritor.writerow(fila)

            # Cerrar el archivo
            archivo.close()
            print(f"\nHorario guardado correctamente en '{nombre_archivo}'.")

        except Exception as e:
            print(f"Error al guardar el archivo: {e}")

    def cargar_csv(self):
        """
        Carga un horario previamente guardado desde un archivo CSV.
        Reconstruye las materias, profesores basicos y el horario
        a partir de los datos del archivo.
        Permite continuar una modificacion que fue pausada anteriormente.
        Complejidad: O(n * b) donde n=filas del CSV y b=bloques horarios.
        """
        print("--- Cargar desde CSV ---")

        # Solicitar el nombre del archivo al usuario
        nombre_archivo = input("Ingrese el nombre del archivo (con extension .csv): ").strip()
        if nombre_archivo == "":
            print("Error: El nombre no puede estar vacio.")
            return

        try:
            # Abrir el archivo para lectura
            archivo = open(nombre_archivo, "r", encoding="utf-8")
            lector = csv.reader(archivo)

            # Leer la primera fila para obtener el numero de aulas
            primera_fila = next(lector)
            if primera_fila[0] != "num_aulas":
                print("Error: El archivo no tiene el formato esperado.")
                archivo.close()
                return

            num_aulas = int(primera_fila[1])

            # Leer la fila de encabezados (se salta, no se usa)
            next(lector)

            # Crear el horario nuevo con el numero de aulas del archivo
            self.horario = Horario(num_aulas)
            self.materias = []
            self.profesores = []

            # Diccionarios para evitar duplicados al reconstruir objetos
            mapa_materias = {}
            mapa_profesores = {}

            # Leer cada fila de datos del CSV
            for fila in lector:
                # Verificar que la fila tenga suficientes columnas
                if len(fila) < 10:
                    continue

                # Extraer los datos de cada columna
                codigo_mat = fila[0].strip()
                nombre_mat = fila[1].strip()
                num_seccion = int(fila[2])
                cedula_prof = fila[3].strip()
                nombre_prof = fila[4].strip()
                dias = fila[5].strip()
                hora_inicio = fila[6].strip()
                hora_fin = fila[7].strip()
                aula = fila[8].strip()
                estado = fila[9].strip()

                # Reconstruir la materia si no existe aun en el mapa
                materia_obj = None
                if codigo_mat != "":
                    if codigo_mat not in mapa_materias:
                        materia_obj = Materia(codigo_mat, nombre_mat, 0)
                        mapa_materias[codigo_mat] = materia_obj
                        self.materias.append(materia_obj)
                    else:
                        materia_obj = mapa_materias[codigo_mat]

                    # Incrementar el contador de secciones requeridas
                    materia_obj.secciones_requeridas = materia_obj.secciones_requeridas + 1

                # Reconstruir el profesor si no existe aun en el mapa
                profesor_obj = None
                if cedula_prof != "":
                    if cedula_prof not in mapa_profesores:
                        profesor_obj = Profesor(nombre_prof, cedula_prof, "", 0)
                        mapa_profesores[cedula_prof] = profesor_obj
                        self.profesores.append(profesor_obj)
                    else:
                        profesor_obj = mapa_profesores[cedula_prof]

                    # Asociar la materia al profesor si no la tiene
                    if materia_obj is not None:
                        if materia_obj not in profesor_obj.List_materias:
                            profesor_obj.List_materias.append(materia_obj)

                # Crear la seccion con los datos leidos
                seccion = Seccion(num_seccion)
                seccion.materia = materia_obj
                seccion.Status = estado

                # Asignar profesor si existe
                if profesor_obj is not None:
                    seccion.Asig_prof(profesor_obj)

                # Buscar el bloque horario correspondiente
                if dias != "" and hora_inicio != "" and hora_fin != "":
                    bloque_encontrado = None
                    for bloque in self.bloques:
                        bloque_dias = bloque.Dias_disp
                        bloque_inicio = bloque.Hora_init.strftime("%H:%M")
                        bloque_final = bloque.Hora_fin.strftime("%H:%M")
                        # Comparar dias y horas para encontrar el bloque correcto
                        if bloque_dias == dias and bloque_inicio == hora_inicio and bloque_final == hora_fin:
                            bloque_encontrado = bloque
                            break

                    if bloque_encontrado is not None:
                        seccion.Asig_Bloque(bloque_encontrado)

                # Asignar el numero de aula
                if aula != "":
                    seccion.id_salon = int(aula)

                # Agregar la seccion al horario y a la materia
                self.horario.secciones.append(seccion)
                if materia_obj is not None:
                    materia_obj.secciones.append(seccion)

            # Cerrar el archivo
            archivo.close()

            # Calcular el max_materias de cada profesor segun las secciones cargadas
            for prof in self.profesores:
                contador = 0
                for s in self.horario.secciones:
                    if s.profesor == prof and s.Status == StatusSeccion.Assignada:
                        contador = contador + 1
                prof.max_materias = contador

            print(f"\nHorario cargado correctamente desde '{nombre_archivo}'.")
            print(f"Materias: {len(self.materias)} | Profesores: {len(self.profesores)} "
                  f"| Secciones: {len(self.horario.secciones)}")

        except FileNotFoundError:
            print(f"Error: No se encontro el archivo '{nombre_archivo}'.")
        except Exception as e:
            print(f"Error al cargar el archivo: {e}")

    def modificar_horario(self):
        """
        Permite modificar la asignacion de una seccion del horario.
        El usuario debe:
        1. Seleccionar una materia por codigo
        2. Seleccionar una seccion de esa materia
        3. Elegir entre cambiar el profesor o cambiar el bloque horario

        Al cambiar profesor: muestra profesores disponibles para esa materia y bloque.
        Al cambiar bloque: muestra bloques con salones libres y luego profesores disponibles.
        Complejidad: O(s + p + b) donde s=secciones, p=profesores, b=bloques.
        """
        if self.horario is None:
            print("No hay horario generado.")
            return

        # --- PASO 1: Seleccionar materia ---
        print("--- Modificar Horario ---")
        codigo = input("Ingrese el codigo de la materia: ").strip()
        materia = self.buscar_materia(codigo)

        if materia is None:
            print("Materia no encontrada.")
            return

        # Obtener las secciones de esta materia en el horario
        secciones = self.horario.Get_secciones_por_materia(materia)
        if not secciones:
            print("No hay secciones para esta materia en el horario.")
            return

        # --- PASO 2: Seleccionar seccion ---
        print(f"\nSecciones de {materia.codigo} - {materia.nombre_mat}:")
        for i in range(len(secciones)):
            print(f"  {i + 1}. {secciones[i]}")

        try:
            seleccion = int(input("\nSeleccione una seccion (numero): ").strip())
            if seleccion < 1 or seleccion > len(secciones):
                print("Numero fuera de rango.")
                return
        except ValueError:
            print("Debe ingresar un numero valido.")
            return

        seccion = secciones[seleccion - 1]

        # --- PASO 3: Seleccionar tipo de modificacion ---
        print(f"\nSeccion seleccionada: {seccion}")
        print("\n1. Cambiar el profesor")
        print("2. Cambiar el bloque horario")
        print("0. Cancelar")

        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            # --- CAMBIAR PROFESOR ---
            # Buscar profesores disponibles para esta materia en el bloque actual
            profesores_disponibles = []
            for profesor in self.profesores:
                # Debe poder dar esta materia
                if not profesor.Puede_dar_materia(materia):
                    continue
                # No mostrar el profesor que ya esta asignado
                if profesor == seccion.profesor:
                    continue
                # Debe tener espacio para mas materias
                if not profesor.Puede_Enseñar_Mas(self.contar_asignadas_profesor(profesor)):
                    continue
                # Si la seccion tiene bloque, debe estar libre en ese bloque
                if seccion.bloque is not None:
                    if not self.horario.Disponibilidad_prof(profesor, seccion.bloque):
                        continue

                profesores_disponibles.append(profesor)

            # Verificar que haya profesores disponibles
            if not profesores_disponibles:
                print("No hay profesores disponibles para esta seccion.")
                return

            # Mostrar los profesores disponibles
            print("\nProfesores disponibles:")
            for i in range(len(profesores_disponibles)):
                print(f"  {i + 1}. {profesores_disponibles[i]}")

            try:
                sel_prof = int(input("\nSeleccione un profesor (numero): ").strip())
                if sel_prof < 1 or sel_prof > len(profesores_disponibles):
                    print("Numero fuera de rango.")
                    return
            except ValueError:
                print("Debe ingresar un numero valido.")
                return

            # Asignar el nuevo profesor a la seccion
            nuevo_profesor = profesores_disponibles[sel_prof - 1]
            seccion.Asig_prof(nuevo_profesor)
            print(f"\nProfesor cambiado a {nuevo_profesor.nombre} correctamente.")

        elif opcion == "2":
            # --- CAMBIAR BLOQUE HORARIO ---
            # Buscar bloques con salones disponibles
            bloques_disponibles = []
            for bloque in self.bloques:
                # Debe tener aula disponible
                if not self.horario.Aula_abierta(bloque):
                    continue
                # No mostrar el bloque actual de la seccion
                if bloque == seccion.bloque:
                    continue
                bloques_disponibles.append(bloque)

            # Verificar que haya bloques disponibles
            if not bloques_disponibles:
                print("No hay bloques con salones disponibles.")
                return

            # Mostrar los bloques disponibles
            print("\nBloques con salones disponibles:")
            for i in range(len(bloques_disponibles)):
                print(f"  {i + 1}. {bloques_disponibles[i].Etiqueta()}")

            try:
                sel_bloque = int(input("\nSeleccione un bloque (numero): ").strip())
                if sel_bloque < 1 or sel_bloque > len(bloques_disponibles):
                    print("Numero fuera de rango.")
                    return
            except ValueError:
                print("Debe ingresar un numero valido.")
                return

            nuevo_bloque = bloques_disponibles[sel_bloque - 1]

            # Buscar profesores disponibles para la materia en el NUEVO bloque
            profesores_disponibles = []
            for profesor in self.profesores:
                # Debe poder dar esta materia
                if not profesor.Puede_dar_materia(materia):
                    continue
                # Verificar carga maxima (el profesor actual ya tiene esta seccion
                # asignada, asi que si es el mismo se le resta 1 de la cuenta)
                asignadas = self.contar_asignadas_profesor(profesor)
                if profesor == seccion.profesor:
                    # Esta seccion se va a mover, no contar como carga extra
                    asignadas = asignadas - 1
                if not profesor.Puede_Enseñar_Mas(asignadas):
                    continue
                # Debe estar libre en el nuevo bloque
                if not self.horario.Disponibilidad_prof(profesor, nuevo_bloque):
                    continue

                profesores_disponibles.append(profesor)

            # Verificar que haya profesores para el nuevo bloque
            if not profesores_disponibles:
                print("No hay profesores disponibles para el nuevo bloque.")
                return

            # Mostrar profesores disponibles para el nuevo bloque
            print("\nProfesores disponibles para este bloque:")
            for i in range(len(profesores_disponibles)):
                print(f"  {i + 1}. {profesores_disponibles[i]}")

            try:
                sel_prof = int(input("\nSeleccione un profesor (numero): ").strip())
                if sel_prof < 1 or sel_prof > len(profesores_disponibles):
                    print("Numero fuera de rango.")
                    return
            except ValueError:
                print("Debe ingresar un numero valido.")
                return

            nuevo_profesor = profesores_disponibles[sel_prof - 1]

            # Calcular el numero de salon ANTES de cambiar el bloque
            nuevo_salon = self.horario.Aulas_ocupadas(nuevo_bloque) + 1

            # Asignar nuevo bloque, profesor y salon
            seccion.Asig_Bloque(nuevo_bloque)
            seccion.Asig_prof(nuevo_profesor)
            seccion.id_salon = nuevo_salon
            seccion.Status = StatusSeccion.Assignada
            print(f"\nBloque cambiado a {nuevo_bloque.Etiqueta()} con profesor "
                  f"{nuevo_profesor.nombre} correctamente.")

        elif opcion == "0":
            print("Operacion cancelada.")

        else:
            print("Opcion invalida.")

    """
    =======================================================
    MODULO DE ESTADISTICAS (Modulo 5 - Opcional)
    =======================================================
    """

    def estadistica_salones_por_hora(self):
        """
        Grafica de barras que muestra cuantos salones estan ocupados
        en cada bloque horario. Incluye una linea roja con el maximo.
        """
        if self.horario is None:
            print("No hay horario generado.")
            return

        # Preparar los datos para la grafica
        nombres_bloques = []  # Nombres de los bloques para el eje X
        salones_ocupados = []  # Cantidad de salones ocupados para el eje Y

        for bloque in self.bloques:
            # Crear nombre corto para que quepa en la grafica
            inicio = bloque.Hora_init.strftime("%H:%M")
            fin = bloque.Hora_fin.strftime("%H:%M")
            if "Lunes" in bloque.Dias_disp:
                dias_corto = "L-M"
            else:
                dias_corto = "M-J"
            nombre = f"{dias_corto}\n{inicio}-{fin}"
            nombres_bloques.append(nombre)

            # Contar salones ocupados en este bloque
            ocupados = self.horario.Aulas_ocupadas(bloque)
            salones_ocupados.append(ocupados)

        # Crear la grafica de barras
        plt.figure(figsize=(14, 6))
        plt.bar(range(len(nombres_bloques)), salones_ocupados, color="steelblue")

        # Linea roja que muestra el maximo de salones
        plt.axhline(y=self.horario.num_aulas, color="red", linestyle="--",
                     label=f"Maximo de salones ({self.horario.num_aulas})")

        # Titulos y etiquetas
        plt.xlabel("Bloque Horario")
        plt.ylabel("Salones Ocupados")
        plt.title("Salones Ocupados por Bloque Horario")
        plt.xticks(range(len(nombres_bloques)), nombres_bloques, fontsize=7)
        plt.legend()
        plt.tight_layout()
        plt.show()
        print("Grafica de salones por hora generada.")

    def estadistica_carga_profesores(self):
        """
        Grafica de barras horizontales que muestra el porcentaje de
        materias asignadas vs permitidas de cada profesor.
        """
        if self.horario is None:
            print("No hay horario generado.")
            return

        if not self.profesores:
            print("No hay profesores cargados.")
            return

        # Preparar los datos
        nombres_profesores = []
        porcentajes = []

        for profesor in self.profesores:
            nombres_profesores.append(profesor.nombre)

            # Contar cuantas secciones tiene asignadas
            secciones_asignadas = self.contar_asignadas_profesor(profesor)

            # Calcular porcentaje (evitar division por cero)
            if profesor.max_materias > 0:
                porcentaje = (secciones_asignadas / profesor.max_materias) * 100
            else:
                porcentaje = 0

            porcentajes.append(porcentaje)

        # Crear grafica de barras horizontales
        plt.figure(figsize=(10, max(6, len(self.profesores) * 0.4)))
        plt.barh(range(len(nombres_profesores)), porcentajes, color="mediumseagreen")

        # Titulos y etiquetas
        plt.xlabel("Porcentaje de Carga (%)")
        plt.ylabel("Profesor")
        plt.title("Porcentaje de Materias Asignadas por Profesor")
        plt.yticks(range(len(nombres_profesores)), nombres_profesores, fontsize=7)
        plt.xlim(0, 110)

        # Mostrar el porcentaje al final de cada barra
        for i in range(len(porcentajes)):
            plt.text(porcentajes[i] + 1, i, f"{porcentajes[i]:.1f}%", va="center", fontsize=8)

        plt.tight_layout()
        plt.show()
        print("Grafica de carga de profesores generada.")

    def estadistica_secciones_cerradas(self):
        """
        Grafica de barras que muestra el porcentaje de secciones cerradas
        por cada materia. Verde = 0%, naranja = menos de 50%, rojo = 50% o mas.
        """
        if self.horario is None:
            print("No hay horario generado.")
            return

        if not self.materias:
            print("No hay materias cargadas.")
            return

        # Preparar los datos
        nombres_materias = []
        porcentajes_cerradas = []

        for materia in self.materias:
            # Solo materias que se ofertan (secciones > 0)
            if materia.secciones_requeridas <= 0:
                continue

            nombres_materias.append(materia.codigo)

            # Contar secciones cerradas
            total_secciones = len(materia.secciones)
            secciones_cerradas = 0

            for seccion in materia.secciones:
                if seccion.Status == StatusSeccion.Cerrada_no_prof:
                    secciones_cerradas = secciones_cerradas + 1
                elif seccion.Status == StatusSeccion.sin_asignar_clase:
                    secciones_cerradas = secciones_cerradas + 1

            # Calcular porcentaje
            if total_secciones > 0:
                porcentaje = (secciones_cerradas / total_secciones) * 100
            else:
                porcentaje = 0

            porcentajes_cerradas.append(porcentaje)

        if not nombres_materias:
            print("No hay materias con secciones para graficar.")
            return

        # Asignar colores segun el porcentaje
        colores = []
        for porcentaje in porcentajes_cerradas:
            if porcentaje == 0:
                colores.append("mediumseagreen")  # Verde = todo bien
            elif porcentaje < 50:
                colores.append("orange")  # Naranja = algunas cerradas
            else:
                colores.append("tomato")  # Rojo = muchas cerradas

        # Crear grafica de barras
        plt.figure(figsize=(14, 6))
        plt.bar(range(len(nombres_materias)), porcentajes_cerradas, color=colores)

        # Titulos y etiquetas
        plt.xlabel("Materia")
        plt.ylabel("Porcentaje de Secciones Cerradas (%)")
        plt.title("Porcentaje de Secciones Cerradas por Materia")
        plt.xticks(range(len(nombres_materias)), nombres_materias, rotation=45,
                   fontsize=7, ha="right")
        plt.ylim(0, 110)
        plt.tight_layout()
        plt.show()
        print("Grafica de secciones cerradas generada.")

    def menu_estadisticas(self):
        """
        Sub-menu del modulo de estadisticas.
        Permite elegir cual grafica ver.
        """
        while True:
            limpiar_pantalla()
            print("=" * 45)
            print("   MODULO DE ESTADISTICAS")
            print("=" * 45)
            print("1. Salones ocupados por bloque horario")
            print("2. Porcentaje de carga por profesor")
            print("3. Porcentaje de secciones cerradas por materia")
            print("0. Volver")
            print("-" * 45)

            opcion = input("Seleccione una opcion: ").strip()

            if opcion == "1":
                self.estadistica_salones_por_hora()
                input("\nPresione Enter para continuar...")

            elif opcion == "2":
                self.estadistica_carga_profesores()
                input("\nPresione Enter para continuar...")

            elif opcion == "3":
                self.estadistica_secciones_cerradas()
                input("\nPresione Enter para continuar...")

            elif opcion == "0":
                break

            else:
                print("Opcion invalida. Intente de nuevo.")
                input("Presione Enter para continuar...")

    """
    =======================================================
    MENUS DEL SISTEMA
    =======================================================
    """
    def menu_inicial(self):
        """
        Menu de inicio del programa.
        Permite al usuario elegir como cargar los datos iniciales
        o salir del sistema.
        """
        while True:
            limpiar_pantalla()
            print("=" * 45)
            print("   SISTEMA DE HORARIOS DE CLASES")
            print("=" * 45)
            print("1. Crear listas en blanco")
            print("2. Descargar datos desde GitHub")
            print("3. Cargar horario desde CSV")
            print("0. Salir")
            print("-" * 45)

            opcion = input("Seleccione una opcion: ").strip()

            if opcion == "1":
                self.crear_listas_en_blanco()
                input("Presione Enter para continuar...")
                self.menu_modulos()

            elif opcion == "2":
                try:
                    self.cargar_desde_github()
                    input("Presione Enter para continuar...")
                    self.menu_modulos()
                except Exception as e:
                    print("Error cargando datos:", e)
                    input("Presione Enter para continuar...")

            elif opcion == "3":
                self.cargar_csv()
                # Si se cargo correctamente, ir directo al menu post-generacion
                if self.horario is not None:
                    self.menu_post_generacion()
                else:
                    input("Presione Enter para continuar...")

            elif opcion == "0":
                print("Saliendo del sistema...")
                break

            else:
                print("Opcion invalida. Intente de nuevo.")
                input("Presione Enter para continuar...")

    def menu_modulos(self):
        """
        Menu de los 4 modulos fundamentales del sistema.
        Se muestra despues de crear listas en blanco o descargar datos.
        """
        while True:
            limpiar_pantalla()
            print("=" * 45)
            print("   MODULOS DEL SISTEMA")
            print("=" * 45)
            print("1. Profesores")
            print("2. Materias")
            print("3. Generar horario")
            print("4. Modificar horario")
            print("0. Volver al menu inicial")
            print("-" * 45)

            opcion = input("Seleccione una opcion: ").strip()

            if opcion == "1":
                self.menu_profesores()

            elif opcion == "2":
                self.menu_materias()

            elif opcion == "3":
                self.generar_horarios()
                # Si se genero el horario, pasar al menu post-generacion
                if self.horario is not None:
                    self.menu_post_generacion()
                else:
                    input("Presione Enter para continuar...")

            elif opcion == "4":
                # Verificar que exista un horario antes de modificar
                if self.horario is None:
                    print("Debe generar un horario primero.")
                    input("Presione Enter para continuar...")
                else:
                    self.menu_post_generacion()

            elif opcion == "0":
                break

            else:
                print("Opcion invalida. Intente de nuevo.")
                input("Presione Enter para continuar...")

    def menu_profesores(self):
        """
        Sub-menu del modulo de Profesores.
        Permite ver, agregar, eliminar y modificar profesores.
        """
        while True:
            limpiar_pantalla()
            print("=" * 45)
            print("   MODULO DE PROFESORES")
            print("=" * 45)
            print("1. Ver lista de profesores")
            print("2. Ver un profesor especifico")
            print("3. Agregar un profesor")
            print("4. Eliminar un profesor")
            print("5. Modificar materias de un profesor")
            print("0. Volver")
            print("-" * 45)

            opcion = input("Seleccione una opcion: ").strip()

            if opcion == "1":
                self.listar_profesores()
                input("\nPresione Enter para continuar...")

            elif opcion == "2":
                self.ver_profesor_especifico()
                input("\nPresione Enter para continuar...")

            elif opcion == "3":
                self.agregar_profesor()
                input("\nPresione Enter para continuar...")

            elif opcion == "4":
                self.eliminar_profesor()
                input("\nPresione Enter para continuar...")

            elif opcion == "5":
                self.modificar_materias_profesor()
                input("\nPresione Enter para continuar...")

            elif opcion == "0":
                break

            else:
                print("Opcion invalida. Intente de nuevo.")
                input("Presione Enter para continuar...")

    def menu_materias(self):
        """
        Sub-menu del modulo de Materias.
        Permite ver, agregar, eliminar y modificar materias.
        """
        while True:
            limpiar_pantalla()
            print("=" * 45)
            print("   MODULO DE MATERIAS")
            print("=" * 45)
            print("1. Ver lista de materias")
            print("2. Ver detalles de una materia")
            print("3. Ver profesores de una materia")
            print("4. Agregar una materia")
            print("5. Eliminar una materia")
            print("6. Modificar secciones de una materia")
            print("0. Volver")
            print("-" * 45)

            opcion = input("Seleccione una opcion: ").strip()

            if opcion == "1":
                self.listar_materias()
                input("\nPresione Enter para continuar...")

            elif opcion == "2":
                self.ver_detalle_materia()
                input("\nPresione Enter para continuar...")

            elif opcion == "3":
                self.ver_profesores_materia()
                input("\nPresione Enter para continuar...")

            elif opcion == "4":
                self.agregar_materia()
                input("\nPresione Enter para continuar...")

            elif opcion == "5":
                self.eliminar_materia()
                input("\nPresione Enter para continuar...")

            elif opcion == "6":
                self.modificar_secciones_materia()
                input("\nPresione Enter para continuar...")

            elif opcion == "0":
                break

            else:
                print("Opcion invalida. Intente de nuevo.")
                input("Presione Enter para continuar...")

    def menu_post_generacion(self):
        """
        Menu que se muestra despues de generar o cargar un horario.
        Permite consultar, guardar en CSV y modificar la asignacion.
        """
        while True:
            limpiar_pantalla()
            print("=" * 45)
            print("   HORARIO GENERADO")
            print("=" * 45)
            print("1. Ver horario de una materia")
            print("2. Ver horario de un profesor")
            print("3. Ver salones asignados a una hora")
            print("4. Guardar horario en CSV")
            print("5. Modificar asignacion de horarios")
            print("6. Ver estadisticas (graficas)")
            print("0. Volver")
            print("-" * 45)

            opcion = input("Seleccione una opcion: ").strip()

            if opcion == "1":
                self.mostrar_horarios_por_materia()
                input("\nPresione Enter para continuar...")

            elif opcion == "2":
                self.mostrar_horario_por_profesor()
                input("\nPresione Enter para continuar...")

            elif opcion == "3":
                self.ver_salones_por_hora()
                input("\nPresione Enter para continuar...")

            elif opcion == "4":
                self.guardar_csv()
                input("\nPresione Enter para continuar...")

            elif opcion == "5":
                self.modificar_horario()
                input("\nPresione Enter para continuar...")

            elif opcion == "6":
                self.menu_estadisticas()

            elif opcion == "0":
                break

            else:
                print("Opcion invalida. Intente de nuevo.")
                input("Presione Enter para continuar...")


"""
=======================================================
MAIN - Punto de entrada del programa
=======================================================
"""

if __name__ == "__main__":
    sistema = SistemaHorarios()
    sistema.menu_inicial()