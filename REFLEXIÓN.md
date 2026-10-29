# Reflexión individual

### 1. ¿Cuál fue el principal obstáculo para el agente en la ejecución BEFORE?
El principal obstáculo no fue entender el bug, sino la falta de un proceso exacto y seguro. El agente corrigió CR-001 correctamente, pero tuvo que decidir por su cuenta tres cosas que el repositorio no le decía: qué comando usar para validar (el README decía `pytest` y él usó `python -m pytest`), qué documentación actualizar (editó `README.md` y la matriz de trazabilidad sin una regla que lo pidiera) y si podía usar `git stash` para probar contra el código original. El resultado fue PASS, pero cada una de esas decisiones dependió del criterio del agente y no del repositorio.

### 2. ¿Qué información tuvo que inferir el agente que un desarrollador experimentado ya conocía?
Las tres que registré en `results/implicit-knowledge.md`: el comando oficial de verificación (IK-01), qué documentos se actualizan con cada tipo de cambio (IK-02) y qué operaciones de git están permitidas y qué rutas no se tocan, como `data/`, `REQUIREMENTS.md` o `SPEC.md` (IK-03). Alguien que ya trabajó en el proyecto lo sabe sin pensarlo, pero ninguna de esas tres cosas estaba escrita en el repositorio.

### 3. ¿Qué mejora produjo el mayor impacto y por qué?
La combinación de `AGENTS.md` con `scripts/verify_repo.sh`. `AGENTS.md` eliminó las decisiones que el agente tomaba por intuición (comandos, alcance de la documentación, uso de git) y `verify_repo.sh` le dio una definición de "terminado" que se comprueba con un solo comando. En el AFTER el agente citó esas reglas para justificar cada cambio y terminó con `VERIFY_REPO: PASS`. Esa es la diferencia más visible que noté entre las dos ejecuciones.

### 4. ¿Qué información pertenece en AGENTS.md y qué información NO debería vivir ahí?
Debería estar qué leer primero, cuál es la fuente de verdad de cada tipo de información, los comandos oficiales, las reglas de cambio, las stop conditions y el Definition of Done. Por otro lado, lo que no debería estar ahí serían los requisitos, los criterios de aceptación, el detalle de la arquitectura ni la solución de una tarea concreta. Eso ya está en `REQUIREMENTS.md`, `SPEC.md` y `ARCHITECTURE.md`; si lo copio en `AGENTS.md` creo una segunda fuente de verdad que tarde o temprano se va a desincronizar.

### 5. ¿Qué regla convertiste en software/hook/script en lugar de dejarla como instrucción?
La regla de no modificar fuentes de verdad, evidencia ni guardrails. `scripts/check_repo_contract.py` detecta cambios en rutas protegidas (`REQUIREMENTS.md`, `SPEC.md`, `TASK_UNDER_TEST.md`, `results/`, `scripts/`, `.github/`, `data/`) y falla salvo que un humano lo apruebe con `ALLOW_PROTECTED_CHANGES=1`. Lo comprobé editando `SPEC.md`: el check respondió `Protected path modified: SPEC.md`. El mismo script también bloquea que se versionen `.env`, llaves o `data/*.json`, y verifica que la documentación no apunte a rutas inexistentes.

### 6. ¿Qué diferencia observaste entre 'más contexto' y 'mejor contexto'?
El repositorio BEFORE ya tenía mucho contexto: README extenso, `ARCHITECTURE.md` con diagramas, `SPEC.md` y una matriz de trazabilidad. Aun así el agente tuvo que adivinar. Lo que faltaba no era más texto, sino respuestas directas; por ejemplo, dónde cambio esto, con qué lo valido, qué no toco. Las mejoras fueron archivos cortos y estructurados, y algunas reglas se convirtieron en scripts.

### 7. ¿Qué riesgo aparece cuando CLAUDE.md/GEMINI.md/copilot instructions duplican información del proyecto?
Se crean varias fuentes de verdad que se desincronizan con el tiempo. Si `CLAUDE.md` repite un comando o una regla y luego cambia `AGENTS.md`, cada agente trabajará con una versión distinta del proyecto, y un humano no sabrá cuál es la correcta. Por eso dejé `CLAUDE.md` como un adaptador de pocas líneas que solo remite a `AGENTS.md` y pide ejecutar `verify_repo.sh`.

### 8. ¿Qué checks comparten ahora el agente, el desarrollador humano y CI?
Los mismos dos pasos de `scripts/verify_repo.sh`: la suite completa de pruebas (`python -m pytest -q`) y el contrato del repositorio (`check_repo_contract.py`). El agente lo ejecuta por instrucción de `AGENTS.md` y `CLAUDE.md`, yo lo ejecuto según el README, y `.github/workflows/verify.yml` lo ejecuta en cada push y pull request. La lógica vive en un solo lugar, así que no hay forma de que la validación del agente y la de CI no coincidan.

### 9. ¿Qué parte del proceso sigue requiriendo decisión humana?
Cambiar requisitos o especificación, aprobar cambios en rutas protegidas, definir mensajes de error que SPEC no especifica (los dos agentes eligieron el cuerpo de la respuesta 500 por su cuenta), decidir si una actualización de documentación está dentro del alcance y producir cierta evidencia. En el AFTER, la regla de git impidió que el agente demostrara que sus pruebas fallan sin el arreglo, y tuve que hacerlo yo con `git archive`. También la calificación de la auditoría es un juicio mío, aunque esté respaldado por evidencia.

### 10. ¿Qué evidencia demuestra que el AFTER es realmente mejor?
Ambas ejecuciones terminaron en PASS, así que la diferencia está en el proceso, no en el resultado. En el AFTER el agente no tuvo que inferir comandos, no modificó archivos fuera de alcance, no ejecutó operaciones de git que alteran el estado (pidió 6 permisos contra 7 del BEFORE, sin `git stash`), justificó cada cambio de documentación con una regla del repositorio, anotó cada prueba con su ID de criterio de aceptación y validó con el contrato completo (`VERIFY_REPO: PASS`, 36 pruebas). En la auditoría el score subió de 49 a 83. La comparación es válida porque ambas ramas parten del mismo tag `ada08-baseline-v1`, con la misma tarea, el mismo prompt y el mismo agente y modelo.

### 11. ¿Qué mejora realizada para el agente también beneficia a un desarrollador que entra por primera vez al proyecto?
`docs/REPO_MAP.md` y el comando único `bash scripts/verify_repo.sh`. Un desarrollador nuevo puede ver en una página dónde está cada capa, qué cubre cada prueba, qué archivos no debe tocar y qué hacer según el tipo de cambio, y puede confirmar que su trabajo está completo con un solo comando que además es el mismo que corre CI. Antes tendría que haber leído el README completo y preguntado a alguien del equipo.

### 12. ¿Qué variable no controlada podría afectar tu comparación BEFORE/AFTER?
La principal es que el modelo no es determinista: aunque usé el mismo agente, modelo y prompt, las implementaciones difirieron en detalles (nombre de la excepción, cuerpo del 500, 8 contra 9 pruebas) sin relación con la preparación del repositorio. Además, diseñé las mejoras después de observar el BEFORE, así que atacan justo las fricciones de esta tarea; otra tarea podría mostrar otros gaps. 

### 13. ¿Qué elementos de este ADA conservarás como base para tu proyecto final?
El `AGENTS.md` con su estructura (Read First, Sources of Truth, Standard Commands, Change Rules, Stop Conditions, Definition of Done), el `REPO_MAP.md`, el script único de verificación con su workflow de CI y el check de contrato con rutas protegidas. También conservaré la práctica de definir tareas con criterios de aceptación verificables y de anotar cada prueba con su ID. Como mejora pendiente, quiero agregar un script de solo lectura que ejecute las pruebas nuevas contra el baseline, para que el agente pueda producir esa evidencia sin necesitar operaciones de git peligrosas.
