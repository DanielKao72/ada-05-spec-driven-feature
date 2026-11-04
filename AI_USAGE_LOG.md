# AI Usage Log — ADA-09 Agentic Code Review

### Entrada 1: Definición del Change Request (CR-002)
* **Etapa:** Selección del cambio y preparación de `CHANGE_REQUEST.md`
* **Qué propuso la IA:**
  - Primero propuso un bug fix como cambio. El detalle se registrará al cerrar la revisión, para no influir en el reviewer.
  - Después propuso paginar `GET /api/v1/customers` con `limit` y `offset`, partiendo de la pregunta abierta Q-01, y redactó FR-09 y AC-13 a AC-18.
  - Detectó que el PR #2 ya usa FR-07, FR-08, AC-08 a AC-12, T-07 y TS-11 a TS-16, y eligió otros identificadores para evitar colisiones.
* **Qué decisión tomó el estudiante:**
  - Descartó el bug fix como cambio de esta actividad y pidió una funcionalidad nueva, aunque hubiera que modificar los documentos del agente.
  - Eligió paginar solo el listado, con `limit` de 1 a 100 y sin valor por defecto, y un PR hacia `ada08-after`.
* **Qué cambió en el producto:**
  - Se actualizaron `REQUIREMENTS.md`, `SPEC.md`, `ARCHITECTURE.md`, `TASKS.md`, `AGENTS.md`, `docs/REPO_MAP.md` y `scripts/check_repo_contract.py`, sin tocar `app/` ni `tests/`.
