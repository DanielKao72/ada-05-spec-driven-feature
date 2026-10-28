# Repository Readiness Audit

## BEFORE

| Dimension | Score 0-5 | Weighted | Evidence | Main Gap |
|---|---:|---:|---|---|
| Entry Point & Navigation | 3 | 9/15 | `README.md` describe propósito, árbol de `app/` y `tests/`, comandos de instalación/ejecución/test y endpoints con ejemplos `curl`. | No existe `docs/REPO_MAP.md` ni guía de "dónde cambiar qué". `docs/tracebility.md` no está enlazado desde README ni AGENTS.md. |
| Agent Instructions | 2 | 6/15 | `AGENTS.md` lista documentos a leer, reglas (no inventar requisitos, no debilitar tests, no agregar dependencias) y un *Definition of Done*. | No define fuentes de verdad de forma explícita, no tiene comandos estándar (solo "Run pytest"), no incluye mapa del repo, rutas protegidas ni stop conditions más allá de "requirements conflict". |
| Build / Run / Test | 3 | 9/15 | README: `pip install -r requirements.txt`, `uvicorn app.main:app --reload --port 8000`, `pytest -v`. | No hay lint/formatter configurado, versión de Python no fijada (`3.10+`), dependencias sin pinear (`>=`) y warning de deprecación `httpx`/`starlette.testclient`. |
| Architecture Boundaries | 3 | 6/10 | `ARCHITECTURE.md` documenta capas Router → Service → Repository, responsabilidades, interfaces y diagramas Mermaid; NFR-02 exige desacoplamiento. | No indica qué NO modificar (p. ej. `data/`, contratos de respuesta, `core/config.py`). Inconsistencia doc/código: "Error Handling" afirma que JSON corrupto produce HTTP 500 con logging, pero `_read_raw_data` atrapa `JSONDecodeError` y devuelve `[]`. Los boundaries no se verifican automáticamente. |
| Requirements & Traceability | 3 | 6/10 | `SPEC.md` referencia los FR/NFR; `docs/tracebility.md` conecta requisito → AC → tarea → archivos → tests. | `TASKS.md` no referencia IDs FR/AC. La matriz está en español, con nombre incorrecto y no es descubrible; marca NFR-01 como "Implementado correctamente" pese al defecto CR-001 (fuente de verdad contradictoria). |
| Automation & Guardrails | 1 | 2/10 | Solo `.gitignore` (excluye `.env`, `data/*.json`, cachés). | No hay `scripts/`, hooks activos (solo `*.sample` en `.git/hooks`), CI (`.github/workflows` inexistente), lint ni check de contrato del repo. Todas las reglas de AGENTS.md existen solo en lenguaje natural. |
| Testability & Evidence | 3 | 9/15 | 6 archivos de tests (unit + integración) con `tmp_path` y override de dependencias en `conftest.py`; escenarios TS-01..TS-10 cubiertos; `results/agent-report.md` como evidencia previa. | README afirma "100% test coverage" sin herramienta de cobertura. No hay plantilla/ruta definida para registrar evidencia de una tarea (comandos, salida, resultado). |
| Safety & Permissions | 1 | 2/10 | `.gitignore` excluye `.env` y datos runtime (`data/*.json`); no hay secretos versionados. | Sin rutas protegidas explícitas, sin reglas sobre acciones destructivas (borrar/sobrescribir `data/customers.json`, `git push --force`) o externas, sin secret scan. El propio bug CR-001 puede sobrescribir datos sin que ninguna regla lo detecte. |

TOTAL BEFORE: 49 / 100

## Top 3 friction points:

1. **No existe un contrato de verificación ejecutable.** Sin `scripts/verify_repo.sh`, lint, hooks ni CI, el agente debe deducir que la validación es "solo `pytest`" leyendo el README; ninguna regla de `AGENTS.md` (no debilitar tests, no tocar archivos fuera de alcance, no agregar dependencias) se verifica de forma determinista.
2. **`AGENTS.md` es incompleto como contrato operativo.** No declara fuentes de verdad, comandos estándar (install/run/test/verify), mapa del repositorio, rutas protegidas (`data/`, `.env`) ni stop conditions; tampoco hay `docs/REPO_MAP.md`, por lo que el agente debe explorar todo el árbol para ubicar el punto de cambio de CR-001 (`app/repositories/json_customer_repository.py`) y sus tests.
3. **Fuentes de verdad inconsistentes y poco descubribles.** `SPEC.md` y `ARCHITECTURE.md` describen HTTP 500 + logging ante JSON corrupto, pero el código devuelve `[]`, y `docs/tracebility.md` (no enlazado, mal nombrado, en español) marca NFR-01 como implementado. El agente puede asumir que el comportamiento documentado ya existe o confiar en una matriz de trazabilidad desactualizada.
