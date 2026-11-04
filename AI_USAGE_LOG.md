# AI Usage Log — ADA-09 Agentic Code Review

### Entrada 1: Definición del Change Request (CR-002)
* **Etapa:** Selección del cambio y preparación de `CHANGE_REQUEST.md`
* **Qué propuso la IA:**
  - Primero propuso un bug fix como cambio. El detalle se registrará al cerrar la revisión, para no influir en el reviewer.
  - Después propuso paginar `GET /api/v1/customers` con `limit` y `offset`, partiendo de la pregunta abierta Q-01, y redactó FR-09 y AC-13 a AC-18.
  - Detectó que el PR #2 ya usa FR-07, FR-08, AC-08 a AC-12, T-07 y TS-11 a TS-16, y eligió otros identificadores para evitar colisiones.
* **Qué decisión tomó el estudiante:**
  - Descarté el bug fix como cambio de esta actividad y pedí una funcionalidad nueva, aunque hubiera que modificar los documentos del agente.
  - Elegí paginar solo el listado, con `limit` de 1 a 100 y sin valor por defecto, y un PR hacia `ada08-after`.
* **Qué cambió en el producto:**
  - Se actualizaron `REQUIREMENTS.md`, `SPEC.md`, `ARCHITECTURE.md`, `TASKS.md`, `AGENTS.md`, `docs/REPO_MAP.md` y `scripts/check_repo_contract.py`, sin tocar `app/` ni `tests/`.

---

### Entrada 2: Plan del coder-agent
* **Etapa:** Fase 1, plan previo a la implementación
* **Qué propuso la IA:**
  - El coder-agent, en una sesión separada, propuso que el router validara `limit` y `offset`, el service los delegara y el repository recortara con `get_page`, además de agregar tests y actualizar `README.md` y `docs/tracebility.md`.
  - Según `results/coder-report.md`, el plan usaba el binding `int` de FastAPI y Pydantic, y advertía que acepta formas como `2.0` y `1_0`.
* **Qué decisión tomó el estudiante:**
  - Aprobé el plan tal cual, sin cambios, antes de que el agente editara archivos.
* **Qué cambió en el producto:**
  - Nada todavía; el plan autorizó la implementación de CR-002.

---

### Entrada 3: Implementación
* **Etapa:** Fase 1, implementación del candidato (`3e21ffc`)
* **Qué propuso la IA:**
  - Implementó la paginación en las tres capas y agregó 33 casos de prueba (de 36 a 69).
  - Sugirió actualizar el conteo de pruebas de NFR-03 en `docs/tracebility.md`.
  - Dejó sin corregir la entrada de `docs/REPO_MAP.md` porque el Change Request la bloqueaba, y lo declaró como limitación.
* **Qué decisión tomó el estudiante:**
  - Acepté las sugerencias del agente.
  - Hice el commit del candidato y ejecuté el Verification Gate (`VERIFY_REPO: PASS`).
* **Qué cambió en el producto:**
  - `GET /api/v1/customers` admite `limit` y `offset` opcionales; sin parámetros devuelve todos los registros.

---

### Entrada 4: Reviewer-agent
* **Etapa:** Fase 4, revisión independiente de `3e21ffc`
* **Qué propuso la IA:**
  - Reportó 0 MUST FIX, 1 SHOULD FIX y 3 OPTIONAL, y recomendó `READY FOR HUMAN REVIEW`.
  - RF-01: con 15 clientes guardados, `limit=1_0` respondía 200 con 10 registros y `limit=2.0` respondía 200 con 2, mientras que AC-17 pide 422 para valores "non-integer" sin definir el término, y ningún test fijaba ese comportamiento.
  - Comprobó la suite con 19 mutaciones, y falló en todas. También señaló que los registros mal formados en el almacenamiento devuelven un 500 en texto plano.
* **Qué decisión tomó el estudiante:**
  - Revisé el reporte y pasé a la fase de decisión humana.
* **Qué cambió en el producto:**
  - Nada; el reviewer no modificó código. Se agregaron `results/review-contract.md` y `results/review-report.md`.

---

### Entrada 5: Human review
* **Etapa:** Fase 5, decisiones sobre los findings
* **Qué propuso la IA:**
  - La sesión de planeación, que no actuó como coder ni como reviewer, recomendó una decisión para cada finding.
* **Qué decisión tomó el estudiante:**
  - Acepté las recomendaciones en los cuatro findings: RF-01 y RF-02 MODIFIED, RF-03 DEFERRED y RF-04 ACCEPTED.
  - Definí "non-integer" como un valor que el parseo de enteros de Pydantic rechaza.
  - Escribí yo mismo `results/human-review-decisions.md`.
  - Corregí yo mismo la entrada de `docs/REPO_MAP.md`, la parte de RF-02 que me correspondía.
* **Qué cambió en el producto:**
  - Ningún cambio en producción; las decisiones definieron el alcance del fix.

---

### Entrada 6: Fix cycle y re-review
* **Etapa:** Fases 6 y 7
* **Qué propuso la IA:**
  - El coder-agent, en una sesión nueva, agregó 15 casos de prueba (de 69 a 84), corrigió `README.md` y `docs/tracebility.md`, y sugirió actualizar el conteo de NFR-03 de 69 a 84, algo que iba más allá del texto de RF-02.
  - La sesión de planeación detectó que `results/pr.diff` y `results/commits.txt` no estaban actualizados antes del re-review.
  - El reviewer-agent, en otra sesión, marcó RF-01, RF-02 y RF-04 como RESOLVED, sin nuevos MUST FIX, y comprobó con mutaciones que los tests nuevos pueden fallar.
* **Qué decisión tomó el estudiante:**
  - Aprobé el plan del fix y el conteo de 84 pruebas.
  - Regeneré la evidencia antes del re-review y no reescribí los mensajes de commit, porque la evidencia cita esos hashes.
* **Qué cambió en el producto:**
  - Los tests fijan el parseo aceptado y cubren el formato paginado y `limit=100`. `app/` no cambió.
