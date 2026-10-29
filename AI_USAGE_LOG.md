# AI Usage Log — ADA-08 Agent-Ready Repository


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

### Entrada 2: Auditoría inicial y evidencia BEFORE
* **Etapa:** Repository Readiness Audit BEFORE y ejecución BEFORE
* **Qué propuso la IA:**
  - Revisó el diff del agente BEFORE.
  - Corrigió la interpretación del documento `results/before-agent-run.md`.
  - Señaló como observación de seguridad el uso de `git stash` / `git stash pop` sin una regla que lo cubriera.
* **Qué decisión tomó el estudiante:**
  - Realizó y calificó por su cuenta la auditoría BEFORE (49/100).
  - Ajustó el reporte BEFORE: registró el modelo usado y dejó solo `README.md` como cambio fuera de alcance, considerando la matriz de trazabilidad como parte de la tarea.
* **Qué cambió en el producto:**
  - Evidencia BEFORE conservada en la rama `ada08-before` (resultado: PASS).

---

### Entrada 3: Diseño de AGENTS.md, CLAUDE.md y REPO_MAP.md
* **Etapa:** Mejoras Context y Navigation
* **Qué propuso la IA:**
  - Reescribir `AGENTS.md` con Read First, Sources of Truth, Repository Map, Standard Commands, Change Rules, Stop Conditions y Definition of Done, sin copiar requisitos.
  - Un `CLAUDE.md` mínimo que solo apunte a `AGENTS.md`.
  - Reglas explícitas: actualizar `README.md` solo si cambia el contrato público de la API; actualizar `docs/tracebility.md` cuando se afecte un requisito; prohibir comandos git que alteran estado sin aprobación.
* **Qué decisión tomó el estudiante:**
  - Definió las reglas y los criterios necesarios para realizar las modificaciones a los archivos.
* **Qué cambió en el producto:**
  - Mejoras I-01, I-02 e I-03 en la rama `ada08-after` (commit `385f58c`).

---

### Entrada 4: Guardrail automatizado
* **Etapa:** Mejoras Executable Knowledge y Guardrail (I-04, I-05)
* **Qué propuso la IA:**
  - `scripts/verify_repo.sh` como contrato único (pruebas + check de contrato).
  - `scripts/check_repo_contract.py` con cuatro checks: archivos esenciales, rutas protegidas con override humano `ALLOW_PROTECTED_CHANGES=1`, archivos prohibidos versionados (`.env`, llaves, `data/*.json`) y rutas citadas en la documentación.
* **Qué decisión tomó el estudiante:**
  - Convertir la regla "no modificar fuentes de verdad ni evidencia" en un check determinista en lugar de dejarla como instrucción.
* **Qué cambió en el producto:**
  - Las reglas críticas de `AGENTS.md` pasaron de lenguaje natural a restricciones observables.

---

### Entrada 5: CI como contrato compartido
* **Etapa:** Mejora CI Check (I-06)
* **Qué propuso la IA:**
  - `.github/workflows/verify.yml`, que instala dependencias y ejecuta el mismo `scripts/verify_repo.sh`, sin duplicar lógica.
* **Qué decisión tomó el estudiante:**
  - Compartir entre humano, agente y CI exactamente las mismas verificaciones (pruebas + contrato del repositorio) para que la validación no dependa de una conversación con el agente.
  - Aceptar como limitación conocida que el check de rutas protegidas no aporta en CI porque compara contra `HEAD`.
* **Qué cambió en el producto:**
  - Un solo contrato de verificación para las tres partes.
