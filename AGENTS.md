# AGENTS.md

## Propósito

Este archivo contiene las reglas generales de trabajo para los proyectos de desarrollo realizados con asistencia de agentes de IA.

Estas instrucciones son comunes a todos los proyectos y deben aplicarse salvo que el pedido actual del usuario o el archivo `DEVELOPMENT_SPEC.md` del proyecto indiquen explícitamente otra cosa.

El objetivo es mantener un proceso de desarrollo ordenado, seguro, trazable y fácil de continuar entre distintas sesiones.

---

# 1. Archivos de contexto obligatorios

Antes de modificar código o archivos del proyecto, leer completamente, si existen:

1. `AGENTS.md`
2. `DEVELOPMENT_SPEC.md`
3. `log.md`

También revisar el estado actual de los archivos involucrados antes de realizar cualquier cambio.

No trabajar únicamente basándose en información recordada de iteraciones anteriores.

El contenido real de los archivos actuales del proyecto representa el estado vigente.

---

# 2. Jerarquía de instrucciones

Aplicar las instrucciones con el siguiente orden de prioridad:

1. Pedido actual del usuario.
2. `DEVELOPMENT_SPEC.md`.
3. `AGENTS.md`.
4. Estado y arquitectura actual del proyecto.

Si el pedido actual modifica una decisión establecida anteriormente, seguir el pedido actual.

No modificar automáticamente `DEVELOPMENT_SPEC.md` para reflejar ese cambio salvo que el usuario lo solicite explícitamente.

---

# 3. DEVELOPMENT_SPEC.md

`DEVELOPMENT_SPEC.md` contiene los requisitos particulares del proyecto.

Puede incluir, entre otras cosas:

* objetivo del proyecto;
* alcance;
* tecnologías utilizadas;
* arquitectura;
* estructura de archivos;
* diseño de interfaz;
* reglas funcionales;
* decisiones técnicas;
* etapas previstas;
* restricciones;
* criterios de funcionamiento.

Debe utilizarse como fuente principal de requisitos específicos del proyecto.

No modificar `DEVELOPMENT_SPEC.md` salvo pedido explícito del usuario.

No reinterpretar, ampliar o reemplazar sus requisitos por decisiones propias.

---

# 4. Estado actual del proyecto

Los archivos actuales del proyecto tienen prioridad sobre versiones anteriores descritas en documentación histórica.

Si existe una diferencia entre:

* el código actual;
* una copia anterior;
* una entrada antigua de `log.md`;

considerar al código actual como el estado vigente.

Los cambios realizados manualmente por el usuario deben conservarse y considerarse parte válida del proyecto.

Nunca sobrescribirlos, revertirlos o reemplazarlos salvo pedido explícito.

---

# 5. Versionado del código

Todo archivo principal de código que lo permita debe incluir al comienzo una línea comentada indicando su versión actual.

Ejemplos:

HTML:

```html
<!-- Version: v0.5.1 -->
```

Python:

```python
# Version: v0.5.1
```

JavaScript:

```javascript
// Version: v0.5.1
```

CSS:

```css
/* Version: v0.5.1 */
```

Otros lenguajes deben utilizar el formato de comentario correspondiente.

La versión debe actualizarse cuando se realice una modificación relevante del código.

Como criterio general:

* cambios importantes pueden incrementar la versión menor: `v0.5` → `v0.6`;
* ajustes pequeños o correcciones pueden incrementar el parche: `v0.5` → `v0.5.1`;
* la estrategia concreta de versionado puede ser indicada por el usuario o por `DEVELOPMENT_SPEC.md`.

La versión declarada en el código debe mantenerse coherente con:

* la copia guardada en `old_versions/`;
* la entrada correspondiente en `log.md`.

No cambiar números de versión arbitrariamente si el proyecto ya utiliza una secuencia definida.

---

# 6. Copias en old_versions

Antes de realizar una modificación de código o de archivos relevantes del proyecto, guardar una copia del estado actual funcional dentro de:

```text
old_versions/
```

Las versiones deben utilizar numeración consecutiva:

```text
Ver01
Ver02
Ver03
Ver04
...
```

No sobrescribir versiones anteriores.

Si el proyecto utiliza varios archivos necesarios para funcionar, guardar una carpeta completa para cada versión.

Ejemplo:

```text
old_versions/
    Ver01/
        index.html
        style.css
        app.js
        assets/
```

Guardar el conjunto mínimo de archivos necesario para reconstruir correctamente esa versión.

En proyectos de un único archivo también puede utilizarse una carpeta por versión para mantener la misma estructura de trabajo.

No crear una nueva versión cuando solamente se analiza, consulta o explica código sin realizar modificaciones.

Antes de crear una nueva versión, comprobar cuál es la última numeración existente para continuar la secuencia correcta.

---

# 7. log.md

Si `log.md` no existe, crearlo.

Mantenerlo actualizado en cada iteración donde se realicen cambios reales en el proyecto.

El log debe registrar de forma breve y útil:

* versión;
* fecha;
* cambios realizados;
* motivo del cambio cuando sea relevante;
* archivos afectados;
* estado de prueba.

Formato recomendado:

```markdown
## Ver 07 — YYYY-MM-DD

### Cambios
- Cambio realizado.
- Corrección realizada.
- Función agregada.

### Motivo
- Razón principal del cambio.

### Archivos afectados
- index.html
- app.js

### Estado
- Probado correctamente.
```

Si algo todavía requiere prueba manual, indicarlo claramente.

Ejemplo:

```text
Estado: implementación terminada, pendiente de prueba manual.
```

No incluir en `log.md`:

* archivos completos;
* grandes bloques de código;
* diffs extensos;
* explicaciones innecesariamente largas.

El log debe funcionar como historial técnico resumido del proyecto.

---

# 8. Cambios pequeños y localizados

Preferir siempre modificaciones pequeñas, controladas y localizadas.

No reescribir archivos completos si el cambio puede realizarse modificando únicamente una parte.

No refactorizar código que no esté relacionado con el pedido actual.

No reorganizar estructuras, nombres, funciones o estilos simplemente por preferencia personal.

Mantener intacto todo lo que ya funciona y no necesita ser modificado.

---

# 9. No agregar funciones no solicitadas

No agregar por iniciativa propia:

* nuevas funcionalidades;
* librerías;
* frameworks;
* dependencias;
* archivos;
* animaciones;
* interfaces;
* configuraciones;
* sistemas auxiliares;
* cambios de arquitectura.

Si se identifica una mejora potencial que no forma parte del pedido actual, puede mencionarse como sugerencia, pero no implementarla sin autorización.

---

# 10. Mantener la tecnología existente

Respetar el stack tecnológico y la arquitectura actual del proyecto.

Ejemplos:

* si el proyecto utiliza HTML/CSS/JavaScript vanilla, no introducir un framework sin autorización;
* si utiliza Tkinter, no migrarlo a otra biblioteca gráfica sin solicitud explícita;
* si utiliza una estructura de archivos determinada, mantenerla salvo necesidad real.

No realizar migraciones tecnológicas simplemente porque exista una alternativa considerada más moderna.

---

# 11. Preservar cambios manuales del usuario

El usuario puede modificar archivos manualmente entre distintas iteraciones.

Antes de trabajar, revisar siempre el contenido actual.

No asumir que el archivo sigue siendo idéntico al utilizado en una interacción anterior.

Si aparecen cambios realizados por el usuario, conservarlos.

No restaurar una versión anterior para facilitar una modificación salvo autorización explícita.

---

# 12. Archivos desconocidos

No eliminar ni modificar archivos o carpetas cuyo propósito no esté claro.

No asumir que un archivo no trackeado, temporal o aparentemente redundante puede borrarse.

Si no es necesario para la tarea actual, dejarlo intacto.

---

# 13. Git

Puede utilizarse Git para inspeccionar el estado del proyecto mediante comandos seguros como:

```bash
git status
git diff
git log
```

No ejecutar sin autorización explícita operaciones que puedan alterar significativamente el repositorio o el historial, entre ellas:

```bash
git reset --hard
git clean
git rebase
git push --force
git push --force-with-lease
```

No eliminar archivos no trackeados automáticamente.

No realizar `push` al repositorio remoto salvo que el usuario lo solicite o exista una instrucción específica que lo autorice.

Antes de operaciones Git importantes, preservar el estado actual del proyecto.

---

# 14. Pruebas después de modificar

Después de realizar cambios, ejecutar las comprobaciones razonablemente posibles.

Según el proyecto pueden incluir:

* validación de sintaxis;
* ejecución del programa;
* carga de HTML;
* comprobación de errores JavaScript;
* ejecución de Python;
* validación de JSON;
* revisión de archivos de configuración;
* pruebas automatizadas existentes.

No alterar innecesariamente el proyecto solo para realizar pruebas.

Informar claramente:

* qué fue comprobado;
* qué funcionó;
* qué no pudo comprobarse;
* qué requiere prueba manual del usuario.

Nunca afirmar que algo fue probado si no fue realmente verificado.

---

# 15. Errores encontrados fuera del pedido actual

Si durante una tarea aparece un problema importante no relacionado directamente con el cambio solicitado:

1. no realizar una modificación extensa automáticamente;
2. informar el problema;
3. explicar brevemente su impacto;
4. conservarlo para una posible tarea posterior.

Una excepción puede hacerse únicamente si el problema impide directamente completar el pedido actual y la corrección es pequeña y segura.

---

# 16. Dependencias

Evitar nuevas dependencias cuando el proyecto puede resolverse razonablemente con las herramientas existentes.

Antes de agregar una dependencia externa:

* comprobar si realmente es necesaria;
* considerar su impacto;
* evitar dependencias innecesarias para funciones simples.

No instalar paquetes, frameworks o herramientas adicionales sin una razón concreta vinculada al pedido.

---

# 17. Código legible

Mantener el estilo existente del proyecto.

El código nuevo debe ser:

* claro;
* mantenible;
* razonablemente comentado;
* consistente con el código existente.

Evitar comentarios que simplemente repitan lo que hace una línea evidente.

Utilizar comentarios principalmente para explicar lógica, decisiones o comportamientos que no sean obvios.

---

# 18. No ocultar problemas

Si una modificación no puede completarse correctamente:

* no simular que está terminada;
* no ocultar errores;
* no eliminar funcionalidad para hacer desaparecer el problema.

Explicar claramente qué parte quedó resuelta y qué parte permanece pendiente.

---

# 19. Evitar cambios masivos innecesarios

No aplicar automáticamente:

* formateadores globales;
* reorganización completa de imports;
* renombrado masivo;
* cambios generales de indentación;
* normalización completa del archivo;
* reescrituras estéticas.

Estos cambios dificultan la revisión y pueden introducir errores innecesarios.

El diff ideal debe contener principalmente los cambios requeridos por la tarea.

---

# 20. Seguridad ante operaciones destructivas

Para cualquier función que pueda:

* borrar archivos;
* modificar discos;
* sobrescribir información;
* eliminar configuraciones;
* afectar datos del usuario;

mantener protecciones existentes y evitar reducir mecanismos de seguridad.

No convertir una operación segura en una operación automática sin confirmación explícita.

---

# 21. Compatibilidad

No reducir deliberadamente la compatibilidad existente salvo que el proyecto lo requiera.

Cuando corresponda, respetar:

* sistemas operativos objetivo;
* navegadores;
* resoluciones;
* versiones de Python;
* versiones mínimas de plataformas;
* hardware previsto.

Los requisitos específicos deben encontrarse en `DEVELOPMENT_SPEC.md`.

---

# 22. Entrega de cada iteración

Al finalizar una modificación, proporcionar un resumen breve que indique:

* qué se cambió;
* qué archivos fueron modificados;
* qué versión quedó activa;
* qué pruebas se realizaron;
* si existe algo pendiente.

Evitar repetir grandes cantidades de información que ya se encuentran en `log.md`.

---

# 23. Principio general

La prioridad es mejorar el proyecto sin romper lo que ya funciona.

Ante una elección entre:

* una modificación pequeña y segura;
* una reescritura amplia que produce el mismo resultado;

preferir la modificación pequeña y segura.

Ante incertidumbre sobre una parte del proyecto que no necesita cambiarse, dejarla intacta.
