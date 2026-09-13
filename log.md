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

## Ver 03 — 2026-09-11

### Cambios
- Se actualizó el código activo a la versión v0.3.
- La advertencia final aparece automáticamente al llegar a 60 segundos y se construye una sola vez por entrada al estado.
- Al entrar en advertencia, la ventana se restaura desde minimizada a su tamaño normal e intenta pasar temporalmente al frente sin quedar siempre visible.
- Los controles Pausa, Continuar, Cancelar, `+15 min` y `+30 min` permanecen disponibles durante la advertencia.
- Al sumar tiempo por encima de 60 segundos, la interfaz vuelve al estado normal sin reiniciar la cuenta regresiva ni duplicar callbacks.
- Se agregó confirmación al cerrar la ventana con un timer activo, incluso pausado o en advertencia.
- Se eliminó el control manual `VER ADVERTENCIA FINAL`.
- Se preservó la versión v0.2 en `old_versions/Ver02/pc_night_timer.py` antes de modificar el código activo.

### Motivo
- Implementar exclusivamente el PASO 3 definido en `DEVELOPMENT_SPEC.md`.

### Archivos afectados
- `pc_night_timer.py`
- `log.md`
- `old_versions/Ver02/pc_night_timer.py`

### Estado
- Implementación terminada y comprobada mediante validación de sintaxis y harness temporal de lógica; la interacción visual real queda pendiente de prueba manual por la limitación de Tcl/Tk del entorno de desarrollo.
- Se comprobó que no existen comandos de apagado ni acciones sobre el sistema.
- Todavía no existe apagado real.
- `settings.ini` queda pendiente para el Paso 4.
- El flujo completo del Modo de prueba queda pendiente para el Paso 5.

## Ver 04 — 2026-09-11

### Cambios
- Se actualizó el código activo a la versión v0.4.
- Se agregó la creación, lectura y escritura robusta de `settings.ini` mediante `configparser` de la biblioteca estándar.
- Se implementó la persistencia de la última selección rápida válida y, para `Personalizado`, de las horas y los minutos.
- Se implementó la persistencia del estado del Modo de prueba y su restauración visual al iniciar.
- Se implementó el guardado de la posición normal de la ventana y su restauración cuando permanece razonablemente visible.
- Se agregaron validaciones y valores predeterminados seguros para secciones ausentes, opciones desconocidas, números inválidos, booleanos inválidos y coordenadas fuera de pantalla.
- Se preservó la versión v0.3 en `old_versions/Ver03/pc_night_timer.py` antes de modificar el código activo.

### Motivo
- Implementar exclusivamente el PASO 4 definido en `DEVELOPMENT_SPEC.md`.

### Archivos afectados
- `pc_night_timer.py`
- `settings.ini`
- `log.md`
- `old_versions/Ver03/pc_night_timer.py`

### Estado
- Implementación terminada y comprobada mediante validación de sintaxis y un harness temporal para creación automática, reapertura, tiempos rápidos y personalizados, Modo de prueba, coordenadas válidas e inválidas, secciones faltantes, INI malformado y valores inválidos.
- El harness también comprobó regresiones de selección de tiempo, pausa, continuación, suma de tiempo, advertencia final, llegada a cero, cancelación y confirmación de cierre.
- El timer activo, su tiempo restante, la pausa y la advertencia no se persisten; cada inicio comienza sin timer activo.
- La ejecución visual no pudo completarse porque el runtime de desarrollo no encuentra un `init.tcl` utilizable. La GUI y la restauración en distintas configuraciones de monitores quedan pendientes de prueba manual con Tkinter operativo.
- El flujo completo del Modo de prueba queda pendiente para el Paso 5.
- Todavía no existe apagado real ni acciones sobre el sistema.

## Ver 05 — 2026-09-12

### Cambios
- Se actualizó el código activo a la versión v0.5.
- Se completó el Modo de prueba con una secuencia visual segura al llegar a cero: `Preparando apagado...`, `Cerrando aplicaciones...` y `Apagando Windows...`.
- Se agregó el estado final `PRUEBA COMPLETADA`, el mensaje de resultado simulado y el botón `NUEVO TIMER` para volver a la configuración.
- El Modo de prueba permanece claramente identificado durante el timer, la advertencia final y toda la simulación.
- Durante la secuencia simulada no hay controles de pausa, suma de tiempo o cancelación, y se evita la ejecución de callbacks duplicados.
- El cierre de la aplicación durante la simulación cancela sus callbacks pendientes y finaliza de forma limpia.
- El modo normal conserva el comportamiento seguro de v0.4 al llegar a cero y no ejecuta acciones reales.
- Se preservó la versión v0.4 en `old_versions/Ver04/pc_night_timer.py` antes de modificar el código activo.

### Motivo
- Implementar exclusivamente el PASO 5 definido en `DEVELOPMENT_SPEC.md`.

### Archivos afectados
- `pc_night_timer.py`
- `log.md`
- `old_versions/Ver04/pc_night_timer.py`

### Estado
- La implementación no contiene comandos de apagado, cierre de aplicaciones ni otras acciones reales del sistema.
- Se mantuvieron la cuenta regresiva, pausa, continuación, cancelación, suma de tiempo, advertencia final y persistencia de preferencias de las versiones anteriores.
- Pruebas estáticas y de lógica automatizada completadas; la interacción visual real queda pendiente de prueba manual si Tkinter no puede inicializarse en el entorno de desarrollo.
- El cierre real y ordenado de aplicaciones queda pendiente para el Paso 6.
- El apagado real de Windows todavía no está implementado.

## Ver 06 — 2026-09-12

### Cambios
- Se actualizó el código activo a la versión v0.6.
- En Modo normal, la llegada a cero inicia un cierre real y ordenado de aplicaciones de usuario mediante mensajes estándar `WM_CLOSE` a ventanas superiores visibles.
- Se agregó un período de gracia configurable de 20 segundos con polling no bloqueante cada 500 ms mediante `after()`; si todos los objetivos cierran antes, el flujo termina inmediatamente.
- Después del timeout se aplica un fallback forzado únicamente a los procesos originales todavía pendientes, usando los handles conservados desde la enumeración para evitar actuar sobre procesos ajenos o PIDs reutilizados.
- Las ventanas se agrupan por proceso, la propia aplicación queda excluida y se omiten ventanas ocultas, internas, sin título, componentes ubicados bajo Windows y nombres asociados a herramientas de seguridad.
- Chrome y otras aplicaciones normales reciben siempre primero la solicitud de cierre ordenado; no se mata indiscriminadamente por nombre ni se modifican perfiles o sesiones.
- Explorer sólo se trata mediante sus ventanas de carpeta identificadas y nunca se fuerza ni se termina `explorer.exe`; su cierre se comprueba por las ventanas concretas, no por la vida del shell.
- El Modo de prueba mantiene intacta su simulación y no crea el componente Win32, no enumera ventanas, no cierra aplicaciones y no ejecuta comandos del sistema.
- Se agregaron estados visuales localizados para preparación, cierre, espera, fallback y resultado final, indicando expresamente que el apagado de Windows aún no existe.
- Al cerrar PC Night Timer durante esta fase se cancelan sus callbacks y se liberan los handles abiertos.
- Se preservó la versión v0.5 exacta en `old_versions/Ver05/pc_night_timer.py` antes de modificar el código activo.

### Motivo
- Implementar exclusivamente el PASO 6 definido en `DEVELOPMENT_SPEC.md`, sin avanzar al apagado real del Paso 7.

### Archivos afectados
- `pc_night_timer.py`
- `log.md`
- `old_versions/Ver05/pc_night_timer.py`

### Estado
- Sintaxis Python comprobada correctamente.
- Harness temporal completado para la separación estricta entre Modo de prueba y Modo normal, cierre anticipado sin esperar los 20 segundos, polling no bloqueante, timeout y fallback dirigido.
- Se comprobó estáticamente la ausencia de `shutdown.exe`, `ExitWindowsEx` y `time.sleep()` en el hilo de interfaz; `settings.ini` no fue modificado.
- Por seguridad, las pruebas automatizadas no enumeraron, cerraron ni terminaron aplicaciones reales.
- Queda pendiente la prueba manual en Windows con Chrome, ventanas de Explorer, FXSound y reproductores: verificar cierre limpio, posibles diálogos de guardado, comportamiento de aplicaciones elevadas y si algún objetivo requiere fallback.
- Una aplicación elevada, protegida, perteneciente a Windows o no identificable puede quedar abierta y se informa en la pantalla final en lugar de aplicar fuerza bruta indiscriminada.
- El apagado real de Windows no está implementado; el PASO 7 queda pendiente.

## Ver 07 — 2026-09-12

### Cambios
- Se actualizó el código activo a la versión v0.7.
- Se implementó el apagado real de Windows mediante `shutdown.exe /s /f /t 0`, iniciado con `subprocess.Popen` sin mostrar una consola.
- Se conservó sin modificaciones innecesarias el cierre previo de aplicaciones de v0.6: solicitud ordenada, timeout de 20 segundos y fallback dirigido.
- Al terminar el cierre de aplicaciones, incluso si queda algún objetivo no resuelto, el flujo guarda las preferencias, muestra `Apagando Windows...` durante 750 ms y solicita el apagado.
- PC Night Timer permanece abierto hasta iniciar `shutdown.exe` y comprobar de forma no bloqueante que el comando terminó correctamente; después cierra su propia ventana.
- Se agregó manejo visible para archivo inexistente, error al crear el proceso y código de salida distinto de cero. En esos casos Windows permanece encendido y se permite volver a configuración o cerrar la aplicación.
- Se mantuvo una protección adicional que impide ejecutar la orden real si el Modo de prueba estuviera activo.
- El Modo de prueba conserva exactamente su simulación segura: no enumera ni cierra aplicaciones y no inicia `shutdown.exe`.
- Se preservó la versión v0.6 exacta en `old_versions/Ver06/pc_night_timer.py` antes de modificar el código activo.

### Motivo
- Implementar exclusivamente el PASO 7 definido en `DEVELOPMENT_SPEC.md`, sin avanzar a los ajustes visuales del Paso 8.

### Archivos afectados
- `pc_night_timer.py`
- `log.md`
- `old_versions/Ver06/pc_night_timer.py`

### Estado
- Sintaxis Python comprobada correctamente.
- Harness temporal completado con `subprocess.Popen` simulado para verificar el comando exacto, ausencia de consola, guardado previo de preferencias, delay mediante `after()`, polling no bloqueante, cierre propio después de resultado correcto y manejo de excepciones/códigos de error.
- Se comprobó que el Modo de prueba no alcanza `shutdown.exe`, que la propia aplicación continúa excluida del cierre previo y que no se usa `os.system()` ni `time.sleep()`.
- No se ejecutó un apagado real desde el entorno de desarrollo.
- Queda pendiente la prueba manual controlada en una PC secundaria para confirmar el apagado completo, la persistencia de `settings.ini` y el comportamiento al siguiente inicio de Chrome, Explorer y FXSound.
- El Paso 8 no fue implementado.

## Ver 07.1 — 2026-09-12

### Cambios
- Se actualizó el código activo a la versión v0.7.1.
- Se agregó detección de privilegios administrativos mediante `IsUserAnAdmin` de la API estándar de Windows.
- Si el proceso no está elevado, se solicita una nueva instancia mediante UAC con `ShellExecuteW` y el verbo `runas`, conservando el intérprete, la ruta del script y los argumentos de línea de comandos.
- La instancia original finaliza solamente cuando Windows confirma que inició la nueva instancia. Si el UAC se rechaza o falla, la aplicación continúa abierta sin elevación y no vuelve a solicitar permisos durante esa ejecución.
- Sin permisos administrativos se bloquea el inicio de timers reales y se muestra un aviso claro; el Modo de prueba permanece disponible y conserva su simulación segura.
- Se agregó una defensa adicional que impide llegar a `shutdown.exe` sin privilegios, sin modificar el comando ni el flujo estable de cierre de aplicaciones.
- Se preservó la versión v0.7 exacta en `old_versions/Ver07/pc_night_timer.py` antes de modificar el código activo.

### Motivo
- Corregir puntualmente la falta de permisos observada en la prueba manual del apagado real, sin avanzar al Paso 8.

### Archivos afectados
- `pc_night_timer.py`
- `log.md`
- `old_versions/Ver07/pc_night_timer.py`

### Estado
- Sintaxis Python comprobada correctamente.
- Harness temporal completado con APIs y procesos simulados para verificar detección administrativa, relanzamiento `runas` con rutas y argumentos con espacios, cancelación o fallo del UAC, ausencia de un segundo pedido de elevación, bloqueo del timer normal sin permisos, ejecución del Modo de prueba sin permisos y defensa previa a `shutdown.exe`.
- Se comprobó mediante comparación estructural que las funciones del cierre ordenado permanecen idénticas a la versión preservada v0.7.
- `settings.ini`, la lógica de cierre ordenado, el timeout de 20 segundos, el fallback y el comando `shutdown.exe /s /f /t 0` no fueron modificados.
- No se mostró un UAC real ni se ejecutaron cierres de aplicaciones o apagados desde el entorno de desarrollo. Queda pendiente una prueba manual controlada de elevación, cancelación del UAC y apagado real en Windows.
- El Paso 8 no fue implementado.

## Ver 07.2 — 2026-09-12

### Cambios
- Se actualizó el código activo a la versión v0.7.2.
- El relanzamiento elevado mediante UAC ahora utiliza `pythonw.exe` cuando ese ejecutable existe junto al intérprete Python actual, evitando la consola visible en la nueva instancia.
- Si `pythonw.exe` no existe, la autoelevación conserva como fallback el intérprete indicado por `sys.executable`.
- En una futura ejecución empaquetada se conserva directamente el ejecutable de la aplicación, sin intentar convertir su nombre a `pythonw.exe`.
- Se preservó la versión v0.7.1 exacta en `old_versions/Ver08/pc_night_timer.py` antes de modificar el código activo.

### Motivo
- Eliminar la ventana negra de consola de la instancia elevada sin modificar el comportamiento funcional de PC Night Timer ni avanzar al Paso 8.

### Archivos afectados
- `pc_night_timer.py`
- `log.md`
- `old_versions/Ver08/pc_night_timer.py`

### Estado
- Sintaxis Python comprobada correctamente.
- Harness temporal completado para verificar selección de `pythonw.exe` existente, fallback cuando falta, conservación de un futuro EXE empaquetado y traspaso correcto de rutas y argumentos con espacios a `ShellExecuteW`.
- Se comprobó mediante comparación estructural que las clases del timer y del cierre/apagado permanecen idénticas a la versión preservada v0.7.1.
- El timer, la advertencia final, `settings.ini`, el Modo de prueba, el cierre ordenado, el timeout de 20 segundos, el fallback y el apagado real no fueron modificados.
- No se mostró un UAC real ni se ejecutaron cierres de aplicaciones o apagados desde el entorno de desarrollo. Queda pendiente confirmar manualmente que la instancia elevada abre la GUI sin una consola visible.
- El Paso 8 no fue implementado.

## Ver 08 — 2026-09-13

### Cambios
- Se actualizó el código activo a la versión v0.8 y se realizó el revamp visual general del PASO 8.
- Se incorporó un fondo azul-gris con degradado sutil, una tarjeta central oscura, bordes finos y una paleta unificada de texto, acento celeste, advertencia ámbar, peligro bordó y resultado correcto verde apagado.
- La configuración ahora presenta mejor jerarquía y espaciado: selector de tiempo agrupado, subpanel atenuable para el tiempo personalizado, control de Modo de prueba con apariencia de switch, botón principal reforzado y acción programada más discreta.
- El timer activo usa un contador monoespaciado más grande, estados secundarios más claros y botones principales y secundarios visualmente coherentes, con Cancelar diferenciado como acción crítica.
- La advertencia final mantiene la identidad general y agrega acento ámbar, encabezado visible, contador destacado, mensaje contextual y cancelación especialmente visible, sin parpadeos ni animaciones agresivas.
- Se unificó la presentación de las pantallas de simulación, cierre ordenado y apagado real para los estados de preparación, cierre, espera, forzado y solicitud final de apagado.
- Se rediseñaron la pantalla `PRUEBA COMPLETADA` y el estado de error de apagado para integrarlos con la nueva identidad visual.
- Se preservó la versión v0.7.2 exacta en `old_versions/Ver08/pc_night_timer.py` antes de modificar el código activo.
- Antes de esta iteración, el directorio real más reciente era `old_versions/Ver071/` aunque la entrada histórica de v0.7.2 lo denominaba `Ver08`; se continuó con `Ver08` por ser la siguiente carpeta consecutiva realmente disponible, sin sobrescribir `Ver071`.
- La lógica funcional no fue modificada de forma sustancial; los cambios se limitaron a recursos, helpers y métodos de presentación.

### Motivo
- Implementar exclusivamente el PASO 8 definido en `DEVELOPMENT_SPEC.md`, mejorando la legibilidad nocturna, la jerarquía visual y la coherencia de todas las vistas sin avanzar al empaquetado.

### Archivos afectados
- `pc_night_timer.py`
- `log.md`
- `old_versions/Ver08/pc_night_timer.py`

### Estado
- Sintaxis Python comprobada correctamente mediante `py_compile`.
- Harness lógico seguro completado para formato y selección de tiempo, validación personalizada, creación de `settings.ini`, callback único del timer y construcción simulada del apagado con el comando, streams y bandera `CREATE_NO_WINDOW` esperados; no se ejecutó `shutdown.exe` ni se cerraron aplicaciones.
- Comparación AST contra la copia preservada completada: UAC, persistencia, timer, cierre ordenado y apagado permanecen estructuralmente idénticos; solamente cambiaron métodos visuales y se agregaron helpers de interfaz.
- Se comprobó la presencia de todos los textos y estados visuales requeridos y `git diff --check` finalizó sin errores.
- La ejecución visual real no pudo completarse porque el runtime disponible de Codex no encuentra un `init.tcl` utilizable. Queda pendiente una prueba visual manual en Windows, especialmente con escala 125 %, para confirmar respiración, foco, tamaño del contador y ajuste fino de contraste.
- No se ejecutaron cierre real de aplicaciones, elevación UAC ni apagado real durante esta iteración. Sus rutas de código se preservaron y se verificaron estática y estructuralmente.
- El PASO 9 no fue implementado.
