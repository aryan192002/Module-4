"""
Patient Complexity Score (PCS) Interactive Calculator
MSE 433 Module 4 — EP Lab AFib Ablation

Run: python pcs_calculator.py
Opens in your default browser. No dependencies required.
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
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0f1117; color: #e8e6e3; font-family: 'Segoe UI', system-ui, sans-serif; padding: 32px; }
.container { max-width: 900px; margin: 0 auto; }
h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
.subtitle { color: #64748b; font-size: 14px; margin-bottom: 32px; }
.tag { font-size: 11px; color: #4ecdc4; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 6px; font-family: monospace; }
.factor-card { background: #1a1d27; border-radius: 10px; padding: 20px; margin-bottom: 16px; }
.factor-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.factor-name { font-size: 15px; font-weight: 600; }
.factor-weight { font-size: 11px; color: #64748b; margin-left: 10px; }
.factor-affects { font-size: 11px; color: #64748b; }
.factor-affects span { color: #4ecdc4; }
.btn-group { display: flex; gap: 6px; flex-wrap: wrap; }
.btn { padding: 8px 16px; font-size: 12px; cursor: pointer; border-radius: 6px; background: transparent; color: #64748b; border: 1px solid #2a2d3a; font-family: inherit; transition: all 0.15s; }
.btn:hover { border-color: #4ecdc4; color: #4ecdc4; }
.btn.selected { font-weight: 700; }
.btn.s0.selected { background: #00B89422; color: #00B894; border-color: #00B894; }
.btn.s1.selected { background: #FFE66D22; color: #FFE66D; border-color: #FFE66D; }
.btn.s2.selected { background: #FF6B6B22; color: #FF6B6B; border-color: #FF6B6B; }
.btn.s3.selected { background: #d6303122; color: #d63031; border-color: #d63031; }
.effect-text { margin-top: 10px; font-size: 12px; color: #64748b; font-style: italic; }
.result-card { background: #1a1d27; border-radius: 12px; padding: 28px; margin-bottom: 24px; border-left: 4px solid #00B894; }
.result-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 16px; }
.score-label { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; }
.score-value { font-size: 52px; font-weight: 700; font-family: monospace; line-height: 1; }
.score-max { font-size: 22px; color: #64748b; }
.category { font-size: 22px; font-weight: 700; }
.recommended { font-size: 14px; color: #64748b; margin-top: 6px; }
.recommended strong { color: #4ecdc4; }
.score-bar { height: 10px; background: #0d0f15; border-radius: 5px; overflow: hidden; margin-bottom: 16px; }
.score-fill { height: 100%; border-radius: 5px; transition: width 0.4s ease; }
.rationale-box { background: #0d0f15; border-radius: 8px; padding: 14px; }
.rationale-label { font-size: 11px; font-weight: 700; color: #4ecdc4; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 1px; }
.rationale-text { color: #64748b; font-size: 13px; line-height: 1.6; }
.steps-affected { margin-top: 14px; }
.steps-affected .label { font-size: 11px; color: #64748b; margin-bottom: 6px; }
.step-tag { display: inline-block; font-size: 11px; padding: 4px 10px; border-radius: 4px; font-family: monospace; margin: 2px 4px 2px 0; }
.toggle-btn { background: transparent; border: 1px solid #2a2d3a; color: #64748b; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit; margin-bottom: 16px; width: 100%; }
.toggle-btn:hover { border-color: #4ecdc4; color: #4ecdc4; }
.breakdown { background: #1a1d27; border-radius: 12px; padding: 24px; margin-bottom: 20px; display: none; }
.breakdown.show { display: block; }
.formula { font-family: monospace; font-size: 13px; color: #4ecdc4; margin-bottom: 16px; line-height: 1.8; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { text-align: left; padding: 8px 10px; color: #64748b; font-weight: 600; font-size: 11px; border-bottom: 1px solid #2a2d3a; }
th.center, td.center { text-align: center; }
td { padding: 8px 10px; border-bottom: 1px solid #2a2d3a15; }
td.mono { font-family: monospace; }
.total-row td { border-top: 2px solid #2a2d3a; font-weight: 700; font-size: 18px; }
.weight-rationale { margin-top: 16px; font-size: 12px; color: #64748b; line-height: 1.6; }
.weight-rationale strong { color: #e8e6e3; }
.schedule-ref { background: #1a1d27; border-radius: 12px; padding: 20px; margin-top: 20px; }
.schedule-title { font-size: 14px; font-weight: 700; margin-bottom: 12px; }
.schedule-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.schedule-slot { background: #0d0f15; border-radius: 8px; padding: 12px; text-align: center; transition: opacity 0.3s; }
.schedule-slot .slot-label { font-size: 12px; font-weight: 700; }
.schedule-slot .slot-pcs { font-size: 11px; font-weight: 700; margin: 4px 0; }
.schedule-slot .slot-time { font-size: 10px; color: #64748b; }
.schedule-slot .slot-reason { font-size: 10px; color: #64748b; margin-top: 4px; }
@media (max-width: 600px) {
  body { padding: 16px; }
  .score-value { font-size: 36px; }
  .category { font-size: 18px; }
  .schedule-grid { grid-template-columns: repeat(2, 1fr); }
  .factor-header { flex-direction: column; align-items: flex-start; }
}
</style>
</head>
<body>
<div class="container" id="app"></div>

<script>
const factors = [
  {
    id: "bmi", name: "BMI Category", weight: 15,
    levels: [
      { label: "Normal (18.5–25)", effect: "Baseline vascular access difficulty, standard anesthesia" },
      { label: "Overweight (25–30)", effect: "+1–2 min access (deeper vein), slightly longer intubation" },
      { label: "Obese (30–40)", effect: "+3–5 min access (US-guided likely needed), harder intubation" },
      { label: "Morbidly Obese (>40)", effect: "+5–10 min total; may need special table, difficult hemostasis" }
    ],
    affects: ["Pt Prep/Intubation", "Vascular Access", "Post-Care"],
    rationale: "BMI is a top-5 predictor in ML surgical duration models (BMJ 2023 scoping review)"
  },
  {
    id: "cardiac", name: "Cardiac History", weight: 20,
    levels: [
      { label: "First-time AFib ablation", effect: "Standard anatomy, no scar tissue" },
      { label: "Prior cardiac catheterization", effect: "Known vascular anatomy, may have scar tissue at access site" },
      { label: "Prior ablation (redo)", effect: "+10–20 min; scar tissue complicates mapping and TSP" },
      { label: "Prior cardiac surgery", effect: "Significantly altered anatomy; TSP may be extremely difficult" }
    ],
    affects: ["TSP", "Pre-Map", "Ablation"],
    rationale: "Redo cases are 1.5–2x longer per literature; scar tissue complicates TSP and mapping"
  },
  {
    id: "anatomy", name: "Septal Anatomy (from pre-op imaging)", weight: 25,
    levels: [
      { label: "Normal / thin septum", effect: "TSP expected 2–5 min" },
      { label: "Thickened septum", effect: "TSP 5–10 min; may need RF-assisted puncture" },
      { label: "Lipomatous / aneurysmal septum", effect: "TSP 10–20 min; specialized techniques required" },
      { label: "Prior septal closure / PFO device", effect: "TSP >20 min or may require alternative approach" }
    ],
    affects: ["TSP"],
    rationale: "TSP has CV=89% — the highest variability step; pre-op imaging predicts difficulty"
  },
  {
    id: "ablation_scope", name: "Planned Ablation Scope", weight: 25,
    levels: [
      { label: "Standard PVI only (4 veins)", effect: "17–20 ABL sites, ~25 min ABL duration" },
      { label: "PVI + 1 extra target (CTI or SVC)", effect: "22–25 ABL sites, ~35 min" },
      { label: "PVI + BOX or PST BOX", effect: "25–28 ABL sites, ~45 min" },
      { label: "PVI + multiple extras (BOX+CTI+AAFL)", effect: "28–30+ ABL sites, 60+ min" }
    ],
    affects: ["Ablation", "Verification"],
    rationale: "Extra targets add 14.2 min on average (p=0.0003) — strongest effect in our data"
  },
  {
    id: "comorbidity", name: "Comorbidity / ASA Score", weight: 10,
    levels: [
      { label: "ASA I–II (healthy / mild systemic)", effect: "Standard anesthesia, fast recovery" },
      { label: "ASA III (severe systemic disease)", effect: "+2–3 min prep, longer post-care monitoring" },
      { label: "ASA IV (severe, constant threat)", effect: "+5+ min prep, extended monitoring, slower extubation" }
    ],
    affects: ["Pt Prep/Intubation", "Post-Care"],
    rationale: "ASA score predicts anesthesia complexity and recovery time"
  },
  {
    id: "anticoag", name: "Anticoagulation Status", weight: 5,
    levels: [
      { label: "Standard protocol (held appropriately)", effect: "Normal hemostasis expected" },
      { label: "Therapeutic anticoagulation (bridged)", effect: "+3–5 min post-care for hemostasis" },
      { label: "Dual antiplatelet / complex regimen", effect: "+5–10 min post-care; may need closure device" }
    ],
    affects: ["Catheter Removal", "Post-Care"],
    rationale: "Therapeutic anticoag adds 3–5 min hemostasis time in post-care"
  }
];

const scheduleSlots = [
  { slot: "Case 1", pcs: "Medium", time: "~8:00 AM", reason: "Warm-up case", color: "#FFE66D" },
  { slot: "Case 2", pcs: "HIGH", time: "~10:00 AM", reason: "Peak cognition + warmed up", color: "#FF6B6B" },
  { slot: "Case 3", pcs: "Medium", time: "~12:00 PM", reason: "Lunch break buffers fatigue", color: "#FFE66D" },
  { slot: "Case 4", pcs: "Low", time: "~2:30 PM", reason: "Routine — fatigue-resilient", color: "#00B894" }
];

const rationales = {
  High: "Peak cognitive resources needed for complex decision-making (TSP navigation, multi-target ablation). Research shows cognitively demanding tasks are most impaired by fatigue. Schedule as the 2nd case when team is warmed up AND cognition is near-peak.",
  Medium: "The 1st or 3rd case slot balances team warm-up with sufficient remaining cognitive resources. These cases benefit from the warm-up effect without needing peak cognition.",
  Low: "Standard PVI with normal anatomy. Routine cases rely on automatized psychomotor skills, which research shows are maintained even under moderate fatigue. Preserves peak cognitive slots for harder cases."
};

let selections = { bmi: 0, cardiac: 0, anatomy: 0, ablation_scope: 0, comorbidity: 0, anticoag: 0 };
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
  return score > 60 ? "High" : score > 30 ? "Medium" : "Low";
}

function getCategoryColor(score) {
  return score > 60 ? "#FF6B6B" : score > 30 ? "#FFE66D" : "#00B894";
}

function getSlot(cat) {
  return cat === "High" ? "2nd case of day" : cat === "Medium" ? "1st or 3rd case" : "4th case (last)";
}

function render() {
  const score = computeScore();
  const cat = getCategory(score);
  const color = getCategoryColor(score);
  const slot = getSlot(cat);

  const affectedSteps = [];
  factors.forEach(f => {
    if (selections[f.id] > 0) {
      f.affects.forEach(step => { if (!affectedSteps.includes(step)) affectedSteps.push(step); });
    }
  });

  let html = '';
  html += '<div class="tag">Capturing Unobserved Factor 1</div>';
  html += '<h1>Patient Complexity Score Calculator</h1>';
  html += '<p class="subtitle">Select patient characteristics below. The PCS captures 6 pre-operative factors currently invisible in the EP Lab dataset.</p>';

  // Factor cards
  factors.forEach(f => {
    html += '<div class="factor-card">';
    html += '<div class="factor-header">';
    html += `<div><span class="factor-name">${f.name}</span><span class="factor-weight">Weight: ${f.weight}%</span></div>`;
    html += `<div class="factor-affects">Affects: <span>${f.affects.join(", ")}</span></div>`;
    html += '</div>';
    html += '<div class="btn-group">';
    f.levels.forEach((l, i) => {
      const sel = selections[f.id] === i ? `selected s${i}` : `s${i}`;
      html += `<button class="btn ${sel}" onclick="select('${f.id}', ${i})">${l.label}</button>`;
    });
    html += '</div>';
    if (selections[f.id] > 0) {
      html += `<div class="effect-text">Effect: ${f.levels[selections[f.id]].effect}</div>`;
    }
    html += '</div>';
  });

  // Result card
  html += `<div class="result-card" style="border-left-color: ${color}">`;
  html += '<div class="result-top">';
  html += '<div>';
  html += '<div class="score-label">Patient Complexity Score</div>';
  html += `<div class="score-value" style="color: ${color}">${score}<span class="score-max">/100</span></div>`;
  html += '</div>';
  html += '<div style="text-align: right">';
  html += `<div class="category" style="color: ${color}">${cat} Complexity</div>`;
  html += `<div class="recommended">Recommended: <strong>${slot}</strong></div>`;
  html += '</div></div>';

  html += '<div class="score-bar">';
  html += `<div class="score-fill" style="width: ${Math.min(100, score)}%; background: linear-gradient(90deg, #00B894, ${score > 30 ? '#FFE66D' : '#00B894'}, ${score > 60 ? '#FF6B6B' : score > 30 ? '#FFE66D' : '#00B894'})"></div>`;
  html += '</div>';

  html += '<div class="rationale-box">';
  html += '<div class="rationale-label">Scheduling Rationale</div>';
  html += `<div class="rationale-text">${rationales[cat]}</div>`;
  html += '</div>';

  if (affectedSteps.length > 0) {
    html += '<div class="steps-affected">';
    html += '<div class="label">Procedure steps affected by selected factors:</div>';
    affectedSteps.forEach(step => {
      html += `<span class="step-tag" style="background: ${color}15; color: ${color}">${step}</span>`;
    });
    html += '</div>';
  }
  html += '</div>';

  // Toggle breakdown
  html += `<button class="toggle-btn" onclick="toggleBreakdown()">${showBreakdown ? 'Hide' : 'Show'} Score Breakdown & Formula</button>`;

  // Breakdown table
  html += `<div class="breakdown ${showBreakdown ? 'show' : ''}">`;
  html += '<div class="formula">PCS = &Sigma; (factor_score / factor_max) &times; factor_weight</div>';
  html += '<table><thead><tr>';
  html += '<th>Factor</th><th class="center">Selection</th><th class="center">Score/Max</th><th class="center">Weight</th><th class="center">Contribution</th>';
  html += '</tr></thead><tbody>';
  factors.forEach(f => {
    const maxLevel = f.levels.length - 1;
    const contribution = (selections[f.id] / maxLevel) * f.weight;
    const cColor = contribution > 0 ? color : '#64748b';
    html += '<tr>';
    html += `<td>${f.name.split("(")[0].trim()}</td>`;
    html += `<td class="center" style="font-size:12px;color:#64748b">${f.levels[selections[f.id]].label.split("(")[0].trim()}</td>`;
    html += `<td class="center mono">${selections[f.id]}/${maxLevel}</td>`;
    html += `<td class="center mono" style="color:#4ecdc4">${f.weight}%</td>`;
    html += `<td class="center mono" style="font-weight:700;color:${cColor}">${contribution.toFixed(1)}</td>`;
    html += '</tr>';
  });
  html += `<tr class="total-row"><td colspan="4">Total PCS</td><td class="center mono" style="color:${color}">${score}</td></tr>`;
  html += '</tbody></table>';
  html += '<div class="weight-rationale"><strong>Weight rationale: </strong>';
  html += 'Septal Anatomy (25%) and Ablation Scope (25%) receive the highest weights because TSP variability (CV=89%) and extra targets (+14.2 min, p=0.0003) are the strongest drivers identified in our data analysis. Cardiac History (20%) is weighted third because redo cases are 1.5&ndash;2&times; longer per literature. BMI (15%), ASA (10%), and Anticoagulation (5%) have progressively lower weights as they primarily affect non-bottleneck steps.</div>';
  html += '</div>';

  // Schedule reference
  html += '<div class="schedule-ref">';
  html += '<div class="schedule-title">Optimal Daily Case Sequence: Med &rarr; High &rarr; Med &rarr; Low</div>';
  html += '<div class="schedule-grid">';
  scheduleSlots.forEach(s => {
    const matchCat = s.pcs === "HIGH" ? "High" : s.pcs;
    const opacity = matchCat === cat ? 1 : 0.4;
    html += `<div class="schedule-slot" style="border-top: 3px solid ${s.color}; opacity: ${opacity}">`;
    html += `<div class="slot-label">${s.slot}</div>`;
    html += `<div class="slot-pcs" style="color: ${s.color}">${s.pcs}</div>`;
    html += `<div class="slot-time">${s.time}</div>`;
    html += `<div class="slot-reason">${s.reason}</div>`;
    html += '</div>';
  });
  html += '</div></div>';

  document.getElementById('app').innerHTML = html;
}

function select(factorId, level) {
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

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def log_message(self, format, *args):
        pass  # suppress console spam

def main():
    server = http.server.HTTPServer(("localhost", PORT), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://localhost:{PORT}"
    print(f"\n  PCS Calculator running at: {url}")
    print(f"  Press Ctrl+C to stop\n")
    webbrowser.open(url)
    try:
        thread.join()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        server.shutdown()

if __name__ == "__main__":
    main()
