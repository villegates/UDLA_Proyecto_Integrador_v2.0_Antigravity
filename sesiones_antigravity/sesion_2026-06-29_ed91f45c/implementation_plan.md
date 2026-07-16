# Implementation Plan - Skyline View, English Translation, and Dynamic Filters

This plan details the steps to replace the Roadmap Matrix and Subsystems List tabs with a dedicated, interactive "Skyline View", translate all database items and UI elements from Spanish to English, and dynamically show or hide filters depending on whether they contain data for the selected project (e.g. hiding Domes and Thickeners for Spence).

## User Review Required

> [!IMPORTANT]
> The **Roadmap Matrix** and **Subsystems List** tabs will be removed as requested. They will be replaced by an interactive **Skyline View** tab.
>
> We will add a dynamic filter checking mechanism: filters (such as Domes or Thickeners) that have no active flags in the selected project's dataset will be hidden from the UI automatically.

## Open Questions

*None at this time. The requirements are clear.*

## Proposed Changes

### Data Processing & Localization

---

#### [MODIFY] [process_pbi_data.py](file:///c:/Users/Pablo%20Villegas/.gemini/antigravity-ide/scratch/process_pbi_data.py)
* Add a translation dictionary (`TRANSLATIONS` and `TYPE_TRANSLATIONS`) to translate all Spanish terms in subsystem descriptions, stages (`etapa`), and milestone types to English during parsing.
* Extract the `Week` and `Index` for each milestone type per subsystem (from the raw PBIX data) and save them in a new `milestones` dictionary in [precom_data.json](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Skylines/PreCom/precom_data.json).

---

### Dashboard Layout & Presentation

---

#### [MODIFY] [dashboard_template.html](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/Skylines/PreCom/dashboard_template.html)
* **Tabs removal**: Delete the Roadmap Matrix and Subsystems List tabs.
* **New Skyline Tab**:
  * Add a tab for "Skyline View".
  * Add a select dropdown inside the tab to choose the milestone type (`Walkdown 1`, `Walkdown 2`, `CRP`, `Walkdown 3`, `Walkdown 4`, `TOP`).
  * Render a grid where each column represents a week and contains a stacked list of subsystem blocks scheduled to complete that week.
  * Sort/position blocks using the database-provided `index` values.
  * Enable clicking blocks to slide open the detail drawer.
* **Dynamic Filter Generation**:
  * Implement logic to scan the active project dataset and render only the milestone filter checkboxes that actually contain data (e.g. hide all for Spence).
* **UI Localization**:
  * Translate all hardcoded Spanish strings, legend labels, and drawer contents to English.

## Verification Plan

### Automated Tests
* Run `process_pbi_data.py` to compile the translated English dataset with milestone indices.
* Run `compile_dashboard.py` to regenerate the static dashboard page.

### Manual Verification
* Load the dashboard in the browser:
  * Select `D3MC Centinela - Skyline` and verify that the Domes/Thickeners filters are shown, and the Skyline displays Centinela data correctly.
  * Select `B2SG Spence - Skyline` and verify that all milestone filters are hidden (since Spence has no active flags) and the Skyline displays Spence data correctly.
  * Confirm that all stage names and subsystem details are translated to English.
