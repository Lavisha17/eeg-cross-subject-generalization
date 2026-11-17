(() => {
  "use strict";

  const $ = id => document.getElementById(id);
  const paths = {
    models: "data/model_results.csv",
    participants: "data/participant_results.csv",
    summary: "data/participant_summary.csv"
  };

  function parseCSV(text) {
    const lines = text.trim().split(/\r?\n/);
    const headers = lines.shift().split(",").map(x => x.trim());
    return lines.filter(Boolean).map(line => {
      const values = line.split(",");
      return Object.fromEntries(headers.map((h, i) => [h, (values[i] || "").trim()]));
    });
  }

  async function load(path) {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`Cannot load ${path}: HTTP ${response.status}`);
    return parseCSV(await response.text());
  }

  const n = value => {
    if (value == null || value === "" || value === "N/A") return null;
    const result = Number(value);
    return Number.isFinite(result) ? result : null;
  };

  const percent = value => value == null ? "N/A" : (value * 100).toFixed(2) + "%";
  const decimal = value => value == null ? "N/A" : value.toFixed(3);

  function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[c]);
  }

  function showError(error) {
    const box = $("load-error");
    box.hidden = false;
    box.textContent = "Results could not be loaded: " + error.message +
      ". Please run this website using the local server instructions.";
    console.error(error);
  }

  function drawBars(element, rows, field, label) {
    const W = 650, left = 175, right = 55, top = 30, row = 62;
    const plot = W - left - right;
    const H = top + rows.length * row + 35;
    let svg = "";

    [0, .25, .5, .75, 1].forEach(t => {
      const x = left + plot * t;
      svg += `<line x1="${x}" y1="${top - 10}" x2="${x}" y2="${H - 25}" stroke="#9ba8a2" opacity=".35"/>`;
      svg += `<text x="${x}" y="${H - 7}" text-anchor="middle" fill="#617174" font-size="11">${t * 100}%</text>`;
    });

    rows.forEach((r, i) => {
      const value = n(r[field]);
      const y = top + i * row;
      const color = r.Model === "Full 56 features" ? "#147d78" :
        r.Model === "Targeted 8 features" ? "#c17a4b" : "#89939b";

      svg += `<text x="${left - 10}" y="${y + 23}" text-anchor="end" fill="#172a2c" font-size="12">${escapeHTML(r.Model)}</text>`;
      if (value == null) {
        svg += `<text x="${left + 8}" y="${y + 23}" fill="#617174" font-size="12">Not applicable</text>`;
      } else {
        const width = Math.max(0, Math.min(1, value)) * plot;
        svg += `<rect x="${left}" y="${y + 4}" width="${width}" height="29" rx="4" fill="${color}"/>`;
        svg += `<text x="${Math.min(left + width + 8, W - 48)}" y="${y + 23}" fill="#172a2c" font-size="12">${percent(value)}</text>`;
      }
    });

    element.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${label}" xmlns="http://www.w3.org/2000/svg">${svg}</svg>`;
  }

  function drawParticipants(element, rows) {
    const ids = [...new Set(rows.map(r => r.Participant))].sort((a, b) => Number(a) - Number(b));
    const W = 720, left = 42, right = 15, top = 20, plotH = 230;
    const plotW = W - left - right;
    const group = plotW / ids.length;
    let svg = "";

    [0, .25, .5, .75, 1].forEach(t => {
      const y = top + plotH * (1 - t);
      svg += `<line x1="${left}" y1="${y}" x2="${W - right}" y2="${y}" stroke="#9ba8a2" opacity=".35"/>`;
      svg += `<text x="${left - 7}" y="${y + 4}" text-anchor="end" fill="#617174" font-size="10">${t * 100}%</text>`;
    });

    ids.forEach((id, i) => {
      const x = left + i * group;
      const entries = [
        { model: "Full 56 features", color: "#147d78", offset: 0 },
        { model: "Targeted 8 features", color: "#c17a4b", offset: 14 }
      ];
      entries.forEach(entry => {
        const found = rows.find(r => r.Participant === id && r.Model === entry.model);
        const value = n(found?.["Balanced Accuracy"]);
        if (value == null) return;
        const h = value * plotH;
        svg += `<rect x="${x + group / 2 - 15 + entry.offset}" y="${top + plotH - h}" width="12" height="${h}" rx="2" fill="${entry.color}"><title>Participant ${id}: ${percent(value)}</title></rect>`;
      });
      svg += `<text x="${x + group / 2}" y="${top + plotH + 18}" text-anchor="middle" fill="#617174" font-size="10">${id}</text>`;
    });

    svg += `<rect x="235" y="278" width="11" height="11" fill="#147d78"/><text x="251" y="288" fill="#172a2c" font-size="11">Full 56 features</text>`;
    svg += `<rect x="390" y="278" width="11" height="11" fill="#c17a4b"/><text x="406" y="288" fill="#172a2c" font-size="11">Targeted 8 features</text>`;
    element.innerHTML = `<svg viewBox="0 0 ${W} 300" role="img" aria-label="Participant-level balanced accuracy" xmlns="http://www.w3.org/2000/svg">${svg}</svg>`;
  }

  function modelTable(rows) {
    $("tbl-models").innerHTML = `
      <thead><tr><th>Model</th><th>Features</th><th>Best C</th><th>CV balanced accuracy</th><th>Test balanced accuracy</th><th>Macro F1</th><th>ROC-AUC</th></tr></thead>
      <tbody>${rows.map(r => `<tr>
        <td>${escapeHTML(r.Model)}</td><td>${escapeHTML(r.Features)}</td><td>${escapeHTML(r["Best C"])}</td>
        <td>${percent(n(r["CV Balanced Accuracy"]))}</td>
        <td>${percent(n(r["Test Balanced Accuracy"]))}</td>
        <td>${decimal(n(r["Test Macro F1"]))}</td>
        <td>${decimal(n(r["Test ROC-AUC"]))}</td>
      </tr>`).join("")}</tbody>`;
  }

  function summaryTable(rows) {
    $("tbl-summary").innerHTML = `
      <thead><tr><th>Model / comparison</th><th>Participants</th><th>Mean balanced accuracy</th><th>Standard deviation</th><th>95% CI</th></tr></thead>
      <tbody>${rows.map(r => `<tr>
        <td>${escapeHTML(r.Model)}</td><td>${escapeHTML(r.Participants)}</td>
        <td>${percent(n(r["Mean Balanced Accuracy"]))}</td>
        <td>${decimal(n(r["Standard Deviation"]))}</td>
        <td>${percent(n(r["CI Lower"]))} – ${percent(n(r["CI Upper"]))}</td>
      </tr>`).join("")}</tbody>`;
  }

  async function init() {
    try {
      const [models, participants, summary] = await Promise.all([
        load(paths.models), load(paths.participants), load(paths.summary)
      ]);

      modelTable(models);
      summaryTable(summary);
      drawBars($("chart-bacc"), models, "Test Balanced Accuracy", "Test balanced accuracy");
      drawBars($("chart-auc"), models, "Test ROC-AUC", "Test ROC-AUC");
      drawParticipants($("chart-part"), participants);

      const full = models.find(r => r.Model === "Full 56 features");
      const targeted = models.find(r => r.Model === "Targeted 8 features");
      $("read-1").textContent =
        `The full 56-feature model achieved ${percent(n(full["Test Balanced Accuracy"]))} test balanced accuracy, compared with ${percent(n(targeted["Test Balanced Accuracy"]))} for the targeted eight-feature model. The majority baseline achieved 50%. These results apply to the ten held-out participants in this experiment.`;

      const a = summary.find(r => r.Model === "Full 56 features");
      const b = summary.find(r => r.Model === "Targeted 8 features");
      const d = summary.find(r => r.Model === "Paired difference (Full - Targeted)");

      $("ci-note").textContent =
        `Participant-level bootstrap 95% confidence intervals (10,000 resamples): full model ${percent(n(a["CI Lower"]))}–${percent(n(a["CI Upper"]))}; targeted model ${percent(n(b["CI Lower"]))}–${percent(n(b["CI Upper"]))}. Paired mean difference: ${percent(n(d["Mean Balanced Accuracy"]))} (95% CI ${percent(n(d["CI Lower"]))}–${percent(n(d["CI Upper"]))}). These estimates are based on ten held-out participants and should be interpreted cautiously.`;

      $("load-error").hidden = true;
    } catch (error) {
      showError(error);
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
