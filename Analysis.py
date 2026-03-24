"""
MSE433 Module 4 – EP Lab AFib Ablation Procedure Analysis
==========================================================
Generates 10 clean figures + printed summary tables.

How to run:
    python MSE433_M4_Analysis.py

Both files must be in the same folder:
    MSE433_M4_Data.xlsx
    MSE433_M4_Analysis.py
"""

import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from scipy import stats

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH = "MSE433_M4_Data.xlsx"
OUT_DIR   = "."
os.makedirs(OUT_DIR, exist_ok=True)

# ── Global style ──────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "figure.dpi": 150,
    "figure.facecolor": "white",
    "axes.facecolor": "#F7F9FC",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "font.family": "DejaVu Sans",
})

COLORS     = {"Dr. A": "#1976D2", "Dr. B": "#D32F2F", "Dr. C": "#388E3C"}
PHYSICIANS = ["Dr. A", "Dr. B", "Dr. C"]
PALETTE    = [COLORS[p] for p in PHYSICIANS]
PHASE_PAL  = ["#3F51B5","#009688","#E53935","#FF9800","#9C27B0","#607D8B","#E91E63"]

# ── Load & clean ──────────────────────────────────────────────────────────────
df_raw = pd.read_excel(DATA_PATH, header=2)
df     = df_raw.dropna(how="all").iloc[1:].copy()
df.columns = df.columns.str.strip()
df = df.rename(columns={"ACCESSS": "ACCESS"})

NUM = ["PT PREP/INTUBATION","ACCESS","TSP","PRE-MAP","ABL DURATION",
       "ABL TIME","#ABL","#APPLICATIONS","LA DWELL TIME","CASE TIME",
       "SKIN-SKIN","POST CARE/EXTUBATION","PT IN-OUT"]
for c in NUM:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df["CASE #"] = pd.to_numeric(df["CASE #"], errors="coerce")
df["DATE"]   = pd.to_datetime(df["DATE"], errors="coerce")
df["Note"]   = df["Note"].fillna("Standard PVI")
df["REPOSITION TIME"] = df["ABL DURATION"] - df["ABL TIME"]
df["ABL_EFF_%"]       = (df["ABL TIME"] / df["ABL DURATION"] * 100).round(1)
df["STD_PVI"]         = df["Note"] == "Standard PVI"

std = df[df["STD_PVI"]].copy()

# ── Console tables ────────────────────────────────────────────────────────────
DIV = "=" * 72

def sec(t): print(f"\n{DIV}\n  {t}\n{DIV}")

sec("DATASET OVERVIEW")
print(f"  Cases: {len(df)}   |   Date range: {df['DATE'].min().date()} -> {df['DATE'].max().date()}")
for p in PHYSICIANS:
    print(f"  {p}: {(df['PHYSICIAN']==p).sum()} cases")
print("\n  Extra-target distribution:")
print(df["Note"].value_counts().to_string())

sec("OVERALL DESCRIPTIVE STATISTICS")
show = ["PT PREP/INTUBATION","ACCESS","TSP","PRE-MAP","ABL DURATION",
        "ABL TIME","REPOSITION TIME","CASE TIME","POST CARE/EXTUBATION","PT IN-OUT"]
print(df[show].describe().round(1).to_string())

sec("CASE TIME BY PHYSICIAN — All cases")
print(df.groupby("PHYSICIAN")["CASE TIME"].describe().round(1).to_string())

sec("CASE TIME BY PHYSICIAN — Standard PVI Only")
print(std.groupby("PHYSICIAN")["CASE TIME"].describe().round(1).to_string())

sec("MEAN +/- STD PER PHASE PER PHYSICIAN (Standard PVI only)")
phases = ["PT PREP/INTUBATION","ACCESS","TSP","PRE-MAP","ABL DURATION",
          "ABL TIME","REPOSITION TIME","POST CARE/EXTUBATION","CASE TIME","PT IN-OUT"]
for p in PHYSICIANS:
    print(f"\n  {p}:")
    sub = std[std["PHYSICIAN"]==p]
    for c in phases:
        print(f"    {c:<28}  mean={sub[c].mean():>6.1f}  std={sub[c].std():>5.1f}")

sec("CORRELATION WITH CASE TIME (Standard PVI only)")
cc = ["PT PREP/INTUBATION","ACCESS","TSP","PRE-MAP",
      "ABL DURATION","REPOSITION TIME","POST CARE/EXTUBATION"]
corr = std[cc+["CASE TIME"]].corr()["CASE TIME"].drop("CASE TIME").sort_values(ascending=False)
print(f"\n  {'Phase':<32} {'r':>7}   Strength")
print("-"*55)
for col, r in corr.items():
    s = "Strong" if abs(r)>=0.7 else "Moderate" if abs(r)>=0.4 else "Weak"
    print(f"  {col:<32} {r:>+.3f}   {s}")

sec("ABLATION EFFICIENCY BY PHYSICIAN")
print(df.groupby("PHYSICIAN")[["ABL DURATION","ABL TIME","REPOSITION TIME","ABL_EFF_%"]].mean().round(1).to_string())

sec("TSP STATS BY PHYSICIAN")
print(df.groupby("PHYSICIAN")["TSP"].describe().round(1).to_string())

sec("EFFECT OF ADDITIONAL ABLATION TARGETS")
ns = df.groupby("Note")["CASE TIME"].agg(["count","mean","std","min","max"])
ns.columns = ["N","Mean","Std","Min","Max"]
print(ns.round(1).sort_values("Mean", ascending=False).to_string())

sec("LEARNING CURVE — First 20 vs Last 20 per Physician")
for p in PHYSICIANS:
    sub = df[df["PHYSICIAN"]==p].sort_values("CASE #")["CASE TIME"].dropna()
    if len(sub) >= 20:
        f, l = sub.head(20).mean(), sub.tail(20).mean()
        print(f"  {p}:  First 20 = {f:.1f} min  |  Last 20 = {l:.1f} min  |  Delta = {l-f:+.1f} min ({(l-f)/f*100:+.1f}%)")

sec("KRUSKAL-WALLIS TEST — Physician differences on Case Time")
groups = [std[std["PHYSICIAN"]==p]["CASE TIME"].dropna().values for p in PHYSICIANS]
H, pv = stats.kruskal(*groups)
print(f"\n  H = {H:.2f},  p = {pv:.4f}")
print(f"  -> {'SIGNIFICANT' if pv<0.05 else 'NOT significant'} difference between physicians (alpha = 0.05)")

print("\n\n  Generating figures...\n")

# ── Save helper ───────────────────────────────────────────────────────────────
def save(fig, name):
    p = os.path.join(OUT_DIR, name)
    fig.savefig(p, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  OK  {name}")

# =============================================================================
# FIG 1 — Case Time: grouped box plots
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Figure 1 — Case Time Distribution by Physician",
             fontsize=14, fontweight="bold", y=1.02)

for ax, (data, subtitle) in zip(axes, [
        (df,  "All Cases  (n = 150)"),
        (std, "Standard PVI Only  (no extra ablation targets)")]):

    data_v = data[data["CASE TIME"].notna()]
    bp = ax.boxplot(
        [data_v[data_v["PHYSICIAN"]==p]["CASE TIME"].values for p in PHYSICIANS],
        patch_artist=True,
        widths=0.45,
        medianprops=dict(color="white", linewidth=2.5),
        whiskerprops=dict(linewidth=1.5),
        capprops=dict(linewidth=1.5),
        flierprops=dict(marker="o", markersize=5, alpha=0.5),
        boxprops=dict(linewidth=1.5)
    )
    for patch, p in zip(bp["boxes"], PHYSICIANS):
        patch.set_facecolor(COLORS[p])
        patch.set_alpha(0.85)
    for flier, p in zip(bp["fliers"], PHYSICIANS):
        flier.set(markerfacecolor=COLORS[p], markeredgecolor=COLORS[p])

    for i, p in enumerate(PHYSICIANS, 1):
        vals = data_v[data_v["PHYSICIAN"]==p]["CASE TIME"].dropna()
        med  = vals.median()
        mn   = vals.mean()
        ax.text(i, med, f"Med={med:.0f}", ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="white",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=COLORS[p], alpha=0.8))
        n = len(vals)
        ax.text(i, ax.get_ylim()[0] if ax.get_ylim()[0] != 0 else vals.min() - 5,
                f"n={n}", ha="center", fontsize=9, color="grey")

    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(PHYSICIANS, fontsize=12)
    ax.set_ylabel("Case Time (minutes)", fontsize=11)
    ax.set_xlabel("Physician", fontsize=11)
    ax.set_title(subtitle, fontsize=11, pad=8)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

patches = [plt.Rectangle((0,0),1,1, facecolor=COLORS[p], alpha=0.85, label=p)
           for p in PHYSICIANS]
axes[1].legend(handles=patches, loc="upper right")
plt.tight_layout()
save(fig, "Fig1_CaseTime_Boxplot.png")

# =============================================================================
# FIG 2 — Stacked bar: mean phase breakdown per physician
# =============================================================================
phases_stk = ["PT PREP/INTUBATION","ACCESS","TSP","PRE-MAP",
               "ABL TIME","REPOSITION TIME","POST CARE/EXTUBATION"]
labels_stk = ["Prep / Intubation","Vascular Access","Transseptal Puncture (TSP)",
               "Pre-Mapping","Active Ablation","Catheter Repositioning",
               "Post Care / Extubation"]

means = std.groupby("PHYSICIAN")[phases_stk].mean()

fig, ax = plt.subplots(figsize=(10, 7))
bottoms = np.zeros(3)
x = np.arange(3)

for i, (col, lbl) in enumerate(zip(phases_stk, labels_stk)):
    vals = [means.loc[p, col] for p in PHYSICIANS]
    bars = ax.bar(x, vals, bottom=bottoms, color=PHASE_PAL[i],
                  label=lbl, edgecolor="white", linewidth=1.2)
    for j, (bar, v) in enumerate(zip(bars, vals)):
        if v >= 2:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bottoms[j] + v/2,
                    f"{v:.1f}", ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold")
    bottoms += np.array(vals)

for i, p in enumerate(PHYSICIANS):
    total = bottoms[i]
    ax.text(i, total + 0.8, f"Total\n{total:.0f} min",
            ha="center", va="bottom", fontsize=9.5, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(PHYSICIANS, fontsize=12)
ax.set_ylabel("Mean Duration (minutes)", fontsize=11)
ax.set_xlabel("Physician", fontsize=11)
ax.set_title("Figure 2 — Mean Procedural Phase Breakdown per Physician\n"
             "Standard PVI Only — numbers inside bars are minutes",
             fontsize=13, fontweight="bold")
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=9.5)
ax.yaxis.grid(True, linestyle="--", alpha=0.6)
ax.set_axisbelow(True)
plt.tight_layout()
save(fig, "Fig2_Phase_Breakdown_Stacked.png")

# =============================================================================
# FIG 3 — TSP histograms per physician
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Figure 3 — Transseptal Puncture (TSP) Duration by Physician\n"
             "TSP is the 2nd strongest driver of total case time  (r = 0.60)",
             fontsize=13, fontweight="bold", y=1.02)

for ax, p in zip(axes, PHYSICIANS):
    data = df[df["PHYSICIAN"]==p]["TSP"].dropna()
    max_bin = max(int(data.max()) + 4, 10)
    ax.hist(data, bins=range(0, max_bin, 2),
            color=COLORS[p], edgecolor="white", linewidth=0.8, alpha=0.88)
    ax.axvline(data.mean(),   color="black",   lw=2, ls="--",
               label=f"Mean = {data.mean():.1f} min")
    ax.axvline(data.median(), color="#FF9800",  lw=2, ls="-",
               label=f"Median = {data.median():.1f} min")
    ax.set_title(f"{p}   (n = {len(data)})\nStd = {data.std():.1f} min", fontsize=11)
    ax.set_xlabel("TSP Duration (minutes)", fontsize=10)
    ax.set_ylabel("Number of Cases", fontsize=10)
    ax.legend(fontsize=9)
    ax.yaxis.grid(True, linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)

plt.tight_layout()
save(fig, "Fig3_TSP_Distribution.png")

# =============================================================================
# FIG 4 — Correlation heatmap
# =============================================================================
corr_raw = ["PT PREP/INTUBATION","ACCESS","TSP","PRE-MAP",
            "ABL DURATION","ABL TIME","REPOSITION TIME",
            "POST CARE/EXTUBATION","CASE TIME","PT IN-OUT"]
corr_lbl = ["Prep/Intubation","Access","TSP","Pre-Map",
            "Abl Duration","Abl Time","Reposition Time",
            "Post Care","Case Time","Pt In-Out"]

cm = std[corr_raw].corr()
cm.index   = corr_lbl
cm.columns = corr_lbl
mask = np.triu(np.ones_like(cm, dtype=bool), k=1)

fig, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(cm, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn",
            center=0, vmin=-1, vmax=1, linewidths=0.6,
            annot_kws={"size": 10}, ax=ax,
            cbar_kws={"shrink": 0.7, "label": "Pearson r"})
ax.set_title("Figure 4 — Correlation Matrix of All Procedural Phases\n"
             "Standard PVI only — read the 'Case Time' row to rank bottlenecks",
             fontsize=12, fontweight="bold", pad=15)
ax.tick_params(axis="x", rotation=30, labelsize=10)
ax.tick_params(axis="y", rotation=0,  labelsize=10)
plt.tight_layout()
save(fig, "Fig4_Correlation_Heatmap.png")

# =============================================================================
# FIG 5 — Ranked bar: bottleneck drivers
# =============================================================================
corr_r = (std[corr_raw].corr()["CASE TIME"]
          .drop(["CASE TIME","PT IN-OUT"])
          .sort_values())
# rename for display
rename = dict(zip(corr_raw, corr_lbl))
corr_r.index = [rename.get(i, i) for i in corr_r.index]

fig, ax = plt.subplots(figsize=(11, 5))
colors_bar = ["#E53935" if v>=0.7 else "#FB8C00" if v>=0.4 else "#43A047"
              for v in corr_r.values]
bars = ax.barh(corr_r.index, corr_r.values, color=colors_bar,
               edgecolor="white", height=0.55)
for bar, v in zip(bars, corr_r.values):
    ax.text(v + 0.012, bar.get_y() + bar.get_height()/2,
            f"r = {v:.3f}", va="center", fontsize=10.5, fontweight="bold")

ax.axvline(0.7, color="#E53935", ls="--", lw=1.5, label="Strong  (r >= 0.70)")
ax.axvline(0.4, color="#FB8C00", ls="--", lw=1.5, label="Moderate  (r >= 0.40)")
ax.set_xlim(0, 1.05)
ax.set_xlabel("Pearson Correlation with Total Case Time", fontsize=11)
ax.set_title("Figure 5 — Which Phases Drive Total Case Time?\n"
             "Standard PVI only  |  Red = strong driver, Orange = moderate, Green = weak",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=9, loc="lower right")
ax.xaxis.grid(True, linestyle="--", alpha=0.6)
ax.set_axisbelow(True)
plt.tight_layout()
save(fig, "Fig5_Bottleneck_Ranking.png")

# =============================================================================
# FIG 6 — Active ablation vs repositioning time (grouped bar)
# =============================================================================
abl_data = df.groupby("PHYSICIAN")[["ABL TIME","REPOSITION TIME"]].mean()

fig, ax = plt.subplots(figsize=(10, 6))
x  = np.arange(3)
w  = 0.35
b1 = ax.bar(x - w/2, abl_data["ABL TIME"],        w,
            label="Active Ablation (energy on)",
            color="#E53935", edgecolor="white", alpha=0.88)
b2 = ax.bar(x + w/2, abl_data["REPOSITION TIME"], w,
            label="Catheter Repositioning (energy off)",
            color="#1976D2", edgecolor="white", alpha=0.88)

for bar in list(b1) + list(b2):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{bar.get_height():.1f} min", ha="center", fontsize=10, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(PHYSICIANS, fontsize=12)
ax.set_ylabel("Mean Duration (minutes)", fontsize=11)
ax.set_xlabel("Physician", fontsize=11)
ax.set_title("Figure 6 — Active Ablation Time vs Catheter Repositioning Time\n"
             "Only ~30% of the ablation phase is actual energy delivery",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.yaxis.grid(True, linestyle="--", alpha=0.6)
ax.set_axisbelow(True)
plt.tight_layout()
save(fig, "Fig6_Ablation_Efficiency.png")

# =============================================================================
# FIG 7 — Repositioning time histograms
# =============================================================================
fig, ax = plt.subplots(figsize=(11, 6))
for p in PHYSICIANS:
    data = df[df["PHYSICIAN"]==p]["REPOSITION TIME"].dropna()
    ax.hist(data, bins=20, alpha=0.55, label=p,
            color=COLORS[p], edgecolor="white")
    ax.axvline(data.mean(), color=COLORS[p], lw=2.5, ls="--",
               label=f"{p} mean = {data.mean():.1f} min")

ax.set_xlabel("Catheter Repositioning Time (minutes)", fontsize=11)
ax.set_ylabel("Number of Cases", fontsize=11)
ax.set_title("Figure 7 — Catheter Repositioning Time Distribution by Physician\n"
             "Dashed lines = physician mean  |  Dr. B has the longest & most variable repositioning",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=9)
ax.yaxis.grid(True, linestyle="--", alpha=0.6)
ax.set_axisbelow(True)
plt.tight_layout()
save(fig, "Fig7_Repositioning_Distribution.png")

# =============================================================================
# FIG 8 — Learning curve
# =============================================================================
fig, ax = plt.subplots(figsize=(13, 6))
df_s = df.sort_values("CASE #")

for p in PHYSICIANS:
    sub  = df_s[df_s["PHYSICIAN"]==p][["CASE #","CASE TIME"]].dropna().reset_index(drop=True)
    idx  = sub.index + 1
    ax.scatter(idx, sub["CASE TIME"], color=COLORS[p], alpha=0.3, s=35, zorder=2)
    roll = sub["CASE TIME"].rolling(5, center=True, min_periods=3).mean()
    ax.plot(idx, roll, color=COLORS[p], lw=2.5,
            label=f"{p}  (5-case rolling avg)", zorder=3)

ax.set_xlabel("Sequential Case Number (per physician)", fontsize=11)
ax.set_ylabel("Case Time (minutes)", fontsize=11)
ax.set_title("Figure 8 — Learning Curve: Case Time Over Time per Physician\n"
             "Dots = individual cases  |  Lines = 5-case rolling average  |  "
             "Flat trend = no improvement over 9 months",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.yaxis.grid(True, linestyle="--", alpha=0.6)
ax.set_axisbelow(True)
plt.tight_layout()
save(fig, "Fig8_Learning_Curve.png")

# =============================================================================
# FIG 9 — Effect of additional ablation targets
# =============================================================================
note_agg = (df.groupby("Note")["CASE TIME"]
              .agg(["mean","sem","count"])
              .rename(columns={"mean":"Mean","sem":"SEM","count":"N"})
              .sort_values("Mean", ascending=False))

fig, ax = plt.subplots(figsize=(12, 6))
bar_cols = ["#B71C1C" if n=="Standard PVI" else
            "#EF5350" if note_agg.loc[n,"Mean"] < 50 else "#C62828"
            for n in note_agg.index]
bars = ax.bar(range(len(note_agg)), note_agg["Mean"],
              yerr=note_agg["SEM"], capsize=6,
              color=bar_cols, edgecolor="white", linewidth=0.8,
              error_kw=dict(elinewidth=1.5, ecolor="black"))

for bar, mean in zip(bars, note_agg["Mean"]):
    if mean > 10:
        ax.text(bar.get_x() + bar.get_width()/2, mean/2,
                f"{mean:.0f} min", ha="center", va="center",
                fontsize=9.5, color="white", fontweight="bold")
ax.bar_label(bars, labels=[f"n={int(n)}" for n in note_agg["N"]],
             padding=4, fontsize=9)

ax.set_xticks(range(len(note_agg)))
ax.set_xticklabels(note_agg.index, rotation=25, ha="right", fontsize=10)
ax.set_ylabel("Mean Case Time (minutes)", fontsize=11)
ax.set_title("Figure 9 — Impact of Additional Ablation Targets on Case Time\n"
             "Error bars = +/- 1 SEM  |  CTI adds ~30 min vs Standard PVI",
             fontsize=13, fontweight="bold")
ax.yaxis.grid(True, linestyle="--", alpha=0.6)
ax.set_axisbelow(True)
plt.tight_layout()
save(fig, "Fig9_Additional_Targets.png")

# =============================================================================
# FIG 10 — Summary dashboard (2x3 panels)
# =============================================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle("Figure 10 — EP Lab Efficiency Summary Dashboard\n"
             "MSE433 Module 4  |  Standard PVI Cases Only",
             fontsize=15, fontweight="bold", y=1.01)

std_v = std[std["CASE TIME"].notna()]

def styled_boxplot(ax, data_list, title, ylabel="Minutes"):
    bp = ax.boxplot(data_list, patch_artist=True, widths=0.5,
                    medianprops=dict(color="white", linewidth=2.5),
                    flierprops=dict(marker="o", markersize=5, alpha=0.4),
                    whiskerprops=dict(linewidth=1.5),
                    capprops=dict(linewidth=1.5))
    for patch, p in zip(bp["boxes"], PHYSICIANS):
        patch.set_facecolor(COLORS[p]); patch.set_alpha(0.85)
    for flier, p in zip(bp["fliers"], PHYSICIANS):
        flier.set(markerfacecolor=COLORS[p], markeredgecolor=COLORS[p])
    ax.set_xticklabels(PHYSICIANS, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=11)
    ax.yaxis.grid(True, ls="--", alpha=0.6); ax.set_axisbelow(True)

# Panel A
styled_boxplot(axes[0,0],
    [std_v[std_v["PHYSICIAN"]==p]["CASE TIME"].dropna().values for p in PHYSICIANS],
    "A — Case Time")

# Panel B
styled_boxplot(axes[0,1],
    [df[df["PHYSICIAN"]==p]["TSP"].dropna().values for p in PHYSICIANS],
    "B — TSP Duration (Transseptal Puncture)")

# Panel C
styled_boxplot(axes[0,2],
    [df[df["PHYSICIAN"]==p]["REPOSITION TIME"].dropna().values for p in PHYSICIANS],
    "C — Catheter Repositioning Time")

# Panel D
styled_boxplot(axes[1,0],
    [std_v[std_v["PHYSICIAN"]==p]["PT IN-OUT"].dropna().values for p in PHYSICIANS],
    "D — Total Patient Time in Lab\n(Arrival to Departure)")

# Panel E — ablation efficiency bar
ax = axes[1,1]
eff = df.groupby("PHYSICIAN")["ABL_EFF_%"].mean()
bars_e = ax.bar(eff.index, eff.values, color=PALETTE,
                edgecolor="white", alpha=0.88, width=0.5)
for bar, v in zip(bars_e, eff.values):
    ax.text(bar.get_x() + bar.get_width()/2, v + 0.6,
            f"{v:.1f}%", ha="center", fontsize=11, fontweight="bold")
ax.set_ylabel("% of Ablation Phase = Active Energy", fontsize=10)
ax.set_ylim(0, 55)
ax.set_title("E — Ablation Efficiency\n(Active Energy / Total Ablation Time)", fontsize=11)
ax.yaxis.grid(True, ls="--", alpha=0.6); ax.set_axisbelow(True)

# Panel F — grouped bar key phases
ax = axes[1,2]
kp  = ["TSP","ABL DURATION","REPOSITION TIME","PT PREP/INTUBATION"]
klb = ["TSP","Abl\nDuration","Repositioning","Prep"]
xk  = np.arange(len(kp))
wd  = 0.25
for i, p in enumerate(PHYSICIANS):
    vals = [std[std["PHYSICIAN"]==p][c].mean() for c in kp]
    ax.bar(xk + i*wd, vals, wd, label=p, color=COLORS[p], alpha=0.85, edgecolor="white")
ax.set_xticks(xk + wd)
ax.set_xticklabels(klb, fontsize=9.5)
ax.set_ylabel("Mean Duration (minutes)", fontsize=10)
ax.set_title("F — Key Phase Comparison", fontsize=11)
ax.legend(fontsize=9)
ax.yaxis.grid(True, ls="--", alpha=0.6); ax.set_axisbelow(True)

plt.tight_layout()
save(fig, "Fig10_Summary_Dashboard.png")

# ── Done ──────────────────────────────────────────────────────────────────────
print(f"\n{DIV}")
print("  ALL DONE — 10 figures saved to:", os.path.abspath(OUT_DIR))
print(DIV)
print("""
  FIGURE GUIDE
  ------------------------------------------------------------------
  Fig 1  — Case time box plots (all cases + standard PVI only)
  Fig 2  — Stacked bar: mean minutes per phase per physician
  Fig 3  — TSP histograms per physician  (2nd biggest bottleneck)
  Fig 4  — Full correlation heatmap of all phases
  Fig 5  — Ranked bar: which phases drive case time most
  Fig 6  — Grouped bar: active ablation vs repositioning time
  Fig 7  — Repositioning time histograms per physician
  Fig 8  — Learning curve over sequential cases
  Fig 9  — Effect of additional ablation targets on case time
  Fig 10 — 6-panel summary dashboard
  ------------------------------------------------------------------
""")