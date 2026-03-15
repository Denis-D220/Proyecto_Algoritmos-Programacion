from datetime import datetime, time # Importar libreria de tiempo para guardar las horas de los bloques en type: datetime
import requests # Importar libreria de request para obtener los datos del github
import json # Importar libreria de Json para cuando tenga los datos del github los tenga en archivo .json

BASE_url = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-2/main"

#Informacion de los bloques posibles

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

class Profesor:
    """
    Atributos de Profesor: nombre: str, cedula: str, email: str, max_materias: int

    Metodos de Profesor: Puede_Enseñar_Mas(int) => bool, Puede_dar_clase(Materia) => bool
    """
    def __init__(self, nombre: str, cedula: str, email: str, max_materias: int):
        self.nombre = nombre
        self.cedula = cedula
        self.email = email
        self.max_materias = max_materias
        self.List_materias = []

    def Puede_Enseñar_Mas(self, Asignado: int) -> bool:
        return Asignado < self.max_materias

    def Puede_dar_clase(self, materia: Materia) -> bool:
        return materia in self.List_materias

    def __str__(self) -> str:
        materias = ", ".join(m.codigo for m in self.List_materias) if self.List_materias else "Ninguna"
        return f"{self.cedula} | {self.nombre} | {self.email} | Max: {self.max_materias} | Materias: {materias}"

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

class Bloque:
    """
    Atributos de Bloque: Dias_disp: str, Hora_init: str, Hora_fin: str

    Metodos de Bloque: Etiqueta() => str

    Dias_disp: String ej = "Lunes y miercoles", 
    Hora_init / Hora_fin = String formato: "HH:MM"
    """
    def __init__(self, Dias_disp: str, Hora_init: str, Hora_fin: str):
        self.Dias_disp = Dias_disp

        # Convertir str -> datetime.time
        self.Hora_init: time = datetime.strptime(Hora_init, "%H:%M").time()
        self.Hora_fin: time = datetime.strptime(Hora_fin, "%H:%M").time()

    def Etiqueta(self) -> str:
        """
        Retorna titulo lejible por la hora del bloque
        Ejemplo: "Lunes y Miercoles 07:00 - 8:00"
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
        return [s for s in self.secciones if s.profesor == profesor]
    
    def Aulas_ocupadas(self, bloque: Bloque) -> int:
        """
        Devuelve la cantidad de secciones que que esten usando aulas en el bloque de horario

        Ej de un Bloque => Bloque: Lunes y Miércoles", "7:00", "8:30".
        Materia: Bases de datos Sec 1 => Aula 1
        Aulas ocupadas = 1  
        """
        contador = 0
        for s in self.secciones:
            if s.bloque == bloque and s.status == StatusSeccion.Assignada:
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
            if s.profesor == profesor and s.bloque == bloque and s.status == StatusSeccion.Assignada:
                return False
        return True
    
"""
 CLASE DEL SISTEMA
"""

class SistemaHorarios:
    def __init__(self):
        self.profesores = []
        self.materias = []
        self.bloques = [Bloque(*datos) for datos in bloques_fijos]
        self.horario = None

    """
    Cargar los datos del github
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
    GENERAR LOS HORARIOS
    """
    def generar_horarios(self):
        """
        
        """
        if not self.materias:
            print("No hay materias cargadas")
            return
        
        try:
            num_aulas = int(input("Inserte numero de aulas disponibles: ").strip())
            if num_aulas <= 0:
                print("Inserte un numero mayor a 0.")
                return
        except ValueError:
            print("Numero invalido")
            return
        
        self.horario = Horario(num_aulas)

        # Limpiar secciones con materias previas
        for materia in self.materias:
            materia.secciones = []

        bloque_actual = 0 # Comenzar desde el primer bloque del horario

        for materia in self.materias:
            if not materia.Esta_abierta(): #Retorna un valor True or False
                continue

            for num_sec in range(1, materia.secciones_requeridas + 1):
                seccion = Seccion(num_sec)
                seccion.materia = materia

                bloque_elegido = None

                # 1. intentar bloque no usado por la misma materia

                # Se Crea una lista que empieza en bloque_actual y luego añade lo que quedó atrás
                bloques_reordenados = self.bloques[bloque_actual:] + self.bloques[:bloque_actual]

                for candidato in bloques_reordenados:
                    if self.horario.Aula_abierta(candidato):
                        bloque_elegido = candidato
                        break

                    """
                    Seleccionar el siguiente bloque posible empezando desde bloque_actual, recorriendo la lista de forma circular.

                    Ese bloque se guarda en la variable candidato para comprobar si:

                    hay aula disponible

                    el profesor está libre

                    se puede asignar la sección
                    """
        
                # 2. si no se puede, usar cualquier bloque libre
                if bloque_elegido is None:
                    for i in range(len(self.bloques)):
                        candidato = self.bloques[(bloque_actual + i) % len(self.bloques)]
                        if self.horario.Aula_abierta(candidato):
                            bloque_elegido = candidato
                            break

                # 3. si no hay aula libre
                if bloque_elegido is None:
                    seccion.Marcar_no_Materia()
                    materia.secciones.append(seccion)
                    self.horario.secciones.append(seccion)
                    continue

                # 4. buscar profesor disponible
                profesor_elegido = None
                for profesor in self.profesores:
                    if not profesor.Puede_dar_clase(materia):
                        continue
                    if not profesor.Puede_Enseñar_Mas(self.contar_asignadas_profesor(profesor)):
                        continue
                    if not self.horario.Disponibilidad_prof(profesor, bloque_elegido):
                        continue

                    profesor_elegido = profesor
                    break

                # 5. si no hay profesor
                if profesor_elegido is None:
                    seccion.Marcar_no_Prof()
                    materia.secciones.append(seccion)
                    self.horario.secciones.append(seccion)
                    continue

                # 6. asignar todo
                seccion.Asig_prof(profesor_elegido)
                seccion.Asig_Bloque(bloque_elegido)
                seccion.id_salon = self.horario.Aulas_ocupadas(bloque_elegido) + 1
                seccion.Status = StatusSeccion.Assignada

                materia.secciones.append(seccion)
                self.horario.secciones.append(seccion)

                bloque_actual = (self.bloques.index(bloque_elegido) + 1) % len(self.bloques)

        print("Horario generado correctamente.")


    """
    MENU DE OPCIONES
    """
    def menu_consultas(self):
        while True:
            print("\n=== CONSULTAS DE HORARIO ===")
            print("1. Ver horario por materia")
            print("2. Ver horario por profesor")
            print("3. Ver bloques")
            print("0. Volver")
        
            op = input("Opcion: ").strip()
            
            if op == "1":
                self.mostrar_horarios_por_materia()
            elif op == "2":
                self.mostrar_horario_por_profesor()
            elif op == "3":
                self.mostrar_bloques()
            elif op == "0":
                break
            else:
                print("Opcion Invalida")

    def menu_principal(self):
        """
        Funcion de ordenamiento para gestionar los datos en base a las funciones de la clase de
        sistema de horarios.
        """
        while True:
            print("\n=== SISTEMA DE HORARIOS ===")
            print("1. Cargar datos desde GitHub")
            print("2. Listar materias")
            print("3. Listar profesores")
            print("4. Generar horario")
            print("5. Consultas de horario")
            print("0. Salir")

            op = input("Opción: ").strip()

            if op == "1":
                try:
                    self.cargar_desde_github()
                except Exception as e:
                    print("Error cargando datos:", e)
            elif op == "2":
                self.listar_materias()
            elif op == "3":
                self.listar_profesores()
            elif op == "4":
                self.generar_horarios()
            elif op == "5":
                self.menu_consultas()
            elif op == "0":
                print("Saliendo...")
                break
            else:
                print("Opción inválida.")

"""
MAIN 
"""

if __name__ == "__main__":
    sistema = SistemaHorarios()
    sistema.menu_principal()