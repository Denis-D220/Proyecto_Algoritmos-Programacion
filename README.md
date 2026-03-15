# Proyecto: Horarios de Clases

## Informacion Academica

| | |
|---|---|
| **Universidad** | Universidad Metropolitana |
| **Facultad** | Ingenieria |
| **Departamento** | Gestion de Proyectos y Sistemas |
| **Materia** | Algoritmos y Programacion (BPTSP05) |
| **Trimestre** | 2526-2 |
| **Estudiantes** | Denis Daniel y Capozzolo Roguer |

## Descripcion del Proyecto

Sistema desarrollado para planificar la oferta de horarios de clases de cada trimestre. El programa permite generar una asignacion automatica de profesores, materias, bloques horarios y salones, asi como modificar dicha asignacion manualmente.

Los datos de profesores y materias se obtienen desde el repositorio de GitHub de la catedra en formato JSON, y el horario generado puede guardarse y cargarse en formato CSV para su visualizacion en Excel.

## Modulos del Sistema

1. **Profesores** — Ver, agregar, eliminar y modificar la lista de profesores y sus materias asignadas.
2. **Materias** — Ver, agregar, eliminar y modificar materias con su numero de secciones.
3. **Generacion de Horarios** — Asignacion automatica de secciones a bloques horarios, profesores y salones.
4. **Modificacion de Horarios** — Cambiar profesor o bloque horario de una seccion especifica.

## Requisitos

- Python 3.10 o superior
- Libreria `requests` (`pip install requests`)
- Conexion a internet (para descargar datos desde GitHub)

## Ejecucion

```bash
python DenisDaniel_&_CapozzoloRoguer.py
```

## Fuente de Datos

Repositorio de la catedra: https://github.com/FernandoSapient/BPTSP05_2526-2
