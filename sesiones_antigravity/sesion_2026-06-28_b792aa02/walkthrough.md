# Walkthrough — PreCom & TOP Interactive HTML Dashboard

We have successfully migrated the Power BI report `D3MC Precom 20220705 Rev 04.pbix` into a premium, fully interactive, standalone HTML dashboard (`index.html`) located in your project directory. 

## Files Created

1. **[precom_data.json](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Skylines/PreCom/precom_data.json)**: Minified database containing the extracted schedules for both **D3MC Centinela** (Revisions 2, 3, 4, Target) and **B2SG Spence** projects, along with precalculated S-curves and subsystem dates.
2. **[dashboard_template.html](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Skylines/PreCom/dashboard_template.html)**: Interactive template housing the HTML structure, responsive Tailwind styling, Chart.js visuals, and client-side filtering/matrix roadmap logic.
3. **[compile_dashboard.py](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Skylines/PreCom/compile_dashboard.py)**: Python compilation script to inject the data JSON and produce the final file.
4. **[index.html](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Skylines/PreCom/index.html)**: The compiled standalone dashboard. 

---

## How to View and Run the Dashboard

The dashboard is completely **standalone and self-contained**, meaning it requires **no web server or database connection** to run. 

1. Navigate to the folder: `c:\Users\Pablo Villegas\OneDrive\Documents\Claude\Skylines\PreCom`
2. Double-click the **[index.html](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Skylines/PreCom/index.html)** file to open it in your web browser (Chrome, Edge, Firefox, or Safari).

---

## Key Dashboard Features

### 1. Dynamic Project & Revision Filters
*   **Project Dropdown**: Select between `D3MC Centinela - Skyline` and `B2SG Spence - Skyline`.
*   **Version Dropdown**: Choose between the available plan snapshots (e.g., `Rev 4`, `Rev 4 - Mes`, `Rev 3`, `Rev 3 - Mes`, `Rev 2`, `Rev 2 - Mes`, or `Target_01`).
*   **Stage Dropdown**: Filter dynamically by PreCom stage.

### 2. S-Curve Analytics Tab
*   An interactive Chart.js combination line and bar chart.
*   **Cumulative S-Curve Lines** for TOP, CRP, and Walkdowns (C1-C4).
*   **Weekly Periodic actual bars** for milestones.
*   Legends are interactive: click on any milestone label in the legend to toggle its visibility on the chart.

### 3. Subsystems Milestone Roadmap Matrix Tab
*   Plots milestone events (**C1, C2, CRP, C3, C4, TOP**) along a weekly schedule timeline grid.
*   Hover over any circle or diamond marker on the grid to see the exact event title, stage, and milestone completion date.
*   Fully responsive scrollable pane allowing rapid visual alignment across all subsystems.

### 4. Master Subsystems List Tab
*   A flat tabular database of all subsystems and their associated dates.
*   **Search bar**: Search instantly by subsystem code or description.
*   **Custom Flags Slicers**: Filter the list by specific milestone attributes (e.g. *Energización Definitiva*, *Domos*, *Espesadores*, *Piscinas*, *Water Run 1*, *Water Run 2*).
*   **Export CSV**: Download the current filtered subsystems list as a clean, formatted Excel-compatible CSV file.

### 5. Details Drawer & Theme Switcher
*   Click on any row in the Subsystems List or matrix grid to slide out a side panel displaying the subsystem's details, stages, flags, and complete dates.
*   Toggle the **Moon/Sun button** in the top right to switch between Dark Mode and Light Mode themes.
