# Verification Checklist
- [ ] Open the dashboard URL. (BLOCKED: Browser tool blocks file:// URLs)
- [ ] Verify title 'EIA COSTA FUEGO'.
- [ ] Verify S-curve charts (scurveChartB, scurveChart0) are rendered.
- [ ] Click 'Weekly Issuance' tab and verify weekly combo charts.
- [ ] Click 'Contractor Breakdown' and verify contractor performance cards & doughnut charts.
- [ ] Click 'Deliverables List' and verify table displays rows.
- [ ] Test search bar (type 'Ausenco' / filter check).
- [ ] Test 'Compare Forecast With' dropdown.

## Blocker Notes
The browser tool has a security restriction that blocks access to `file://` URLs.
To proceed with verification, the planner needs to:
1. Spin up a temporary local HTTP server in the directory `c:\Users\Pablo Villegas\OneDrive\Documents\Claude\Docs Control\`.
   For example, using:
   `python -m http.server 8000 --directory "c:\Users\Pablo Villegas\OneDrive\Documents\Claude\Docs Control"`
2. Re-run this browser subagent with the URL `http://localhost:8000/dashboard.html`.
