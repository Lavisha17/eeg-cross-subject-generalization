# EEG Workload Classification Research Website

## Run locally

From the repository root, run:

```powershell
python -m http.server 8000 --directory website
```

Open http://localhost:8000 in your browser.

Press Ctrl+C in the terminal to stop the server.

## Contents

- `index.html`: research website
- `css/style.css`: layout and styling
- `js/main.js`: CSV loading, tables and charts
- `data/`: experiment result CSV files
- `assets/figures/`: generated research figures

The website uses the actual experiment output files. Charts are rendered locally using SVG; no chart library is required.
