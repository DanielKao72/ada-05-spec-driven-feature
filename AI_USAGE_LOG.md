# AI Usage Log — ADA-08 Agent-Ready Repository

Registro del uso de IA durante ADA-08. Asistente de apoyo: Claude Code (Opus 5.5) en una sesión separada de las ejecuciones BEFORE y AFTER, que se realizaron en sesiones limpias con el prompt oficial.

---

### Entrada 1: Selección de la tarea controlada (CR-001)
* **Etapa:** Definición de `TASK_UNDER_TEST.md`
* **Qué propuso la IA:**
  - Descartó las opciones "agregar filtro", "agregar campo" y "modificar endpoint" porque exigían requisitos que no existen en `REQUIREMENTS.md`/`SPEC.md`, lo que viola la regla "Do not invent business requirements".
  - Detectó un bug real: `_read_raw_data` atrapaba `JSONDecodeError` y devolvía `[]`, contradiciendo SPEC › Error Handling (HTTP 500 + logging) y provocando pérdida de datos en `POST`.
  - Propuso criterios de aceptación CR-001-AC-01..AC-05 derivados de SPEC y NFR-01.
* **Qué decisión tomó el estudiante:**
  - Aceptó la tarea "corregir un bug con criterio de aceptación conocido".
  - Pidió que el documento estuviera en inglés (convención de idioma del ADA) y que se agregaran criterios de aceptación explícitos.
* **Qué cambió en el producto:**
  - Se creó `TASK_UNDER_TEST.md` (CR-001) sin redefinir requisitos, citando NFR-01, FR-05, FR-06 y SPEC › Error Handling.

---

### Entrada 2: Baseline y aislamiento de la ejecución BEFORE
* **Etapa:** Protocolo experimental
* **Qué propuso la IA:**
  - Commit de `TASK_UNDER_TEST.md` y un tag fijo (`ada08-baseline-v1`) en lugar de depender solo de la rama `ada08-baseline`.
  - Sacar del repositorio `REPOSITORY_READINESS_AUDIT.md` y el PDF del ADA durante el BEFORE, porque el agente habría leído la lista de fricciones como pista.
* **Qué decisión tomó el estudiante:**
  - Aceptó ambas propuestas y pidió que los commits tuvieran solo su usuario como autor, sin co-autoría de la IA.
* **Qué cambió en el producto:**
  - Baseline común `3fef64c` (27 pruebas en verde); ramas `ada08-before` y `ada08-after` derivadas del mismo tag.

---

### Entrada 3: Auditoría inicial y evidencia BEFORE
* **Etapa:** Repository Readiness Audit BEFORE y ejecución BEFORE
* **Qué propuso la IA:**
  - Revisó el diff del agente BEFORE y reejecutó las pruebas de forma independiente (35 en verde).
  - Redactó `results/before-agent-run.md` y corrigió una interpretación: las 7 solicitudes de permiso del agente no son "clarification questions".
  - Señaló como observación de seguridad el uso de `git stash` / `git stash pop` sin una regla que lo cubriera.
* **Qué decisión tomó el estudiante:**
  - Realizó y calificó por su cuenta la auditoría BEFORE (49/100).
  - Ajustó el reporte BEFORE: registró el modelo usado y dejó solo `README.md` como cambio fuera de alcance, considerando la matriz de trazabilidad como parte de la tarea.
* **Qué cambió en el producto:**
  - Evidencia BEFORE conservada en la rama `ada08-before` (resultado: PASS).

---

### Entrada 4: Discoverability y conocimiento implícito
* **Etapa:** Identificación de conocimiento tribal
* **Qué propuso la IA:**
  - IK-01: comando oficial de pruebas (README decía `pytest`, el agente usó `python -m pytest`, no había script de verificación).
  - IK-02: qué documentación actualizar en cada cambio.
  - IK-03: operaciones git permitidas y rutas protegidas.
* **Qué decisión tomó el estudiante:**
  - Aceptó los tres hallazgos y que IK-01 e IK-03 se convirtieran en verificaciones ejecutables, mientras IK-02 quedara como regla documentada porque no puede decidirse de forma determinista.
* **Qué cambió en el producto:**
  - `results/implicit-knowledge.md` con la remediación de cada hallazgo.

---

### Entrada 5: Diseño de AGENTS.md, CLAUDE.md y REPO_MAP.md
* **Etapa:** Mejoras Context y Navigation (I-01, I-02, I-03)
* **Qué propuso la IA:**
  - Reescribir `AGENTS.md` con Read First, Sources of Truth, Repository Map, Standard Commands, Change Rules, Stop Conditions y Definition of Done, sin copiar requisitos.
  - Un `CLAUDE.md` mínimo que solo apunte a `AGENTS.md`.
  - `docs/REPO_MAP.md` con entry points, límites entre capas, inventario de pruebas, guía de cambios y rutas protegidas, cuidando no describir la solución de CR-001.
  - Reglas explícitas: actualizar `README.md` solo si cambia el contrato público de la API; actualizar `docs/tracebility.md` cuando se afecte un requisito; prohibir comandos git que alteran estado sin aprobación.
* **Qué decisión tomó el estudiante:**
  - Aceptó las reglas de documentación y de git.
  - Rechazó agregar un linter (`ruff`) para no introducir una dependencia nueva; lint quedó como "Not configured".
* **Qué cambió en el producto:**
  - Mejoras I-01, I-02 e I-03 en la rama `ada08-after` (commit `385f58c`).

---

### Entrada 6: Guardrail automatizado
* **Etapa:** Mejoras Executable Knowledge y Guardrail (I-04, I-05)
* **Qué propuso la IA:**
  - `scripts/verify_repo.sh` como contrato único (pruebas + check de contrato).
  - `scripts/check_repo_contract.py` con cuatro checks: archivos esenciales, rutas protegidas con override humano `ALLOW_PROTECTED_CHANGES=1`, archivos prohibidos versionados (`.env`, llaves, `data/*.json`) y rutas citadas en la documentación.
  - `.gitattributes` para que el `.sh` conserve finales LF en Windows.
* **Qué decisión tomó el estudiante:**
  - Convertir la regla "no modificar fuentes de verdad ni evidencia" en un check determinista en lugar de dejarla como instrucción.
  - Validar el guardrail: una edición de prueba a `SPEC.md` produjo `Protected path modified: SPEC.md`. El check también detectó una referencia a `REPOSITORY_READINESS_AUDIT.md`, que aún no existía en la rama, y se agregó a las rutas opcionales.
* **Qué cambió en el producto:**
  - Las reglas críticas de `AGENTS.md` pasaron de lenguaje natural a restricciones observables.

---

### Entrada 7: CI como contrato compartido
* **Etapa:** Mejora CI Check (I-06)
* **Qué propuso la IA:**
  - `.github/workflows/verify.yml`, que instala dependencias y ejecuta el mismo `scripts/verify_repo.sh`, sin duplicar lógica.
* **Qué decisión tomó el estudiante:**
  - Compartir entre humano, agente y CI exactamente las mismas verificaciones (pruebas + contrato del repositorio) para que la validación no dependa de una conversación con el agente.
  - Aceptar como limitación conocida que el check de rutas protegidas no aporta en CI porque compara contra `HEAD`.
* **Qué cambió en el producto:**
  - Un solo contrato de verificación para las tres partes.

---

### Entrada 8: Ejecución AFTER
* **Etapa:** Ejecución AFTER y verificación independiente
* **Qué propuso la IA:**
  - Revisó el diff del agente AFTER y reejecutó `verify_repo.sh` (36 pruebas, `VERIFY_REPO: PASS`).
  - Como el agente AFTER no pudo demostrar que sus pruebas fallan sin el arreglo (la nueva regla de git lo impedía), verificó esto fuera del repositorio con `git archive HEAD`: 7 pruebas fallaron (AC-01..AC-04) y 2 pasaron (regresiones AC-05).
  - Redactó `results/after-agent-run.md` con los mismos encabezados que el BEFORE.
* **Qué decisión tomó el estudiante:**
  - Confirmó que el agente pidió los mismos permisos que en el BEFORE, excepto `git stash`.
  - Hizo commit de los cambios del agente AFTER.
* **Qué cambió en el comportamiento del agente:**
  - Usó solo comandos documentados, citó `AGENTS.md` y `REPO_MAP.md`, justificó cada cambio de documentación con una regla, anotó cada prueba con su ID de AC y no ejecutó operaciones git que alteraran estado.

---

### Entrada 9: Evaluación final y límites que requieren intervención humana
* **Etapa:** Repository Readiness Audit AFTER e informe de impacto
* **Qué propuso la IA:**
  - Calificación AFTER conservadora con el gap restante de cada dimensión: 83/100 (delta +34).
  - `results/readiness-improvement-report.md` con indicadores, mejoras clasificadas, amenazas a la validez y gaps restantes.
* **Qué decisión tomó el estudiante:**
  - Revisó y ajustó la auditoría AFTER y el informe antes del commit.
* **Limitaciones que siguen requiriendo intervención humana:**
  - Cambios a `REQUIREMENTS.md`/`SPEC.md` y aprobación de cambios en rutas protegidas.
  - Mensajes de error visibles al usuario que SPEC no define (ambos agentes eligieron el cuerpo del 500 por su cuenta).
  - Demostrar que una prueba falla sin el arreglo: la regla de git hizo al agente más seguro, pero le quitó esa forma de producir evidencia.
  - El override `ALLOW_PROTECTED_CHANGES=1` es una variable de entorno, no una aprobación auditada.
