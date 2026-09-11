# Historial de desarrollo — PC Night Timer

## Ver 01 — 2026-09-11

### Cambios
- Se creó la estructura inicial del proyecto para la versión v0.1.
- Se creó la interfaz estática en Tkinter con tema oscuro y ventana fija.
- Se diseñaron las vistas de configuración, timer activo y advertencia final.
- Se agregaron controles visuales para tiempos rápidos, tiempo personalizado, Modo de prueba, inicio, pausa, cancelación y suma de tiempo.

### Motivo
- Implementar exclusivamente el PASO 1 definido en `DEVELOPMENT_SPEC.md` y dejar preparada la interfaz para su validación visual.

### Archivos afectados
- `pc_night_timer.py`
- `log.md`
- `old_versions/` (carpeta inicial vacía)

### Estado
- Interfaz estática implementada. El comportamiento funcional del timer queda pendiente para el Paso 2.
- No se implementó apagado real ni ninguna acción sobre el sistema.
- La sintaxis de Python fue comprobada correctamente.
- La ejecución visual no pudo completarse en el entorno de desarrollo porque su runtime de Python no pudo inicializar Tcl/Tk (`init.tcl`).
- Estado: implementación terminada, pendiente de prueba visual manual en una instalación de Python con Tkinter operativo.
