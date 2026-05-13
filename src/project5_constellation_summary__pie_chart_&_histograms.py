=============================================================================
🛰️ Project 5 — Constellation Summary: Pie Chart & Histograms
=============================================================================
 Author   : Hakim El Azzouzi
 Degree   : MSc Global Navigation Satellite Systems
            Mohammed First University, Oujda, Morocco
 Email    : elazzouzihakim10@gmail.com
 LinkedIn : https://linkedin.com/in/Hakim-El-Azzouzi
 Location : Luxembourg 🇱🇺
-----------------------------------------------------------------------------
 Station  : AUCK00NZL  —  Auckland, New Zealand  (GeoNet / LINZ Network)
 File     : AUCK00NZL_R_20260010000_01D_30S_MO.rnx
 Receiver : TRIMBLE ALLOY
 Antenna  : TRM115000.00
 Format   : RINEX 3.05  |  Mixed Constellations  |  30-second sampling
 Date     : 2026-01-01  (Day-of-Year 001)
-----------------------------------------------------------------------------
 Description
 -----------
## 📌 Overview

After analysing individual satellites in Projects 1–4, this project steps back and asks:

> **What does the full 24-hour RINEX file actually contain — statistically?**

We produce a complete **data summary dashboard** across all five GNSS constellations,
combining four complementary views into one cohesive analysis.

| Plot | What It Shows |
|------|---------------|
| 🥧 Pie + bar chart | Observation share and satellite count per constellation |
| 📊 SNR histogram + box plot | Signal quality distribution, median, IQR, outliers |
| 📈 Pseudorange histogram | Range measurement distribution — each system in its orbital band |
| 🌡️ Full GNSS heatmap | Every satellite from every system over 24 hours |
-----------------------------------------------------------------------------
 **About the projects**
 ----------------------
# Step1: Install & Import Libraries
# Step2: Load the RINEX File
# Step3: Select Satellite and Extract Observables
# Step4: Plot 1: Raw Measurements Overlaid
# Step5: Plot 2: Noise Comparison (Epoch-to-Epoch Differences)
# Step6: Plot 3: Code Minus Phase (C - Φ)
=============================================================================
"""

pip install --upgrade georinex

# ──────────────────────────────────────────────────────────
# Step 1 — Install & Import Libraries
# ──────────────────────────────────────────────────────────
# Install georinex if not already installed
# Uncomment the line below if you are running this for the first time:
# !pip install --upgrade georinex

import georinex as gr
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import warnings

warnings.filterwarnings('ignore')  # suppress xarray FutureWarnings during load

# Global plot style (dark GNSS theme)
plt.rcParams.update({
    'figure.dpi': 120,
})
# ─────────────────────────────────────────────
# Constellation colour palette — consistent across all projects
# ─────────────────────────────────────────────
CONST_COLORS = {
    'G': '#2196F3',   # GPS        — blue
    'R': '#F44336',   # GLONASS    — red
    'E': '#4CAF50',   # Galileo    — green
    'C': '#FF9800',   # BeiDou     — orange
    'J': '#9C27B0',   # QZSS       — purple
    'S': '#00BCD4',   # SBAS       — cyan (if present)
}
CONST_NAMES = {
    'G': 'GPS',
    'R': 'GLONASS',
    'E': 'Galileo',
    'C': 'BeiDou',
    'J': 'QZSS',
    'S': 'SBAS',
}

print('✅ All libraries loaded successfully')
print(f'   georinex version : {gr.__version__}')
print(f'   xarray version   : {xr.__version__}')

# ─────────────────────────────────────────────────────────────────
# Step 2 — Load the RINEX File
# ─────────────────────────────────────────────────────────────────
# RINEX FILE PATH HERE
obs_path = "/AUCK00NZL_R_20260010000_01D_30S_MO.rnx"  # ← change this path
# Read the file header first (fast — no data loaded yet)
print("📋 FILE HEADER")
print("=" * 60)
header = gr.rinexheader(obs_path)

for key, value in header.items():
    print(f"{key:<25}: {value}")

print()

# Load all observation data (interval=30 means keep 30-sec rate)

print("⏳ Loading observation data (this may take 1–2 minutes)...")
obs = gr.load(obs_path, interval=30)
print()
print("✅ Data loaded!")
print(obs)

# ─────────────────────────────────────────────────
# Step 3 — Build the Full Dataset per Constellation
# ─────────────────────────────────────────────────
# SNR and pseudorange codes to try per constellation
SNR_CODES = {
    'G': ['S1C', 'S2W'],
    'R': ['S1C', 'S1P'],
    'E': ['S1X', 'S5X'],
    'C': ['S1X', 'S2I'],
    'J': ['S1C', 'S1X'],
    'S': ['S1C'],
}
PR_CODES = {
    'G': ['C1C', 'C2W'],
    'R': ['C1C', 'C1P'],
    'E': ['C1X', 'C5X'],
    'C': ['C1X', 'C2I'],
    'J': ['C1C', 'C1X'],
    'S': ['C1C'],
}

all_sv = obs.sv.values

# Collect all observations per constellation

data = {}   # prefix → {'snr': array, 'pr': array, 'n_sats': int, 'n_obs': int}

print("📡 Collecting observations per constellation...")
print()
print(f"{'System':<10} {'Satellites':>10} {'SNR obs':>12} {'PR obs':>12} {'Mean SNR':>12} {'PR range':>22}")
print("-" * 80)

for prefix in ['G', 'R', 'E', 'C', 'J', 'S']:
    sats = [s for s in all_sv if s.startswith(prefix)]
    if not sats:
        continue

    snr_all = []
    pr_all  = []

    # Try each SNR code
    for code in SNR_CODES.get(prefix, ['S1C']):
        if code not in obs.data_vars:
            continue
        for sat in sats:
            vals = obs[code].sel(sv=sat).to_series().dropna().values
            snr_all.extend(vals)
        if snr_all:
            break   # use first code that has data

    # Try each pseudorange code
    for code in PR_CODES.get(prefix, ['C1C']):
        if code not in obs.data_vars:
            continue
        for sat in sats:
            vals = obs[code].sel(sv=sat).to_series().dropna().values
            pr_all.extend(vals)
        if pr_all:
            break

    snr_arr = np.array(snr_all)
    pr_arr  = np.array(pr_all)

    data[prefix] = {
        'snr':    snr_arr,
        'pr':     pr_arr,
        'n_sats': len(sats),
        'n_obs':  len(snr_arr),
        'name':   CONST_NAMES.get(prefix, prefix),
        'color':  CONST_COLORS.get(prefix, '#FFFFFF'),
    }

    pr_str = f"{pr_arr.min()/1e6:.1f}–{pr_arr.max()/1e6:.1f} Mm" if len(pr_arr) > 0 else "N/A"
    snr_mean = f"{snr_arr.mean():.1f} dB-Hz" if len(snr_arr) > 0 else "N/A"
    print(f"  {CONST_NAMES.get(prefix, prefix):<8} {len(sats):>10} {len(snr_arr):>12} {len(pr_arr):>12} {snr_mean:>14} {pr_str:>22}")

print()
total_obs = sum(d['n_obs'] for d in data.values())
print(f"✅ Total SNR observations across all systems: {total_obs:,}")

# ──────────────────────────────────────────────
# Step 4 — Plot 1: Observation Share — Pie Chart
# ──────────────────────────────────────────────
# Data for pie chart

labels  = [d['name']  for d in data.values() if d['n_obs'] > 0]
sizes   = [d['n_obs'] for d in data.values() if d['n_obs'] > 0]
colors  = [d['color'] for d in data.values() if d['n_obs'] > 0]
n_sats  = [d['n_sats'] for d in data.values() if d['n_obs'] > 0]

# Explode the largest slice slightly for emphasis
max_idx = sizes.index(max(sizes))
explode = [0.05 if i == max_idx else 0 for i in range(len(sizes))]

# Figure

fig, (ax_pie, ax_bar) = plt.subplots(1, 2, figsize=(16, 7), facecolor="#0d1117")
fig.suptitle(
    'Constellation Observation Summary | AUCK00NZL | 2026-01-01\n'
    'Share of SNR observations tracked per GNSS system over 24 hours',
    fontsize=13, fontweight='bold', color="#ffffff"
)

for ax in [ax_pie, ax_bar]:
    ax.set_facecolor("#0d1117")

# ─── Pie chart ──────────────────────────────────────────
wedges, texts, autotexts = ax_pie.pie(
    sizes,
    labels=None,
    colors=colors,
    explode=explode,
    autopct='%1.1f%%',
    startangle=140,
    pctdistance=0.75,
    wedgeprops=dict(linewidth=1.5, edgecolor='#0d1117')
)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(10)
    autotext.set_fontweight('bold')

# Custom legend with observation counts
legend_labels = [
    f"{name}   {count:,} obs  ({n} sats)"
    for name, count, n in zip(labels, sizes, n_sats)
]
legend_patches = [
    mpatches.Patch(color=c, label=l)
    for c, l in zip(colors, legend_labels)
]
ax_pie.legend(
    handles=legend_patches,
    loc='lower center',
    bbox_to_anchor=(0.5, -0.18),
    fontsize=9,
    framealpha=0.2,
    facecolor='#1a1a2e',
    edgecolor='#444444',
    labelcolor='white'
)
ax_pie.set_title('Share of tracked observations per system', color='white', fontsize=11)

# ─── Horizontal bar chart (satellites per system) ────────
bar_colors = colors[::-1]
bars = ax_bar.barh(
    labels[::-1], n_sats[::-1],
    color=bar_colors, edgecolor='#0d1117', linewidth=1.2
)

# Add value labels
for bar, val in zip(bars, n_sats[::-1]):
    ax_bar.text(
        bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
        f'{val} satellites',
        va='center', color='#e0e0e0', fontsize=10
    )

ax_bar.set_xlabel('Number of Satellites Tracked', color='#aaaaaa', fontsize=11)
ax_bar.set_title('Satellites tracked per constellation', color='white', fontsize=11)
ax_bar.tick_params(colors='#aaaaaa')
ax_bar.set_facecolor('#111827')
ax_bar.grid(True, axis='x', color='#222222', linewidth=0.5)
ax_bar.set_xlim(0, max(n_sats) + 5)

for t in ax_bar.get_yticklabels():
    t.set_color('white')
for spine in ax_bar.spines.values():
    spine.set_edgecolor('#333333')

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('plot1_constellation_pie.png', dpi=150,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.show()

print('✅ Plot saved: plot1_constellation_pie.png')
print()
print('💡 Interpretation:')
for name, count, n in zip(labels, sizes, n_sats):
    print(f'   • {name:<8}: {count:>8,} obs from {n} sats  ({count/total_obs*100:.1f}%)')

# ────────────────────────────────────────────────────────
# Step 5 — Plot 2: SNR Distribution — Histogram + Box Plot
# ────────────────────────────────────────────────────────
# Figure: 2 panels — histogram (left) + box plot (right)

fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor="#0d1117")
fig.suptitle(
    'SNR Distribution per Constellation | AUCK00NZL | 2026-01-01\n'
    'All epochs · All satellites · L1 signal',
    fontsize=13, fontweight='bold', color="#ffffff"
)

for ax in axes:
    ax.set_facecolor("#111827")
    ax.tick_params(colors="#aaaaaa")
    ax.grid(True, color="#222222", linewidth=0.5)
    for spine in ax.spines.values():
        spine.set_edgecolor("#333333")

# ─── Left: Overlapping histograms ───────────────────────
bins = np.linspace(10, 60, 60)

for prefix, d in data.items():
    if len(d['snr']) == 0:
        continue
    axes[0].hist(
        d['snr'],
        bins=bins,
        color=d['color'],
        alpha=0.55,
        label=f"{d['name']}  (μ={d['snr'].mean():.1f} dB-Hz)",
        edgecolor='none',
        density=True   # normalise to compare systems with different observation counts
    )

# Quality reference lines
axes[0].axvline(25, color='#F44336', ls='--', lw=1.2, alpha=0.8, label='Poor threshold (25 dB-Hz)')
axes[0].axvline(35, color='#4CAF50', ls='--', lw=1.2, alpha=0.8, label='Good threshold (35 dB-Hz)')
axes[0].axvline(40, color='#FFEB3B', ls='--', lw=1.0, alpha=0.7, label='Excellent threshold (40 dB-Hz)')

axes[0].set_xlabel('SNR [dB-Hz]', color='#aaaaaa', fontsize=11)
axes[0].set_ylabel('Probability density', color='#aaaaaa', fontsize=11)
axes[0].set_title('SNR histogram — normalised density', color='white', fontsize=11)

legend0 = axes[0].legend(fontsize=8, framealpha=0.3, facecolor='#1a1a2e', edgecolor='#444444')
for t in legend0.get_texts():
    t.set_color('white')

# ─── Right: Box plot ────────────────────────────────────
box_data   = [d['snr'] for d in data.values() if len(d['snr']) > 0]
box_labels = [d['name'] for d in data.values() if len(d['snr']) > 0]
box_colors = [d['color'] for d in data.values() if len(d['snr']) > 0]

bp = axes[1].boxplot(
    box_data,
    vert=True,
    patch_artist=True,
    notch=False,
    showfliers=True,
    whis=[5, 95],   # whiskers = 5th to 95th percentile
    medianprops=dict(color='white', linewidth=2),
    whiskerprops=dict(linewidth=1.2),
    capprops=dict(linewidth=1.5),
    flierprops=dict(marker='o', markersize=2, alpha=0.4)
)

# Colour each box by constellation
for patch, color, fp in zip(bp['boxes'], box_colors, bp['fliers']):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
    fp.set_markerfacecolor(color)
    fp.set_markeredgecolor(color)

for element in ['whiskers', 'caps']:
    for line, color in zip(
        [bp[element][i] for i in range(len(bp[element]))],
        [c for c in box_colors for _ in range(2)]
    ):
        line.set_color(color)

# Quality threshold lines
axes[1].axhline(25, color='#F44336', ls='--', lw=1.0, alpha=0.7)
axes[1].axhline(35, color='#4CAF50', ls='--', lw=1.0, alpha=0.7)
axes[1].axhline(40, color='#FFEB3B', ls='--', lw=0.8, alpha=0.6)

axes[1].set_xticklabels(box_labels, color='white', fontsize=11)
axes[1].set_ylabel('SNR [dB-Hz]', color='#aaaaaa', fontsize=11)
axes[1].set_title(
    'SNR box plot — median · IQR · 5–95th pctile · outliers',
    color='white', fontsize=11
)
axes[1].set_ylim(10, 65)

# Add median value labels
for i, d in enumerate([d for d in data.values() if len(d['snr']) > 0]):
    median = np.median(d['snr'])
    axes[1].text(
        i + 1, median + 1.5, f'{median:.1f}',
        ha='center', fontsize=8, color='white', fontweight='bold'
    )

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('plot2_snr_distribution.png', dpi=150,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.show()

print('✅ Plot saved: plot2_snr_distribution.png')
print()
print('📊 SNR Summary per constellation:')
print(f"{'System':<10} {'Median':>8} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
print("-" * 55)
for prefix, d in data.items():
    if len(d['snr']) == 0:
        continue
    print(f"  {d['name']:<8} {np.median(d['snr']):>7.1f}  {d['snr'].mean():>7.1f}  "
          f"{d['snr'].std():>7.1f}  {d['snr'].min():>7.1f}  {d['snr'].max():>7.1f}  dB-Hz")

# ───────────────────────────────────────────────────────────────────────
# Step 6 — Plot 3: Pseudorange Distribution — Histogram per Constellation
# ───────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 6), facecolor="#0d1117")
ax.set_facecolor("#111827")

ax.set_title(
    'Pseudorange Distribution per Constellation | AUCK00NZL | 2026-01-01\n'
    'Each system occupies a different range band — reflecting orbital altitude',
    fontsize=13, fontweight='bold', color="#ffffff"
)

# Determine global bin range
all_pr = np.concatenate([d['pr'] for d in data.values() if len(d['pr']) > 0])
pr_min = np.percentile(all_pr, 0.5)   # ignore extreme outliers
pr_max = np.percentile(all_pr, 99.5)
bins = np.linspace(pr_min, pr_max, 80)

for prefix, d in data.items():
    if len(d['pr']) == 0:
        continue
    ax.hist(
        d['pr'] / 1e6,    # convert to million metres
        bins=bins / 1e6,
        color=d['color'],
        alpha=0.55,
        label=f"{d['name']}  (μ={d['pr'].mean()/1e6:.2f} Mm)",
        edgecolor='none',
        density=True
    )
    # Mark the mean with a vertical line
    ax.axvline(
        d['pr'].mean() / 1e6,
        color=d['color'], ls=':', lw=1.5, alpha=0.9
    )

ax.set_xlabel('Pseudorange [Mm = million metres]', color='#aaaaaa', fontsize=11)
ax.set_ylabel('Probability density', color='#aaaaaa', fontsize=11)

ax.tick_params(colors='#aaaaaa')
ax.grid(True, color='#222222', linewidth=0.5)
for spine in ax.spines.values():
    spine.set_edgecolor('#333333')

legend = ax.legend(fontsize=10, framealpha=0.3, facecolor='#1a1a2e', edgecolor='#444444')
for t in legend.get_texts():
    t.set_color('white')

plt.tight_layout()
plt.savefig('plot3_pseudorange_distribution.png', dpi=150,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.show()

print('✅ Plot saved: plot3_pseudorange_distribution.png')
print()
print('📊 Pseudorange summary per constellation:')
print(f"{'System':<10} {'Mean [Mm]':>10} {'Std [Mm]':>10} {'Min [Mm]':>10} {'Max [Mm]':>10}")
print("-" * 55)
for prefix, d in data.items():
    if len(d['pr']) == 0:
        continue
    pr = d['pr'] / 1e6
    print(f"  {d['name']:<8} {pr.mean():>10.3f} {pr.std():>10.3f} {pr.min():>10.3f} {pr.max():>10.3f}")

# ────────────────────────────────────────────────────
# Step 7 — Plot 4: Plot 4: Full Multi-GNSS SNR Heatmap
# ────────────────────────────────────────────────────
# Collect ordered list of all satellites by constellation

ordered_sats = []
sat_colors_list = []

for prefix in ['G', 'E', 'R', 'C', 'J', 'S']:
    sats = sorted([s for s in all_sv if s.startswith(prefix)])
    for sat in sats:
        ordered_sats.append(sat)
        sat_colors_list.append(CONST_COLORS.get(prefix, '#FFFFFF'))

# Determine best SNR code per constellation
SNR_BEST = {}
for prefix in ['G', 'R', 'E', 'C', 'J', 'S']:
    for code in SNR_CODES.get(prefix, ['S1C']):
        if code in obs.data_vars:
            # Quick check: does it have any data at all?
            sats = [s for s in all_sv if s.startswith(prefix)]
            if sats:
                n = obs[code].sel(sv=sats[0]).to_series().notna().sum()
                if n > 0:
                    SNR_BEST[prefix] = code
                    break

# Build SNR matrix: rows = satellites, columns = time

time_index = pd.to_datetime(obs.time.values)
n_epochs   = len(time_index)
n_rows     = len(ordered_sats)

snr_matrix = np.full((n_rows, n_epochs), np.nan)

for i, sat in enumerate(ordered_sats):
    prefix = sat[0]
    code   = SNR_BEST.get(prefix)
    if code is None or code not in obs.data_vars:
        continue
    try:
        series = obs[code].sel(sv=sat).to_series().reindex(time_index)
        snr_matrix[i, :] = series.values
    except Exception:
        pass

# Replace NaN with sentinel (below vmin) for rendering
snr_display = np.where(np.isnan(snr_matrix), 5, snr_matrix)

# Custom GNSS colormap

gnss_cmap = LinearSegmentedColormap.from_list(
    "gnss_snr",
    ["#0d1117", "#1a0533", "#2c3e8c", "#0099cc", "#00e676", "#ffeb3b", "#ff6f00"],
    N=256
)

# Figure — tall heatmap, one row per satellite

row_height = 0.28   # inches per satellite row
fig_height = max(8, n_rows * row_height + 2)

fig, ax = plt.subplots(figsize=(16, fig_height), facecolor="#0d1117")
ax.set_facecolor("#0d1117")

# imshow — reliable for any matrix size
ax.imshow(
    snr_display,
    aspect='auto',
    cmap=gnss_cmap,
    vmin=15, vmax=55,
    extent=[
        mdates.date2num(time_index[0]),
        mdates.date2num(time_index[-1]),
        -0.5,
        n_rows - 0.5
    ],
    origin='upper'
)

ax.xaxis_date()

# Colorbar
sm = plt.cm.ScalarMappable(cmap=gnss_cmap, norm=plt.Normalize(vmin=15, vmax=55))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, pad=0.01)
cbar.set_label('SNR [dB-Hz]', color='#e0e0e0', fontsize=11)
cbar.ax.yaxis.set_tick_params(color='#aaaaaa')
plt.setp(cbar.ax.get_yticklabels(), color='#aaaaaa')

# Y axis — satellite labels, coloured by constellation
ax.set_yticks(range(n_rows))
ax.set_yticklabels(ordered_sats, fontsize=7)
for tick_label, color in zip(ax.get_yticklabels(), sat_colors_list):
    tick_label.set_color(color)

# Draw horizontal separators between constellations
current_prefix = None
for i, sat in enumerate(ordered_sats):
    prefix = sat[0]
    if current_prefix is not None and prefix != current_prefix:
        ax.axhline(i - 0.5, color='#555555', lw=1.5, linestyle='--')
        # Constellation label on the right
        ax.text(
            1.002, (i - 0.5) / n_rows - 0.5 / n_rows * 2,
            CONST_NAMES.get(current_prefix, current_prefix),
            transform=ax.transAxes,
            color=CONST_COLORS.get(current_prefix, 'white'),
            fontsize=8, va='center', fontweight='bold'
        )
    current_prefix = prefix

ax.set_title(
    f'Full Multi-GNSS SNR Heatmap — {n_rows} Satellites | AUCK00NZL | 2026-01-01\n'
    'Green/Yellow = strong signal  |  Blue/Purple = weak  |  Black = not visible',
    fontsize=12, fontweight='bold', color='#ffffff'
)
ax.set_xlabel('UTC Time (HH:MM)', fontsize=11, color='#e0e0e0')

ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
plt.xticks(rotation=30, color='#aaaaaa')

for spine in ax.spines.values():
    spine.set_edgecolor('#333333')

plt.tight_layout()
plt.savefig('plot4_full_gnss_heatmap.png', dpi=150,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.show()

print(f'✅ Plot saved: plot4_full_gnss_heatmap.png')
print(f'   Total satellites shown: {n_rows}')
print()
print('💡 Interpretation:')
print('   • Each ROW = one satellite, grouped by constellation (separated by dashed lines)')
print('   • GPS rows are blue, GLONASS red, Galileo green, BeiDou orange, QZSS purple')
print('   • Black = satellite below horizon')
print('   • Bright rows = satellites tracked all day (high elevation or GEO)')

