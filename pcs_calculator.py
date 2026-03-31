"""
Patient Complexity Score (PCS) Interactive Calculator
MSE 433 Module 4 — EP Lab AFib Ablation

Run:
    python3 pcs_calculator.py

Then open:
    http://localhost:8050
"""

import http.server
import threading
import webbrowser

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PCS Calculator — MSE 433</title>
<style>
:root {
  --bg: #0b1020;
  --panel: rgba(22, 28, 45, 0.88);
  --panel-2: rgba(18, 23, 38, 0.92);
  --border: rgba(255, 255, 255, 0.08);
  --text: #eef2ff;
  --muted: #94a3b8;
  --accent: #67e8f9;
  --green: #22c55e;
  --yellow: #facc15;
  --red: #f87171;
  --shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
  --radius-lg: 20px;
  --radius-md: 14px;
  --radius-sm: 10px;
}

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
}

body {
  min-height: 100vh;
  font-family: Inter, "Segoe UI", system-ui, sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at top left, rgba(103, 232, 249, 0.12), transparent 28%),
    radial-gradient(circle at top right, rgba(248, 113, 113, 0.10), transparent 22%),
    linear-gradient(145deg, #070b16 0%, #0b1020 45%, #0f172a 100%);
  padding: 24px;
}

.container {
  max-width: 1480px;
  margin: 0 auto;
}

.hero {
  margin-bottom: 20px;
  padding: 24px 28px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(16px);
}

.tag {
  display: inline-block;
  font-size: 11px;
  color: var(--accent);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

h1 {
  margin: 0 0 8px 0;
  font-size: 34px;
  line-height: 1.1;
  font-weight: 800;
}

.subtitle {
  margin: 0;
  color: var(--muted);
  font-size: 15px;
  max-width: 900px;
  line-height: 1.6;
}

.app-shell {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(360px, 0.95fr);
  gap: 22px;
  align-items: start;
}

.left-panel,
.right-panel {
  min-width: 0;
}

.right-panel {
  position: sticky;
  top: 20px;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  backdrop-filter: blur(16px);
}

.section-card {
  padding: 20px;
}

.section-title {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--accent);
  margin-bottom: 14px;
  font-weight: 700;
}

.factors-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.factor-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px;
  min-height: 100%;
}

.factor-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 14px;
}

.factor-topline {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.factor-name {
  font-size: 15px;
  font-weight: 700;
  line-height: 1.35;
}

.factor-weight {
  white-space: nowrap;
  font-size: 11px;
  color: var(--accent);
  background: rgba(103, 232, 249, 0.10);
  border: 1px solid rgba(103, 232, 249, 0.18);
  padding: 5px 9px;
  border-radius: 999px;
}

.factor-affects {
  font-size: 12px;
  color: var(--muted);
  line-height: 1.5;
}

.factor-affects span {
  color: #dbeafe;
}

.btn-group {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.btn {
  width: 100%;
  text-align: left;
  padding: 11px 12px;
  font-size: 12px;
  cursor: pointer;
  border-radius: 12px;
  background: rgba(255,255,255,0.02);
  color: #cbd5e1;
  border: 1px solid rgba(255,255,255,0.06);
  font-family: inherit;
  transition: 0.18s ease;
  line-height: 1.45;
}

.btn:hover {
  transform: translateY(-1px);
  border-color: rgba(103, 232, 249, 0.35);
  color: #ffffff;
  background: rgba(255,255,255,0.04);
}

.btn.selected {
  font-weight: 700;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
}

.btn.s0.selected {
  background: rgba(34, 197, 94, 0.12);
  color: #bbf7d0;
  border-color: rgba(34, 197, 94, 0.45);
}

.btn.s1.selected {
  background: rgba(250, 204, 21, 0.12);
  color: #fde68a;
  border-color: rgba(250, 204, 21, 0.45);
}

.btn.s2.selected {
  background: rgba(248, 113, 113, 0.12);
  color: #fecaca;
  border-color: rgba(248, 113, 113, 0.45);
}

.btn.s3.selected {
  background: rgba(239, 68, 68, 0.16);
  color: #fee2e2;
  border-color: rgba(239, 68, 68, 0.5);
}

.effect-text {
  margin-top: 12px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.05);
  font-size: 12px;
  color: var(--muted);
  line-height: 1.55;
}

.result-card {
  padding: 24px;
  margin-bottom: 16px;
  background: linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.02));
  border: 1px solid var(--border);
  border-radius: 22px;
  box-shadow: var(--shadow);
}

.result-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.score-label {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1.6px;
  margin-bottom: 8px;
}

.score-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.score-value {
  font-size: 58px;
  font-weight: 800;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  line-height: 1;
}

.score-max {
  font-size: 22px;
  color: var(--muted);
}

.category {
  font-size: 24px;
  font-weight: 800;
  text-align: right;
}

.recommended {
  font-size: 14px;
  color: var(--muted);
  margin-top: 8px;
  text-align: right;
  line-height: 1.5;
}

.recommended strong {
  color: var(--accent);
}

.score-bar {
  height: 12px;
  background: rgba(255,255,255,0.05);
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 16px;
}

.score-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.35s ease;
}

.rationale-box {
  background: var(--panel-2);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 16px;
  padding: 16px;
}

.rationale-label {
  font-size: 11px;
  font-weight: 800;
  color: var(--accent);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1.4px;
}

.rationale-text {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.7;
}

.steps-affected {
  margin-top: 14px;
}

.steps-affected .label {
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.step-tag {
  display: inline-block;
  font-size: 11px;
  padding: 6px 10px;
  border-radius: 999px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  margin: 4px 6px 0 0;
  border: 1px solid rgba(255,255,255,0.08);
}

.toggle-btn {
  width: 100%;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  color: #dbeafe;
  padding: 13px 16px;
  border-radius: 14px;
  cursor: pointer;
  font-size: 13px;
  font-family: inherit;
  margin-bottom: 16px;
  transition: 0.18s ease;
}

.toggle-btn:hover {
  border-color: rgba(103,232,249,0.3);
  color: white;
  background: rgba(255,255,255,0.05);
}

.breakdown {
  padding: 20px;
  margin-bottom: 16px;
  display: none;
  background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.02));
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow);
}

.breakdown.show {
  display: block;
}

.formula {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 13px;
  color: var(--accent);
  margin-bottom: 16px;
  line-height: 1.8;
  background: rgba(103, 232, 249, 0.06);
  border: 1px solid rgba(103, 232, 249, 0.14);
  padding: 10px 12px;
  border-radius: 12px;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

th {
  text-align: left;
  padding: 10px;
  color: var(--muted);
  font-weight: 700;
  font-size: 11px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  text-transform: uppercase;
  letter-spacing: 1px;
}

th.center,
td.center {
  text-align: center;
}

td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  color: #e2e8f0;
}

td.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.total-row td {
  border-top: 2px solid rgba(255,255,255,0.10);
  border-bottom: none;
  font-weight: 800;
  font-size: 16px;
}

.weight-rationale {
  margin-top: 16px;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.7;
}

.weight-rationale strong {
  color: white;
}

.schedule-ref {
  padding: 20px;
  background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.02));
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow);
}

.schedule-title {
  font-size: 14px;
  font-weight: 800;
  margin-bottom: 14px;
}

.schedule-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.schedule-slot {
  background: rgba(255,255,255,0.03);
  border-radius: 14px;
  padding: 14px;
  text-align: left;
  transition: 0.25s ease;
  border: 1px solid rgba(255,255,255,0.05);
}

.schedule-slot .slot-label {
  font-size: 12px;
  font-weight: 800;
}

.schedule-slot .slot-pcs {
  font-size: 12px;
  font-weight: 800;
  margin: 7px 0 4px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.schedule-slot .slot-time {
  font-size: 11px;
  color: var(--muted);
}

.schedule-slot .slot-reason {
  font-size: 11px;
  color: var(--muted);
  margin-top: 6px;
  line-height: 1.45;
}

.footer-note {
  margin-top: 16px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.6;
}

@media (max-width: 1180px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .right-panel {
    position: static;
    top: auto;
  }
}

@media (max-width: 820px) {
  .factors-grid {
    grid-template-columns: 1fr;
  }

  .schedule-grid {
    grid-template-columns: 1fr;
  }

  .result-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .category,
  .recommended {
    text-align: left;
  }
}

@media (max-width: 600px) {
  body {
    padding: 14px;
  }

  .hero,
  .section-card,
  .result-card,
  .breakdown,
  .schedule-ref {
    padding: 16px;
  }

  h1 {
    font-size: 28px;
  }

  .score-value {
    font-size: 44px;
  }
}
</style>
</head>
<body>
<div class="container" id="app"></div>

<script>
const factors = [
  {
    id: "bmi",
    name: "BMI Category",
    weight: 15,
    levels: [
      { label: "Normal (18.5–25)", effect: "Baseline vascular access difficulty and standard anesthesia profile." },
      { label: "Overweight (25–30)", effect: "+1 to 2 min access due to deeper vein and slightly longer intubation." },
      { label: "Obese (30–40)", effect: "+3 to 5 min access, ultrasound guidance more likely, harder intubation." },
      { label: "Morbidly Obese (>40)", effect: "+5 to 10 min total, possible table constraints, harder hemostasis." }
    ],
    affects: ["Pt Prep/Intubation", "Vascular Access", "Post-Care"]
  },
  {
    id: "cardiac",
    name: "Cardiac History",
    weight: 20,
    levels: [
      { label: "First-time AFib ablation", effect: "Standard anatomy with no prior scar-related complexity." },
      { label: "Prior cardiac catheterization", effect: "May have scar tissue at access site or known vascular variation." },
      { label: "Prior ablation (redo)", effect: "+10 to 20 min. Scar tissue complicates mapping and TSP." },
      { label: "Prior cardiac surgery", effect: "Altered anatomy may make TSP and mapping significantly harder." }
    ],
    affects: ["TSP", "Pre-Map", "Ablation"]
  },
  {
    id: "anatomy",
    name: "Septal Anatomy (from pre-op imaging)",
    weight: 25,
    levels: [
      { label: "Normal / thin septum", effect: "TSP expected in roughly 2 to 5 min." },
      { label: "Thickened septum", effect: "TSP may take 5 to 10 min and require added care." },
      { label: "Lipomatous / aneurysmal septum", effect: "TSP may take 10 to 20 min and require specialized technique." },
      { label: "Prior septal closure / PFO device", effect: "TSP may exceed 20 min or require an alternative approach." }
    ],
    affects: ["TSP"]
  },
  {
    id: "ablation_scope",
    name: "Planned Ablation Scope",
    weight: 25,
    levels: [
      { label: "Standard PVI only (4 veins)", effect: "Around 17 to 20 ablation sites and about 25 min duration." },
      { label: "PVI + 1 extra target", effect: "Roughly 22 to 25 sites and about 35 min duration." },
      { label: "PVI + BOX or PST BOX", effect: "About 25 to 28 sites and near 45 min duration." },
      { label: "PVI + multiple extras", effect: "28 to 30+ sites and 60+ min ablation duration." }
    ],
    affects: ["Ablation", "Verification"]
  },
  {
    id: "comorbidity",
    name: "Comorbidity / ASA Score",
    weight: 10,
    levels: [
      { label: "ASA I–II", effect: "Standard anesthesia and faster recovery expected." },
      { label: "ASA III", effect: "+2 to 3 min prep and longer post-care monitoring." },
      { label: "ASA IV", effect: "+5+ min prep, slower extubation, extended monitoring." }
    ],
    affects: ["Pt Prep/Intubation", "Post-Care"]
  },
  {
    id: "anticoag",
    name: "Anticoagulation Status",
    weight: 5,
    levels: [
      { label: "Standard protocol", effect: "Normal hemostasis expected." },
      { label: "Therapeutic anticoagulation", effect: "+3 to 5 min post-care for hemostasis." },
      { label: "Dual antiplatelet / complex regimen", effect: "+5 to 10 min post-care and possible closure device." }
    ],
    affects: ["Catheter Removal", "Post-Care"]
  }
];

const scheduleSlots = [
  { slot: "Case 1", pcs: "Medium", time: "~8:00 AM", reason: "Warm-up case to settle the team into flow.", color: "#facc15" },
  { slot: "Case 2", pcs: "High", time: "~10:00 AM", reason: "Best slot for peak cognition after warm-up.", color: "#f87171" },
  { slot: "Case 3", pcs: "Medium", time: "~12:00 PM", reason: "Still strong attention with decent buffer.", color: "#facc15" },
  { slot: "Case 4", pcs: "Low", time: "~2:30 PM", reason: "Routine case that is more fatigue resilient.", color: "#22c55e" }
];

const rationales = {
  High: "This case likely needs the strongest decision quality and the most focused attention. The second case is the best fit because the team is already warmed up, but fatigue is still limited.",
  Medium: "A medium-complexity case fits best in the first or third slot. These positions balance warm-up effects with still-solid cognitive capacity.",
  Low: "This case is routine enough to tolerate later-day fatigue better. Placing it last helps preserve the strongest slots for harder cases."
};

let selections = {
  bmi: 0,
  cardiac: 0,
  anatomy: 0,
  ablation_scope: 0,
  comorbidity: 0,
  anticoag: 0
};

let showBreakdown = false;

function computeScore() {
  let total = 0;
  factors.forEach(f => {
    const maxLevel = f.levels.length - 1;
    total += (selections[f.id] / maxLevel) * f.weight;
  });
  return Math.round(total);
}

function getCategory(score) {
  if (score > 60) return "High";
  if (score > 30) return "Medium";
  return "Low";
}

function getCategoryColor(score) {
  if (score > 60) return "#f87171";
  if (score > 30) return "#facc15";
  return "#22c55e";
}

function getSlot(category) {
  if (category === "High") return "2nd case of the day";
  if (category === "Medium") return "1st or 3rd case";
  return "4th case of the day";
}

function render() {
  const score = computeScore();
  const category = getCategory(score);
  const color = getCategoryColor(score);
  const slot = getSlot(category);

  const affectedSteps = [];
  factors.forEach(f => {
    if (selections[f.id] > 0) {
      f.affects.forEach(step => {
        if (!affectedSteps.includes(step)) affectedSteps.push(step);
      });
    }
  });

  let html = "";

  html += '<div class="hero panel">';
  html += '<div class="tag">Capturing Unobserved Factor 1</div>';
  html += '<h1>Patient Complexity Score Calculator</h1>';
  html += '<p class="subtitle">This dashboard estimates procedural complexity from six pre-operative factors that are often hidden in the raw EP lab timing data. Select the patient profile on the left and the score updates instantly on the right.</p>';
  html += '</div>';

  html += '<div class="app-shell">';

  html += '<div class="left-panel">';
  html += '<div class="panel section-card">';
  html += '<div class="section-title">Patient Inputs</div>';
  html += '<div class="factors-grid">';

  factors.forEach(f => {
    html += '<div class="factor-card">';
    html += '<div class="factor-header">';
    html += '<div class="factor-topline">';
    html += `<div class="factor-name">${f.name}</div>`;
    html += `<div class="factor-weight">${f.weight}% weight</div>`;
    html += '</div>';
    html += `<div class="factor-affects">Affects: <span>${f.affects.join(", ")}</span></div>`;
    html += '</div>';

    html += '<div class="btn-group">';
    f.levels.forEach((level, i) => {
      const selectedClass = selections[f.id] === i ? `selected s${i}` : `s${i}`;
      html += `<button class="btn ${selectedClass}" onclick="selectLevel('${f.id}', ${i})">${level.label}</button>`;
    });
    html += '</div>';

    html += `<div class="effect-text"><strong>Selected effect:</strong> ${f.levels[selections[f.id]].effect}</div>`;
    html += '</div>';
  });

  html += '</div>';
  html += '</div>';
  html += '</div>';

  html += '<div class="right-panel">';

  html += `<div class="result-card">`;
  html += '<div class="result-top">';
  html += '<div>';
  html += '<div class="score-label">Patient Complexity Score</div>';
  html += `<div class="score-row"><div class="score-value" style="color:${color}">${score}</div><div class="score-max">/100</div></div>`;
  html += '</div>';
  html += '<div>';
  html += `<div class="category" style="color:${color}">${category} Complexity</div>`;
  html += `<div class="recommended">Recommended scheduling slot: <strong>${slot}</strong></div>`;
  html += '</div>';
  html += '</div>';

  html += '<div class="score-bar">';
  html += `<div class="score-fill" style="width:${Math.min(score, 100)}%; background: linear-gradient(90deg, #22c55e 0%, #facc15 55%, #f87171 100%);"></div>`;
  html += '</div>';

  html += '<div class="rationale-box">';
  html += '<div class="rationale-label">Scheduling Rationale</div>';
  html += `<div class="rationale-text">${rationales[category]}</div>`;

  if (affectedSteps.length > 0) {
    html += '<div class="steps-affected">';
    html += '<div class="label">Procedure steps affected</div>';
    affectedSteps.forEach(step => {
      html += `<span class="step-tag" style="background:${color}18; color:${color}; border-color:${color}33;">${step}</span>`;
    });
    html += '</div>';
  }

  html += '</div>';
  html += '</div>';

  html += `<button class="toggle-btn" onclick="toggleBreakdown()">${showBreakdown ? "Hide" : "Show"} Score Breakdown & Formula</button>`;

  html += `<div class="breakdown ${showBreakdown ? "show" : ""}">`;
  html += '<div class="section-title">Scoring Breakdown</div>';
  html += '<div class="formula">PCS = Σ (selected level / max level) × factor weight</div>';
  html += '<div class="table-wrap">';
  html += '<table>';
  html += '<thead><tr><th>Factor</th><th class="center">Selected</th><th class="center">Score / Max</th><th class="center">Weight</th><th class="center">Contribution</th></tr></thead>';
  html += '<tbody>';

  factors.forEach(f => {
    const maxLevel = f.levels.length - 1;
    const contribution = (selections[f.id] / maxLevel) * f.weight;
    html += '<tr>';
    html += `<td>${f.name.split("(")[0].trim()}</td>`;
    html += `<td class="center">${f.levels[selections[f.id]].label.split("(")[0].trim()}</td>`;
    html += `<td class="center mono">${selections[f.id]}/${maxLevel}</td>`;
    html += `<td class="center mono">${f.weight}%</td>`;
    html += `<td class="center mono" style="font-weight:700; color:${contribution > 0 ? color : '#94a3b8'}">${contribution.toFixed(1)}</td>`;
    html += '</tr>';
  });

  html += `<tr class="total-row"><td colspan="4">Total PCS</td><td class="center mono" style="color:${color}">${score}</td></tr>`;
  html += '</tbody></table>';
  html += '</div>';

  html += '<div class="weight-rationale">';
  html += '<strong>Weight rationale:</strong> Septal anatomy and ablation scope are weighted highest because they are the strongest drivers of intra-procedural difficulty. Cardiac history follows closely because redo or surgically altered cases can meaningfully increase mapping and access complexity. BMI, ASA score, and anticoagulation matter too, but they affect more secondary timing burdens rather than the main bottleneck steps.';
  html += '</div>';
  html += '</div>';

  html += '<div class="schedule-ref">';
  html += '<div class="section-title">Case Sequence Reference</div>';
  html += '<div class="schedule-title">Suggested daily pattern: Medium → High → Medium → Low</div>';
  html += '<div class="schedule-grid">';
  scheduleSlots.forEach(s => {
    const isActive = s.pcs === category;
    html += `<div class="schedule-slot" style="border-top: 3px solid ${s.color}; opacity:${isActive ? 1 : 0.55}; transform:${isActive ? "translateY(-2px)" : "none"};">`;
    html += `<div class="slot-label">${s.slot}</div>`;
    html += `<div class="slot-pcs" style="color:${s.color}">${s.pcs}</div>`;
    html += `<div class="slot-time">${s.time}</div>`;
    html += `<div class="slot-reason">${s.reason}</div>`;
    html += '</div>';
  });
  html += '</div>';
  html += '<div class="footer-note">This layout is meant to help explain where a patient best fits in the daily sequence, not to replace clinical judgment.</div>';
  html += '</div>';

  html += '</div>';
  html += '</div>';

  document.getElementById("app").innerHTML = html;
}

function selectLevel(factorId, level) {
  selections[factorId] = level;
  render();
}

function toggleBreakdown() {
  showBreakdown = !showBreakdown;
  render();
}

render();
</script>
</body>
</html>"""

PORT = 8050


class QuietHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def log_message(self, format, *args):
        pass


def main():
    server = http.server.HTTPServer(("localhost", PORT), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://localhost:{PORT}"
    print(f"PCS Calculator running at: {url}")
    print("Press Ctrl+C to stop.")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        thread.join()
    except KeyboardInterrupt:
        print("\\nStopped.")
        server.shutdown()


if __name__ == "__main__":
    main()