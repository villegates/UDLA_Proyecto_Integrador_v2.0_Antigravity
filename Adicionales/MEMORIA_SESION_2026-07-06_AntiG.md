# 🧠 Memoria de Sesión — Validación repo grupal + PPT final (Proyecto Integrador DPL1046)

**Fecha:** 04-jul-2026 · **Curso:** DPL1046 — Diplomado en Ingeniería de Datos con Python, UDLA (Prof. Juan Manuel Rozas)
**Equipo:** Mijael Inostroza · Ashley Toloza · Felipe Vallejos · Pablo Villegas · **Presentan: martes 07-07-2026** (10-12 min + 5 Q&A)

> **Para replicar en otra cuenta/IA:** todo lo necesario está en esta memoria + el repo público
> `https://github.com/ashley-toloza/pipeline-analisis-pagos` (commit validado: `04443f3`) — los CSVs de Olist
> (~32 MB) vienen commiteados en el repo, así que un `git clone` basta. No hay insumos no descargables.
> Entregables de esta sesión (acompañan a esta memoria en `Proyecto\Claude\`):
> `VALIDACION_pipeline-analisis-pagos_2026-07-04.md` y `Presentacion_Final_Pipeline_Pagos_Claude.html` (la PPT FINAL, corregida).

---

## 1. Contexto (resumen de la sesión 30-jun, para autosuficiencia)

- Proyecto Integrador = **Examen 100%** del curso. Pipeline ETL local en Python sobre dataset Olist.
- Rúbrica: Funcionalidad 35% / Calidad código 30% / Buenas prácticas 15% / Presentación y valor 20%.
- Checklist del profe (clase 8): pipeline corre completo con 1 comando · ≥2 fuentes reales · tests en verde ·
  README claro · no duplica al re-correr · presentación con su template HTML · explicar cualquier parte del código.
- En sesión 30-jun se había arreglado una versión propia (v2.0 Claude, repo
  `villegates/UDLA_Proyecto_Integrador_v2.0_Claude`): 5 tests, output/ fuera de git, hallazgo 3 calculated.
  **El grupo NO incorporó esos fixes**: la entrega oficial es otro codebase (de Ashley) que evolucionó
  (merge con customers, loguru, auditoría SQL) pero **reintrodujo los mismos errores ya corregidos**.

## 2. Qué se hizo en esta sesión (04-jul)

1. **Validación completa del repo grupal** contra la rúbrica/checklist de clase-08 y cobertura de clases 1–7:
   clon fresco + lectura de todo el código + ejecución real (`main.py` y `pytest`).
2. **Informe** → `VALIDACION_pipeline-analisis-pagos_2026-07-04.md` (misma carpeta).
3. **PPT final en HTML** → `Presentacion_Final_Pipeline_Pagos_Claude.html`: copia de la del repo (17 slides,
   template UDLA del profe) con 3 correcciones de texto (ver §5).
4. Memoria interna de Claude actualizada (equipo real, repo oficial, hallazgos).
5. En curso al cierre: reemplazar el contenido de `villegates/UDLA_Proyecto_Integrador_v2.0_Claude` por lo de esta
   sesión (proyecto grupal validado + entregables Claude; v2.0 del 30-jun queda en el historial git).

## 3. Resultado de la validación — cifras exactas (para verificar réplica)

**Entorno:** Python 3.13.5, venv del diplomado (`diplomado-idsdata-juanmarozas\.venv`). **OJO:** le faltaban
`pytest` y `pyyaml` → los instalé (`pip install pytest pyyaml`). En la máquina de la demo: `pip install -r requirements.txt`.

- Tests: **3/3 PASSED** (`test_aislamiento_datos_sucios`, `test_filtrado_ordenes_canceladas`,
  `test_comportamiento_tipos_y_columnas`) en 2.57s, pytest 9.1.1.
- Pipeline (tras borrar `output/`): corre completo. 11 filas de pagos aisladas (montos ≤0 / cuotas <1);
  órdenes 98.816 válidas de 99.441 (excluye 625 `canceled`); API viva: 1 USD = $921,70 CLP × factor 0,19
  → 1 BRL ≈ $175,12 CLP (fallback si API cae: 180,0).
- Top estado: São Paulo — 43.267 transacciones, 5.942.338,42 BRL, 1.040.640.131 CLP.
- Método dominante: credit_card — 76.349 transacciones, 78,4% del monto.
- `ordenes_criticas.csv`: **640 filas, TODAS `unavailable`, 0 canceladas** (ver hallazgo C4).
- Segunda corrida de `main.py`: se detiene por el guard ("El reporte ejecutivo ya existe").
- Cobertura clases 1–7: **completa** (GitHub c1 · funciones/contratos c3 · API+.env c4 · pandas merge/groupby/crosstab c5 ·
  logging/config/robustez c6 · API→SQLite+SQL+slide IA c7). La rúbrica no exige IA ni cloud aparte.

## 4. Los 4 hallazgos críticos (detalle completo en el informe)

| # | Hallazgo | Fix recomendado |
|---|---|---|
| C1 | `output/` commiteado → **en clon fresco `python main.py` es NO-OP** (guard de "idempotencia" en `main.py:69`). Primera impresión del profe = pipeline no hace nada. | Sacar `output/` de git; idealmente borrar el guard (`main.py:68-72`) — la idempotencia real ya la da `to_sql(if_exists="replace")` + `to_csv` que sobreescribe. |
| C2 | **`.env` con token commiteado en GitHub público** (`API_AUTH_TOKEN="oll_live_..."`). Además el token es decorativo: no se usa en el código y mindicador.cl no requiere auth. | Borrar del repo, `.gitignore`. Darle rol real al `.env` (p.ej. `API_URL=`). El token queda en el historial — si fuera real habría que rotarlo. |
| C3 | **No hay `.gitignore`**: data/ (32 MB), `__pycache__`, `pipeline.log`, `.Rhistory`, `.env` versionados. README miente ("data/ ... Ignorados en Git"). | Ver comandos abajo. |
| C4 | **"640 órdenes críticas (canceladas o no disponibles)" es falso**: `transform.py:70` elimina todas las canceladas antes del merge → las 640 son solo `unavailable`. | (a) construir `ordenes_criticas` desde `df_orders` original (~625 canceled + 640 unavailable), o (b) corregir la narrativa a "no disponibles" (aplicado en la PPT corregida). |

**Comandos del fix C2+C3:**
```bash
git rm -r --cached data output src/__pycache__ tests/__pycache__ .env pipeline.log .Rhistory
