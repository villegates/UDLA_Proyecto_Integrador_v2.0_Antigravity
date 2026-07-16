# Implementation Plan - HTML Deliverables Dashboard & S-Curve Control

The goal is to replace the Power BI (`.pbix`) dashboard with a modern, premium, self-contained HTML/JS dashboard (`dashboard.html`). 
A Python script (`update_dashboard.py`) will automatically scan the workspace, parse the Excel "Input" sheets (e.g., `Planilla Control_150626 rev1 Input.xlsx`), compute cumulative progress, weekly metrics, and contractor statistics, and write this data directly into the dashboard file as a JavaScript object.

This eliminates CORS browser issues, allowing the dashboard to run instantly in any web browser by simply double-clicking `dashboard.html`.

---

## User Review Required

### Key Design & Functional Decisions
1. **Dropdown-Based Historical Comparison**: To address the requirement to "control the forecast prior to the control week," the dashboard will process **all** historical Excel files in the folder. A dropdown menu on the dashboard will allow you to select **any** previous control week (e.g., June 8, June 2, May 10, etc.) to immediately compare the current forecast curve against that week's forecast curve.
2. **Standalone HTML file**: The dashboard will compile all CSS (Tailwind via CDN for rapid utility styling or beautiful custom vanilla CSS) and libraries (Chart.js for visualizations) in a single portable file, making it easy to share or archive.

---

## Open Questions

> [!IMPORTANT]
> Please verify the following assumptions:
> 1. **Piteau Log File**: We observed that `Registro Control Ing. EIA_050526_Piteau - Input.xlsx` is an older log from May 5, 2026. In later weeks (June 2, 8, 15), Piteau deliverables are already integrated into the master `Planilla Control_[Date] Input.xlsx` worksheet. We propose to ignore the standalone Piteau files and focus entirely on the master `Planilla Control_[Date] Input.xlsx` files. Please let us know if we should process the standalone Piteau files separately.
> 2. **Date Format**: We assumed the date in the filename is `DDMMYY` format (e.g., `Planilla Control_150626` represents **June 15, 2026**). Please confirm this is correct.

---

## Proposed Changes

### Data Processor

#### [NEW] [update_dashboard.py](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Docs%20Control/update_dashboard.py)
A Python script that will:
- Scan the directory for files matching `Planilla Control_* Input.xlsx` and parse the date.
- Load the master sheet `Planilla Control` from each file.
- Clean and normalize dates (`Fecha Entrega PLAN REV B/0`, `FORECAST REV B/0`, `Fecha REV B/0 REAL`).
- Group deliverables by week (Mondays) and compute weekly cumulative and periodic counts.
- Generate contractor summaries (deliverables count, completed, pending, status distribution).
- Create a deliverables listing with search/filter tags.
- Read an HTML template, inject the parsed JSON database, and save it as `dashboard.html`.

### Dashboard UI

#### [NEW] [dashboard_template.html](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Docs%20Control/dashboard_template.html)
The template file containing:
- A modern UI layout (sidebar, dashboard cards, tab panels).
- Chart.js integration for the S-curves and Weekly Combo Charts.
- Tailwind CSS and custom styling for a premium dark/glassmorphic look.
- Javascript logic to handle tab switching, search/filtering of the deliverables table, and dynamic chart updates when selecting a historical comparison week from the dropdown.

#### [NEW] [dashboard.html](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Docs%20Control/dashboard.html)
The final generated file that the user opens to view the dashboard.

---

## Verification Plan

### Automated Tests
- We will run `python update_dashboard.py` and verify it runs without errors.
- We will print the output JSON data to verify that:
  - Deliverables count is correct (e.g., 476 for June 15, 2026).
  - All weeks are sorted.
  - S-curve coordinates sum up to the total deliverables count.

### Manual Verification
- Open `dashboard.html` in a web browser.
- Verify the layout renders correctly, tabs switch, and the dropdown updates the "Previous Forecast" line on the charts.
- Use the search bar to locate specific deliverables and check their status.
