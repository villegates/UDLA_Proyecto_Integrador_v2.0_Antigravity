# Project Memory: PreCom & TOP Dashboard Reconstruction

This document serves as the comprehensive memory of the **PreCom & TOP Control Dashboard** reconstruction project (spanning D3MC Centinela and B2SG Spence datasets) from the beginning of the sessions until the current milestone.

---

## 1. Project Overview & Context

The goal of this project is to replicate and enhance a Power BI dashboard showing **Pre-Commissioning (PreCom) and Turnover Packages (TOP)** status as an interactive, premium HTML/JS web application.

The source information resides in:
*   `D3MC Precom 20220705 Rev 04.pbix`: The source Power BI model.
*   `Copy.xlsx` & `Programa 18.07.22  Con Caminatas (ODPT Feb1)_Input.xlsx`: Excel schedules detailing subsystem dates, milestones, and revisions.
*   `tbl_P6_Data.csv`: Extracted database of P6 activities used by the Power BI queries.

---

## 2. Chronological Progress

### Phase 1: Database Extraction & Fixing Corruption
*   **Encoding Fix**: Discovered and resolved a bug in the preprocessor script (`process_pbi_data.py`) where character replacement functions (`replace("", "ó")`) were corrupting string values. Re-established native Spanish encoding support for clean text rendering.
*   **Excel Formula Evaluation**: Modified workbook loaders in auxiliary inspection scripts to load spreadsheets with `data_only=True` to resolve formulas (like `=+AC1079` to retrieve actual version tags like `Rev 4` or stage descriptors).
*   **Database Translation**: Built glossaries (`TRANSLATIONS` and `TYPE_TRANSLATIONS`) to dynamically map Spanish fields to English during compilation:
    *   *Stages*: e.g., `SS Eléctrico - Precom` $\rightarrow$ `Electrical SS - Precom`
    *   *Milestones*: `Caminata` $\rightarrow$ `Walkdown`, `Entrega Const.` $\rightarrow$ `Construction Release (CRP)`
*   **Milestone Indexing**: Updated the preprocessor to capture vertical stacking indices for subsystems (`Index` column in P6) to enable vertical stacking.

### Phase 2: First Dashboard Build
*   Created `dashboard_template.html` containing an **S-Curve Analytics** chart and an initial timeline view.
*   Cleaned up obsolete spreadsheet tabs ("Roadmap Matrix" and "Subsystems List") to simplify the layout.
*   Generated the compiled `index.html` file using `compile_dashboard.py` (successfully grouping and injecting clean JSON data).

### Phase 3: Dynamic Filters & Tab Refactoring
*   **Dynamic Flag Filters**: Implemented dynamic filter rendering in the dashboard header.
    *   For **B2SG Spence**, the filter bar (Domes, Thickeners, etc.) is hidden since those flags are empty/null.
    *   For **D3MC Centinela**, all 6 checkboxes (Definitive Energization, Domes, Thickeners, Pool Filling, Water Run 1, Water Run 2) appear dynamically.
*   **Spence Database Split**: Found that B2SG Spence database records were being compressed under a single empty version string in `precom_data.json`. Refactored `process_pbi_data.py` to group by `Month` (which holds the database release dates: `20200327`, `20200424`, `20200925`) instead of `Version`. This correctly restored Spence's historical database snapshots in the version selector dropdown.

---

## 3. Data Findings & Analysis

### Revisions & Versions Mapping
1.  **D3MC Centinela - Skyline**: Revisions are labeled `Rev1`, `Rev2`, and `Rev3`. The versions in the PBIX/Excel are `Rev 2`, `Rev 3`, and `Rev 4`.
2.  **B2SG Spence - Skyline**: The project has three database versions labeled by dates in the `Month` column:
    *   `20200327`: Extracted from folder `Rev A7` (Update Mar20).
    *   `20200424`: Extracted from folder `Rev A6` (Update Apr20).
    *   `20200925`: Extracted from file `B2SG - Base datos 20200925 ... Rev 0.xlsx`.
    *   *Summary*: The "Rev.0" schedule version mentioned by the user corresponds to the `20200925` database snapshot. The "Rev.B" (or baseline revision) corresponds to the `20200424` or `20200327` snapshots.

### Subsystem Quantities Analysis
A python script was executed to count scheduled Turnover Packages (TOP) by week across revisions:
*   **Centinela Revisions** (from `Programa 18.07.22  Con Caminatas (ODPT Feb1) .xlsx`):
    *   `Rev1` (Total 53 subsystems): Grouped mostly between November 2024 and July 2025 (peak on week 2025-03-23 with 11 subsystems).
    *   `Rev2` (Total 2 subsystems): Planned for weeks 2025-03-16 and 2025-04-20.
    *   `Rev3` (Total 10 subsystems): Distributed between September 2024 and April 2025.
    *   `N/A` (Total 111 subsystems): Distributed from June 2024 through June 2025.
*   **Spence Versions** (from `precom_data.json`):
    *   `20200424` (Rev A6 / "Rev.B" equivalent - Total 223 subsystems): Planned from May 2020 through October 2020 (peaks in July/August/October 2020).
    *   `20200925` (Rev 0 - Total 223 subsystems): Planned between August 2020 and October 2020 (concentrated peak on week 2020-09-18 with 75 subsystems).

---

## 4. Current Work: Replicating Target Sheets

We are currently working on matching the dashboard sheets exactly with the Power BI visuals:

### Target Tab 1: "Filters by CRP & TOP"
*   This represents the main **Skyline View** schedule.
*   **Milestone Toggle**: A radio/dropdown selector to filter by milestone type (`CRP` or `TOP`).
*   **Stage Card Coloring**: Subsystem cards are color-coded by their pre-commissioning Stage (`Etapa`):
    *   `E1`: Red
    *   `E2`: Yellow
    *   `E3`: Purple
    *   `E4`: Green
    *   `N/A` or others: Slate Gray
*   **Slicer Filters**: Slicers for Etapas and Dynamic Flags.

### Target Tab 2: "CRP & TOP Curves"
*   This represents the main S-Curve analytics page.
*   **Chart.js Plotting**: Displays cumulative curves (`CRP Cum`, `TOP Cum`) and incremental weekly counts (`CRP Inc`, `TOP Inc`).
*   **Data Grid Matrix**: A detailed weekly/monthly summary table displayed directly underneath the chart, containing rows for incremental counts (`CRP Inc`, `TOP Inc`, `C1 Inc`, `C2 Inc`, `C3 Inc`, `C4 Inc`) and cumulative totals (`CRP Cum`, `TOP Cum`).
