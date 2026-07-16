# Power BI to Interactive HTML Dashboard Migration

Reconstruct the Power BI report `D3MC Precom 20220705 Rev 04.pbix` (Centinela & Spence Precommissioning and TOP Schedule) into a premium, responsive, and standalone HTML/JS dashboard (`index.html`) using the extracted data model.

## User Review Required

> [!IMPORTANT]
> **Data Scope and Selection**:
> The dashboard will incorporate both the **D3MC Centinela** (Revisions 2, 3, 4, and Target) and **B2SG Spence** project datasets extracted directly from the Power BI model. The default active view will load **D3MC Centinela - Rev 4** as it represents the most complete schedule including all 4 walkdowns (Caminatas) and TOP dates.
>
> **Interactive Roadmap Grid**:
> Replicating the Excel/Power BI pivot table matrix, we will implement a visual **Subsystems Progress Matrix** that plots walkdowns (C1-C4), construction releases (CRP), and turnover packages (TOP) along an interactive weekly timeline grid with premium hover states.

## Open Questions

> [!NOTE]
> There are no major open questions, as the data schema has been successfully extracted using `pbixray` and matches the Excel files in the workspace.

## Proposed Changes

---

### Data Compilation & Processing

Create a Python build script that bundles the precomputed JSON dataset directly into the HTML dashboard.

#### [NEW] [compile_dashboard.py](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Skylines/PreCom/compile_dashboard.py)
A Python compilation script that loads the HTML layout, injects `precom_data.json` into the code template, and writes the compiled standalone `index.html`.

---

### Dashboard Layout & Presentation

#### [NEW] [dashboard_template.html](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Skylines/PreCom/dashboard_template.html)
The dashboard template containing Tailwind CSS, FontAwesome icons, Chart.js visual configurations, and UI tabs:
1. **S-Curve Analytics**: Cumulative S-curves and weekly periodic actual counts for C1-C4, CRP, and TOP.
2. **Subsystems Progress Matrix**: An interactive roadmap grid showing milestone completions per week for each subsystem.
3. **Master Subsystems List**: Full searchable list with details and CSV export functionality.

#### [NEW] [index.html](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Skylines/PreCom/index.html)
The final generated, single-file static HTML dashboard ready for offline use.

## Verification Plan

### Automated Verification
- Run the python compilation script `compile_dashboard.py` to ensure it successfully builds the HTML file.
- Verify file sizes and that no errors occur during compiling.

### Manual Verification
- Open `index.html` in a web browser.
- Verify theme toggles (Light/Dark mode) adapt colors correctly.
- Test filters (Project, Version, Stage, and milestone flags like Domos/Espesadores).
- Ensure the S-Curve lines and bars render correctly on Chart.js.
- Verify the search and CSV export functionality in the subsystems table.
