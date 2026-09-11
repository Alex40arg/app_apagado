# DEVELOPMENT_SPEC.md

## Proyecto

**Nombre:** PC Night Timer  
**Plataforma:** Windows 10 / Windows 11  
**Lenguaje previsto:** Python  
**Interfaz gráfica:** Tkinter  
**Distribución futura:** EXE standalone mediante PyInstaller

---

# 1. Objetivo del proyecto

PC Night Timer es una pequeña aplicación de escritorio para Windows destinada a programar el apagado automático de una PC después de un intervalo de tiempo configurable.

El caso de uso principal es una computadora conectada a un televisor en un dormitorio, utilizada por la noche para ver películas, videos o contenido multimedia.

La aplicación debe permitir iniciar un temporizador de apagado de manera simple, mostrar claramente el tiempo restante, advertir al usuario antes del apagado y realizar el cierre del sistema de la forma más ordenada posible.

La prioridad del proyecto es:

- simplicidad;
- legibilidad a distancia;
- funcionamiento confiable;
- bajo consumo de recursos;
- comportamiento predecible;
- evitar cierres innecesariamente bruscos de aplicaciones;
- asegurar que, salvo cancelación explícita, la PC termine apagándose.

---

# 2. Alcance de la versión inicial

La versión inicial del proyecto, v0.1, debe centrarse únicamente en:

**Apagado programado de Windows.**

No implementar todavía:

- suspensión;
- hibernación;
- reinicio;
- programación por hora exacta;
- calendario;
- días de la semana;
- inicio automático con Windows;
- icono en bandeja del sistema;
- estadísticas;
- control remoto;
- apagado por red;
- sonidos complejos;
- sistemas de actualización;
- soporte específico para aplicaciones individuales salvo que resulte necesario más adelante.

Suspender e Hibernar se consideran posibles funciones futuras y deben quedar fuera de la implementación inicial.

---

# 3. Archivos del proyecto

La estructura inicial prevista es:

```text
PC_Night_Timer/
│
├── AGENTS.md
├── DEVELOPMENT_SPEC.md
├── log.md
├── pc_night_timer.py
├── settings.ini
│
└── old_versions/
```

La estructura puede ampliarse únicamente si una etapa posterior lo requiere realmente.

No dividir prematuramente el proyecto en múltiples módulos si la complejidad actual no lo justifica.

Debe respetarse siempre lo indicado en `AGENTS.md`.

---

# 4. Versionado

El archivo principal debe comenzar con una línea comentada indicando la versión.

Ejemplo:

```python
# Version: v0.1
```

Cada modificación real debe respetar las reglas de versionado, copias en `old_versions/` y actualización de `log.md` definidas en `AGENTS.md`.

---

# 5. Plataforma y compatibilidad

La aplicación debe funcionar en:

- Windows 10;
- Windows 11.

No debe depender de características exclusivas de una edición determinada de Windows.

La PC objetivo puede utilizar:

- resolución Full HD 1920×1080;
- escala de Windows de 100% o 125%.

La interfaz debe seguir siendo completamente visible y cómoda en esas condiciones.

---

# 6. Diseño general de la interfaz

## 6.1 Estilo

La interfaz debe usar tema oscuro apropiado para uso nocturno.

Orientación visual:

- fondo negro o casi negro;
- paneles gris muy oscuro;
- texto principal blanco;
- texto secundario gris claro;
- color de acento bordó oscuro o azul apagado;
- evitar colores chillones, neón o excesivamente brillantes;
- utilizar rojo o ámbar solamente cuando ayuden a comunicar una advertencia o acción destructiva/inminente.

La aplicación debe verse sobria, limpia y moderna dentro de las posibilidades de Tkinter.

---

## 6.2 Tamaño de ventana

La ventana debe tener tamaño fijo.

Tamaño inicial recomendado:

```text
850 × 600 px
```

Este tamaño podrá ajustarse durante las pruebas visuales si fuera necesario.

Requisitos:

- no permitir redimensionamiento manual;
- permitir minimizar;
- permitir restaurar;
- mantener el timer funcionando correctamente mientras la ventana está minimizada;
- no maximizar automáticamente la ventana;
- al restaurarse automáticamente debe volver a su tamaño normal.

---

## 6.3 Legibilidad

La interfaz está pensada para verse desde una cama frente a un televisor de 40 pulgadas Full HD.

Por lo tanto:

- el contador debe ser el elemento visual principal;
- las fuentes deben ser suficientemente grandes;
- los botones deben tener dimensiones cómodas;
- debe existir espacio razonable entre controles;
- no apretar elementos innecesariamente;
- tampoco dejar grandes espacios vacíos sin función;
- el timer debe poder leerse con facilidad a varios metros de distancia.

El contador podrá utilizar inicialmente un tamaño visual equivalente aproximado a 64–80 px, sujeto a prueba real.

---

## 6.4 Selección y foco

Los elementos puramente informativos no deben comportarse como texto seleccionable o editable.

Evitar que:

- títulos;
- etiquetas;
- mensajes;
- contador;
- textos decorativos

puedan recibir foco innecesario o dar sensación de selección.

Solamente deben ser interactivos los controles que realmente lo requieran:

- botones;
- listas desplegables;
- campos de tiempo personalizado.

---

# 7. Estados principales de la interfaz

La aplicación debe tener al menos dos estados visuales claramente diferenciados.

## 7.1 Estado de configuración

Permite elegir el tiempo e iniciar el timer.

Debe incluir:

- nombre de la aplicación;
- selector de tiempo rápido;
- opción de tiempo personalizado;
- indicador de Modo de prueba;
- botón principal para iniciar.

La acción de la v0.1 será siempre:

```text
Apagar PC
```

No es necesario mostrar todavía un selector de acción si solamente existe una acción disponible.

---

## 7.2 Estado de timer activo

Durante la cuenta regresiva el protagonismo debe pasar al contador.

Debe mostrar:

- texto descriptivo, por ejemplo:
  - `La PC se apagará en`
- contador en formato:
  - `HH:MM:SS`
- botón Pausa / Continuar;
- botón Cancelar;
- botón `+15 min`;
- botón `+30 min`.

Los controles de configuración inicial pueden ocultarse o deshabilitarse mientras el timer esté funcionando.

---

# 8. Selección de tiempo

## 8.1 Tiempos rápidos

Ofrecer inicialmente:

- 15 minutos;
- 30 minutos;
- 45 minutos;
- 60 minutos;
- 75 minutos;
- 90 minutos;
- 105 minutos;
- 120 minutos.

También debe existir:

```text
Personalizado
```

---

## 8.2 Tiempo personalizado

El tiempo personalizado debe permitir valores pequeños para pruebas, por ejemplo 2 minutos.

Preferencia:

- campo de horas;
- campo de minutos;

en lugar de un único campo de texto libre.

Debe validarse la entrada.

No aceptar:

- valores negativos;
- texto no numérico;
- tiempo total igual a cero.

No agregar segundos como opción normal para usuario final salvo que se decida explícitamente más adelante.

---

# 9. Funcionamiento del temporizador

El timer debe ser controlado por la propia aplicación.

No utilizar como mecanismo principal:

```text
shutdown /s /t <segundos>
```

para toda la duración del contador.

La aplicación debe mantener internamente el tiempo restante y ejecutar la acción real solamente al finalizar.

Ventajas buscadas:

- pausa real;
- continuar;
- sumar tiempo;
- cancelación inmediata;
- contador visible exacto;
- advertencia final;
- modo de prueba;
- mayor control sobre el flujo de apagado.

---

# 10. Pausa

El botón Pausa debe:

- detener temporalmente la cuenta regresiva;
- mantener visible el tiempo restante;
- cambiar su función o texto a `Continuar`.

Al continuar:

- el timer debe proseguir desde el tiempo restante;
- no debe reiniciarse.

---

# 11. Cancelación

El botón Cancelar debe:

- detener completamente el timer;
- impedir el apagado;
- regresar al estado de configuración;
- conservar como selección inicial el tiempo configurado anteriormente.

Puede solicitar confirmación si el apagado está dentro del último minuto.

---

# 12. Agregar tiempo

Durante un timer activo deben existir:

```text
+15 min
+30 min
```

Al pulsarlos:

- sumar inmediatamente ese tiempo al contador actual;
- mantener el timer activo;
- actualizar la visualización;
- si la aplicación estaba en estado de advertencia final y el nuevo tiempo supera 60 segundos, debe volver al estado normal del timer.

---

# 13. Advertencia final

Cuando queden exactamente 60 segundos o menos:

1. Si la ventana está minimizada, restaurarla.
2. Llevarla al frente de manera razonable.
3. No maximizarla.
4. Mostrar un estado visual de advertencia.
5. Mantener visible el contador.
6. Mostrar claramente que el apagado es inminente.
7. Ofrecer una forma evidente de cancelarlo.

Texto orientativo:

```text
La computadora se apagará en menos de un minuto.

Guarde cualquier trabajo pendiente
o cancele el apagado.
```

Durante este estado el botón de cancelación debe ser especialmente visible.

Se puede utilizar un color ámbar suave o similar para resaltar el contador o el borde.

Evitar efectos molestos, parpadeos fuertes o sonidos obligatorios.

---

# 14. Cierre de la aplicación

## 14.1 Sin timer activo

Si no existe timer activo, la aplicación puede cerrarse normalmente.

## 14.2 Con timer activo

Si existe un timer activo y el usuario intenta cerrar la ventana:

- mostrar un cuadro de confirmación;
- advertir que cerrar la aplicación cancelará el timer;
- permitir:
  - cancelar el cierre;
  - confirmar cierre y cancelar el timer.

Nunca cerrar silenciosamente la aplicación dejando al usuario creer que el apagado sigue programado.

---

# 15. Apagado de Windows

El objetivo es conseguir un cierre lo más ordenado posible, pero garantizando que la PC finalmente se apague si el usuario no cancela.

La aplicación debe evitar utilizar un cierre agresivo como primera opción.

Flujo deseado:

1. El contador llega a cero.
2. Mostrar:
   - `Preparando apagado...`
3. Intentar permitir un cierre ordenado de aplicaciones.
4. Dar un margen breve para que finalicen.
5. Solicitar el apagado de Windows.
6. Si alguna aplicación impide el cierre normal, el sistema debe terminar apagándose igualmente después del mecanismo previsto.

No implementar una estrategia que deje la PC encendida indefinidamente porque una aplicación se resista al cierre.

La prioridad final es:

```text
si el usuario no cancela, la PC debe apagarse.
```

---

# 16. Aplicaciones abiertas y cierre seguro

La aplicación se utilizará normalmente con programas como:

- Google Chrome;
- Explorador de archivos;
- reproductores multimedia;
- FXSound;
- aplicaciones sencillas similares.

Evitar matar procesos directamente como primera estrategia.

Especialmente con Chrome se debe intentar evitar que al siguiente inicio aparezca:

```text
Chrome no se cerró correctamente
```

La implementación concreta del cierre ordenado debe investigarse y probarse durante las etapas correspondientes.

No agregar desde el inicio una lista rígida y compleja de aplicaciones específicas.

---

# 17. Modo de prueba

Debe existir un Modo de prueba para desarrollar y validar la aplicación sin apagar realmente la PC.

Cuando esté activo:

- ejecutar el timer normalmente;
- permitir minimizar;
- permitir restaurar;
- probar Pausa;
- probar Continuar;
- probar Cancelar;
- probar `+15 min`;
- probar `+30 min`;
- ejecutar la advertencia de 60 segundos;
- simular el estado de preparación del apagado;
- NO cerrar aplicaciones reales;
- NO apagar Windows.

Al terminar:

```text
PRUEBA COMPLETADA

El apagado se habría ejecutado correctamente.
```

Debe existir una indicación visible mientras el modo está activo:

```text
MODO DE PRUEBA — La PC no se apagará
```

El botón principal puede cambiar a:

```text
INICIAR PRUEBA
```

cuando este modo esté habilitado.

---

# 18. Configuración persistente

Utilizar:

```text
settings.ini
```

para almacenar preferencias simples.

Valores iniciales previstos:

```ini
[General]
last_time_minutes=60

[Window]
x=
y=

[Testing]
test_mode=false
```

Opcionalmente se pueden guardar otros valores simples si aparece una necesidad real durante el desarrollo.

---

# 19. Posición de ventana

Guardar la última posición válida de la ventana.

Al iniciar:

- intentar restaurarla en esa posición;
- comprobar que siga estando dentro de un área visible de pantalla;
- si la posición guardada no es válida, usar una posición centrada o segura.

Esto evita que una configuración anterior con otro monitor deje la ventana fuera de pantalla.

---

# 20. Estado del timer y persistencia

NO guardar un timer activo para retomarlo después de cerrar la aplicación o reiniciar Windows.

Al abrir la aplicación:

- siempre comenzar sin timer activo;
- recuperar únicamente preferencias;
- nunca asumir que debe continuar un apagado anterior.

---

# 21. Configuración inicial predeterminada

Primera ejecución:

```text
Tiempo: 60 minutos
Modo de prueba: desactivado
```

La última selección válida de tiempo debe recordarse para la siguiente ejecución.

---

# 22. Consumo de recursos

La aplicación debe permanecer liviana.

Durante la espera del timer:

- consumo de CPU prácticamente despreciable;
- sin loops intensivos;
- sin animaciones innecesarias;
- sin dependencias pesadas;
- sin actividad de red.

No agregar frameworks externos salvo necesidad real y aprobación explícita.

---

# 23. Seguridad

No realizar operaciones destructivas fuera del apagado previsto.

No cerrar por fuerza bruta procesos del sistema de manera indiscriminada.

No modificar:

- registro de Windows;
- políticas del sistema;
- tareas programadas;
- configuración de energía;
- archivos del usuario

salvo que una etapa futura lo requiera explícitamente.

---

# 24. Logs

En la primera versión no es necesario implementar un sistema complejo de logging técnico.

`log.md` corresponde al historial de desarrollo del proyecto y debe mantenerse según `AGENTS.md`.

Si durante el desarrollo surge necesidad de un log de ejecución separado para diagnóstico, debe evaluarse antes de agregarlo.

---

# 25. Empaquetado final

Cuando la aplicación Python se considere estable:

- generar una versión EXE standalone;
- preferentemente mediante PyInstaller;
- evitar ventana de consola;
- verificar ejecución en Windows 10 y Windows 11;
- comprobar que `settings.ini` se cree y lea en una ubicación adecuada.

El empaquetado NO forma parte de las primeras etapas de desarrollo.

---

# 26. Criterios de funcionamiento de v0.1

La v0.1 podrá considerarse funcional cuando:

- la aplicación abra correctamente;
- la interfaz sea legible en Full HD;
- funcione con escala de Windows 100% y 125%;
- la ventana tenga tamaño fijo;
- pueda minimizarse;
- el timer continúe minimizado;
- permita seleccionar tiempos rápidos;
- permita tiempo personalizado;
- Pausa funcione;
- Continuar funcione;
- Cancelar funcione;
- `+15 min` funcione;
- `+30 min` funcione;
- la advertencia de 60 segundos funcione;
- la ventana se restaure automáticamente desde minimizada;
- Modo de prueba funcione sin apagar la PC;
- settings.ini recuerde las preferencias previstas;
- el cierre de la app con timer activo solicite confirmación;
- el apagado real funcione;
- Chrome y aplicaciones comunes tengan oportunidad razonable de cerrarse correctamente;
- la PC termine apagándose si el usuario no cancela.

---

# 27. Estrategia de pruebas

Las pruebas deben realizarse progresivamente.

## Nivel 1 — Pruebas sin apagado

Utilizar Modo de prueba para verificar:

- interfaz;
- contador;
- selección de tiempo;
- tiempo personalizado;
- pausa;
- continuar;
- sumar tiempo;
- cancelar;
- minimizar;
- restaurar;
- advertencia final;
- comportamiento al cerrar ventana;
- lectura/escritura de settings.ini.

Estas pruebas pueden repetirse tantas veces como sea necesario.

---

## Nivel 2 — Apagado real controlado

Realizar en una PC secundaria.

Usar un tiempo personalizado corto, por ejemplo:

```text
2 minutos
```

Abrir previamente algunas aplicaciones representativas:

- Chrome;
- Explorador;
- FXSound.

Verificar:

- advertencia al minuto;
- cierre ordenado;
- apagado final.

---

## Nivel 3 — Prueba de uso real

Simular el escenario nocturno:

- Chrome reproduciendo YouTube o video;
- FXSound activo si corresponde;
- aplicación minimizada;
- timer real.

Dejar que:

- llegue a la advertencia final;
- restaure la ventana;
- llegue a cero;
- cierre;
- apague Windows.

Luego de volver a iniciar la PC verificar especialmente:

- que Chrome no informe cierre incorrecto;
- que no existan síntomas de cierre forzado innecesario;
- que settings.ini conserve correctamente las preferencias.

---

# 28. Etapas de desarrollo

El proyecto debe desarrollarse por pasos pequeños.

Codex no debe implementar etapas futuras antes de que el usuario lo solicite.

---

## PASO 1 — Base del proyecto e interfaz estática

Objetivo:

Crear la primera estructura funcional sin ejecutar todavía apagados reales.

Implementar:

- `pc_night_timer.py`;
- comentario de versión;
- ventana principal Tkinter;
- tamaño fijo aproximado 850×600;
- tema oscuro;
- layout principal;
- nombre PC Night Timer;
- selector de tiempos rápidos;
- opción Personalizado;
- campos de horas/minutos personalizados;
- control de Modo de prueba;
- botón Iniciar;
- diseño del estado de timer activo;
- contador visual;
- botones Pausa, Cancelar, +15 min y +30 min;
- estructura visual de advertencia final.

En esta etapa:

- el timer puede todavía no estar completamente funcional;
- no cerrar aplicaciones;
- no ejecutar shutdown;
- no implementar PyInstaller.

Objetivo principal: validar visualmente layout, tamaño, legibilidad y organización.

---

## PASO 2 — Timer funcional

Implementar:

- cuenta regresiva real;
- actualización de `HH:MM:SS`;
- tiempos rápidos;
- tiempo personalizado;
- validaciones;
- Pausa;
- Continuar;
- Cancelar;
- +15 min;
- +30 min;
- transición entre estado de configuración y estado activo.

Todavía sin apagado real.

---

## PASO 3 — Ventana y comportamiento del último minuto

Implementar:

- funcionamiento correcto minimizado;
- restauración automática al llegar a 60 segundos;
- traer ventana al frente;
- estado visual de advertencia final;
- cancelación desde advertencia;
- control correcto al intentar cerrar la aplicación con timer activo.

---

## PASO 4 — settings.ini

Implementar:

- creación automática si no existe;
- lectura;
- escritura;
- último tiempo seleccionado;
- Modo de prueba;
- posición de ventana;
- validación de posición guardada.

No persistir timer activo.

---

## PASO 5 — Modo de prueba completo

Implementar flujo completo simulado:

- timer;
- advertencia;
- llegada a cero;
- preparación simulada;
- mensaje de prueba completada.

Garantizar:

- no cerrar aplicaciones;
- no ejecutar apagado;
- modo claramente identificado visualmente.

---

## PASO 6 — Investigación e implementación de cierre ordenado

Analizar y seleccionar el mecanismo apropiado para Windows.

Objetivo:

- dar oportunidad a aplicaciones normales de cerrarse correctamente;
- evitar matar Chrome innecesariamente;
- evitar cerrar procesos indiscriminadamente;
- mantener la garantía de apagado final.

Implementar únicamente después de revisar el comportamiento y riesgos.

---

## PASO 7 — Apagado real

Integrar el apagado real de Windows.

Realizar primero pruebas controladas en PC secundaria.

Verificar:

- apagado completo;
- ausencia de bloqueos;
- comportamiento con Chrome;
- comportamiento con Explorer;
- comportamiento con FXSound;
- resultado al siguiente inicio.

---

## PASO 8 — Ajustes visuales y UX

Basado en pruebas reales con el televisor:

- tamaño final de ventana;
- tipografías;
- tamaño del contador;
- colores;
- espaciados;
- visibilidad a distancia;
- comportamiento con escala Windows 125%.

No hacer rediseños amplios si la interfaz ya funciona correctamente.

---

## PASO 9 — Empaquetado EXE

Una vez estable:

- generar EXE standalone;
- sin consola;
- probar ejecución desde una carpeta normal;
- probar lectura/escritura de settings.ini;
- comprobar funcionamiento en Windows 10/11 si es posible;
- documentar proceso de generación.

---

## PASO 10 — Cierre de v0.1

Realizar:

- prueba final completa;
- actualización de `log.md`;
- copia final en `old_versions/`;
- revisión de versión interna;
- limpieza de archivos temporales de desarrollo;
- documentación mínima de uso.

No agregar nuevas funciones durante esta etapa salvo correcciones necesarias.

---

# 29. Posibles funciones futuras

No implementar en v0.1.

Ideas reservadas:

- Suspender;
- Hibernar;
- selector de acción;
- programación por hora exacta;
- bandeja del sistema;
- acceso directo con preset;
- sonido opcional de advertencia;
- presets adicionales;
- inicio automático con Windows;
- tema configurable;
- temporizador mediante parámetros de línea de comandos.

Estas funciones deberán evaluarse individualmente antes de incorporarse.

---

# 30. Principio de desarrollo

PC Night Timer debe mantenerse como una herramienta pequeña y confiable.

Ante dos soluciones equivalentes:

- preferir la más simple;
- preferir la que agregue menos dependencias;
- preferir cambios localizados;
- evitar arquitectura innecesariamente compleja;
- no agregar funciones por iniciativa propia.

La prioridad de la v0.1 es:

```text
Configurar → Iniciar → Esperar → Advertir → Apagar.
```
