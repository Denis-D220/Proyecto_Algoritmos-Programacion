from datetime import datetime, time
import requests
import json
import re

BASE_url = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-2/main"

#Informacion de los bloques

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

class StatusSeccion():
    Assignada = "Asignada"
    Cerrada_no_prof = "Cerrada_no_prof"
    sin_asignar_clase = "sin_asignar_clase"

"""
=======================================================
CLASES
=======================================================
"""
class Profesor:
    def __init__(self, nombre: str, cedula: str, email: str, max_materias: int):
        self.nombre = nombre
        self.cedula = cedula
        self.email = email
        self.max_materias = max_materias
        self.List_materias = []

    def Puede_Enseñar_Mas(self, Asignado: int) -> bool:
        return Asignado < self.max_materias

    def Puede_dar_clase(self, materia: "Materia") -> bool:
        return materia in self.List_materias

    def __str__(self) -> str:
        materias = ", ".join(m.codigo_mat for m in self.List_materias) if self.List_materias else "Ninguna"
        return f"{self.cedula} | {self.nombre} | {self.email} | Max: {self.max_materias} | Materias: {materias}"

class Materia:
    def __init__(self, codigo_mat: str, nombre_mat: str, secciones_requeridas: int):
        self.codigo = codigo_mat
        self.nombre_mat = nombre_mat
        self.secciones_requeridas = secciones_requeridas
        self.secciones = []

    def Esta_abierta(self) -> bool:
        return self.secciones_requeridas > 0
    
    def __str__(self) -> str:
        return f"{self.codigo_mat} - {self.nombre_mat} (Secciones: {self.secciones_requeridas})"

class Bloque:
    """
    Dias_disp: String ej = "Lunes y miercoles"
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
        inicio = self.Hora_init.strptime("%H:%M")
        fin = self.Hora_fin.strptime("%H:%M")

        return f"{self.Dias_disp} {inicio} - {fin}"

    def __str__(self) -> str:
        return self.Etiqueta()

class Seccion:
    def __init__(self, NumSeccion: int):
        self.NumSeccion = NumSeccion
        self.Status = StatusSeccion.ASSIGNADA
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
        self.Status = StatusSeccion.CERRADA_NO_PROF
        self.profesor = None
        self.bloque = None
        self.id_salon = None

    def Marcar_no_Materia(self):
        self.Status = StatusSeccion.SIN_ASIGNAR_CLASE
        self.id_salon = None

    def __str__(self) -> str:
        materia = self.materia.codigo_mat if self.materia else "N/A"
        prof = self.profesor.nombre if self.profesor else "N/A"
        bloque = self.bloque.Etiqueta() if self.bloque else "N/A"
        salon = self.id_salon if self.id_salon is not None else "N/A"
        return (
            f"Materia: {materia} | Sección: {self.NumSeccion} | "
            f"Profesor: {prof} | Bloque: {bloque} | Aula: {salon} | "
            f"Estado: {self.Status.value}"
        )
    
class Horario:
    def __init__(self, num_aulas: int):
        self.num_aulas = num_aulas
        self.secciones = []
    
    def Get_secciones_por_materia(self, materia: Materia) -> list[Seccion]:
        return [s for s in self.secciones if s.materia == materia]
    
    def Get_secciones_por_prof(self, profesor: Profesor) -> list[Seccion]:
        return [s for s in self.secciones if s.profesor == profesor]
    
    def Aulas_ocupadas(self, bloque: Bloque) -> int:
        return sum( 1 for s in self.secciones
                   if s.bloque == bloque and s.status == StatusSeccion.Assignada)
    
    def Aula_abierta(self, bloque: Bloque) -> bool:
        return self.Aulas_ocupadas(bloque) < self.num_aulas
    
    def Disponibilidad_prof(self, profesor: Profesor, bloque: Bloque):
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
    
        # Reparacion del JSON de profesores
        texto = texto.replace('"Cedula"::', '"Cedula":')
        texto = re.sub(r'"\s*"Apellido"', '", "Apellido"', texto)

        return json.loads(texto)
    
    def cargar_desde_github(self):
        materias_raw = self.descargar_json("materias2526-2.json")
        profesores_raw = self.descargar_json("profesores.json")

        #Crear materias
        for item in materias_raw:
            materia = Materia(
                codigo_mat= str(item.get("Codigo", "")).strip(),
                nombre_mat= str(item.get("Nombre", "")).strip(),
                secciones_requeridas= int(item.get("Secciones", 0))
            )
            self.materias.append(materia)

        #Mapa de materias ordenada con su codigo
        mapa_materias = {m.codigo_mat: m for m in self.materias}

        #Hacer lista de profesores
        for item in profesores_raw:
            nombre = f"{str(item.get("Nombre", "")).strip()} {str(item.get("Apellido", "")).strip()}".strip()
            profesor = Profesor(
                nombre= nombre,
                cedula=str(item.get("Cedula", "")).strip(),
                email=str(item.get("Email", "")).strip(),
                max_materias=int(item.get("Max Carga", 0))
            )
            for codigo in item.get("Materias", []):
                codigo = str(codigo).strip()
                if codigo in mapa_materias:
                    profesor.List_materias.append(mapa_materias[codigo])
                
            self.profesores.append(profesor)

        print("Datos cargados correctamente")

"""
 FUNCIONES DE BUSQUEDA
"""