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

## Ver 02 — 2026-09-11

### Cambios
- Se actualizó el código activo a la versión v0.2.
- Se implementó la cuenta regresiva interna en formato `HH:MM:SS` mediante `after()` de Tkinter.
- Se habilitaron los ocho tiempos rápidos y el tiempo personalizado por horas y minutos.
- Se agregaron validaciones para entradas no numéricas, minutos fuera de 0 a 59 y tiempo total igual a cero.
- Se implementaron Pausa, Continuar, Cancelar, `+15 min` y `+30 min`, tanto durante la ejecución como durante la pausa.
- Al llegar a cero, el timer se detiene en `00:00:00`, deshabilita los controles de modificación y muestra `Tiempo finalizado` sin ejecutar acciones del sistema.
- Se preservó la versión v0.1 en `old_versions/Ver01/pc_night_timer.py` antes de modificar el código activo.

### Motivo
- Implementar exclusivamente el PASO 2 definido en `DEVELOPMENT_SPEC.md`.

### Archivos afectados
- `pc_night_timer.py`
- `log.md`
- `old_versions/Ver01/pc_night_timer.py`

### Estado
- Sintaxis Python comprobada correctamente.
- Harness temporal completado correctamente para tiempos rápidos, tiempo personalizado de 2 minutos, entradas inválidas, pausa sin decremento, continuación, cancelación sin callbacks pendientes, suma de 15 y 30 minutos en ejecución y pausa, llegada a cero y protección contra valores negativos.
- Se comprobó estáticamente que `pc_night_timer.py` no contiene llamadas a apagado ni comandos del sistema.
- La prueba visual con Tkinter no pudo ejecutarse en el runtime de desarrollo porque no encuentra un `init.tcl` utilizable. Queda pendiente la prueba manual de la GUI en una instalación de Python con Tkinter operativo.
- No existe apagado real todavía.
- La advertencia final automática queda pendiente para el Paso 3.
- `settings.ini` queda pendiente para el Paso 4.
