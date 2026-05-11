# 📊 Project 5 — Constellation Summary: Pie Chart & Histograms

> **Observation Share · SNR Distribution · Pseudorange Bands · Full GNSS Heatmap | Auckland, NZ**

---

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

---

## 🖼️ Output Plots

### Plot 1 — Constellation Observation Share

Side-by-side:
- **Pie chart**: percentage of total SNR observations per system
- **Bar chart**: number of satellites tracked per constellation

### Plot 2 — SNR Distribution

Side-by-side:
- **Histogram**: overlapping normalised density curves per constellation, with quality thresholds at 25 / 35 / 40 dB-Hz
- **Box plot**: median, IQR, 5–95th percentile whiskers, outlier dots — median labelled per system

### Plot 3 — Pseudorange Distribution

Overlapping histograms showing the range measurement spread for each constellation:
- GLONASS (19,100 km) → shifted left
- GPS (~20,200 km) → centre
- Galileo (~23,222 km) → shifted right
- BeiDou GEO (36,000 km) → far right if tracked

### Plot 4 — Full Multi-GNSS SNR Heatmap

Every satellite from every constellation, one row each, separated by dashed constellation
boundaries with colour-coded labels. The most complete picture of tracking coverage
in the file.

---

## 📂 File Structure

```
project5-constellation-summary/
├── Outputs/
│   ├── plot1_constellation_pie.png
│   ├── plot2_snr_distribution.png
│   ├── plot3_pseudorange_distribution.png
│   └── plot4_full_gnss_heatmap.png
├── src/
│   ├── project5_constellation_summary__pie_chart_&_histograms.py        ← Main python
├── requirements.txt                                                    ← Python dependencies
├── LICENSE                                                             ← MIT License
└── README.md                                                           ← This file
```

---

## ⚙️ How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your RINEX file path

Update **Step 2** of the notebook:

```python
obs_path = "/path/to/your/file.rnx"
```

### 3. Run all cells

```bash
jupyter notebook project5_constellation_summary.ipynb
```

No configuration needed. The notebook auto-detects all constellations and observable
codes present in your file.

---

## 🛠️ Dependencies

| Package | Purpose |
|---------|---------|
| `georinex` | Parse RINEX 3 observation files |
| `xarray` | N-dimensional labelled arrays |
| `pandas` | Time series manipulation |
| `numpy` | Numerical computations and statistics |
| `matplotlib` | Publication-quality plotting |

---

## 🧭 Observables Used

The notebook auto-detects the best available code per constellation:

| Constellation | SNR tried | Pseudorange tried |
|--------------|-----------|-------------------|
| GPS (G) | S1C, S2W | C1C, C2W |
| GLONASS (R) | S1C, S1P | C1C, C1P |
| Galileo (E) | S1X, S5X | C1X, C5X |
| BeiDou (C) | S1X, S2I | C1X, C2I |
| QZSS (J) | S1C, S1X | C1C, C1X |

---

## 💡 Technical Note — SNR Heatmap

All heatmaps in this project use `imshow` with `extent=` and `ax.xaxis_date()`,
avoiding the `pcolormesh` blank-plot issue documented in Project 1.

---

## 👤 Author

**Hakim El Azzouzi**  
MSc Global Navigation Satellite Systems  
Mohammed First University, Oujda, Morocco  
📧 elazzouzihakim10@gmail.com  
🔗 [linkedin.com/in/Hakim-El-Azzouzi](https://linkedin.com/in/Hakim-El-Azzouzi)  
📍 Luxembourg 🇱🇺

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🔗 Part of the GNSS RINEX Analysis Series

| # | Project |
|---|---------|
| 1 | Single GPS Satellite — Pseudorange & SNR Heatmap |
| 2 | All GPS Satellites — Fleet Pseudorange & SNR Heatmap |
| 3 | Multi-Constellation GNSS — One Satellite per System |
| 4 | Pseudorange vs Carrier-Phase Comparison |
| **5** | **Constellation Summary — Pie Chart & Histograms** ← You are here |
| 6 | Ionospheric Delay — Geometry-Free Combination |
| 7 | Data Quality Report |
