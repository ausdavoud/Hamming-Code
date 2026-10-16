"""Redraws docs/error-rate.png and docs/matrices.png from hamming.py.

    uv run docs/figures.py
"""
import random
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import hamming  # noqa: E402

OUT = ROOT / "docs"

# ---- decoded bit error rate of Hamming(2^r - 1, 2^r - 1 - r) over a binary symmetric channel
random.seed(2025)
ps = [float(p) for p in np.geomspace(0.002, 0.45, 28)]
d = {"p": ps, "series": {}, "shannon": {}}
for r in (3, 4, 5):
    d["series"][r] = [hamming.main(r=r, error_probability=p, data_length=200_000) for p in ps]
    d["shannon"][r] = float(hamming.solve_for_p(r))
    print(f"r = {r} done", flush=True)

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
SERIES = {3: "#2a78d6", 4: "#eb6834", 5: "#1baf7a"}
MARKER = {3: "o", 4: "s", 5: "D"}
NAME = {3: "(7, 4)", 4: "(15, 11)", 5: "(31, 26)"}

for f in ["/System/Library/Fonts/HelveticaNeue.ttc"]:
    if Path(f).exists():
        font_manager.fontManager.addfont(f)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
        break
plt.rcParams.update({"axes.edgecolor": GRID, "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "font.size": 11.5})

# ---- error rate against flip probability
ps = d["p"]
fig = plt.figure(figsize=(11, 6.2), dpi=120, facecolor=SURFACE)
fig.text(0.06, 0.93, "What a Hamming code buys you", fontsize=19, color=INK, weight="bold")
fig.text(0.06, 0.885, "Bit error rate after decoding, 200,000 random bits per point. Dashed: each code's Shannon limit.",
         fontsize=12, color=INK2)
ax = fig.add_axes([0.08, 0.12, 0.78, 0.68])
ax.set_facecolor(SURFACE)
ax.set_xscale("log")
ax.set_yscale("log")
ax.grid(color=GRID, linewidth=0.8, which="major")
ax.set_axisbelow(True)
ax.tick_params(length=0)
ax.plot(ps, ps, color=MUTED, linewidth=1.6, linestyle=(0, (5, 4)))
ax.text(0.0075, 0.0075 * 1.45, "no code", color=INK2, fontsize=11, rotation=33, rotation_mode="anchor")
for r, ys in d["series"].items():
    r = int(r)
    pts = [(p, y) for p, y in zip(ps, ys) if y > 0]
    x, y = zip(*pts)
    ax.plot(x, y, color=SERIES[r], linewidth=2, marker=MARKER[r], markersize=6.5,
            markerfacecolor=SERIES[r], markeredgecolor=SURFACE, markeredgewidth=1.6, label=NAME[r], zorder=3)
    p_star = d["shannon"][r]
    ax.axvline(p_star, color=SERIES[r], linewidth=1.2, linestyle=(0, (2, 3)), alpha=0.9, zorder=1)
    ax.text(p_star, 0.85, f"p* {NAME[r]}", color=INK2, fontsize=10, ha="center", va="bottom")
ax.set_xlim(0.0018, 0.62)
ax.set_ylim(4e-6, 0.8)
ax.set_xlabel("probability p that the channel flips a bit")
ax.set_ylabel("bit error rate after decoding")
ax.legend(frameon=False, loc="upper left", labelcolor=INK, handlelength=2.2)
fig.savefig(OUT / "error-rate.png", facecolor=SURFACE)
plt.close(fig)

# ---- H and G for the (7, 4) code, exactly as hamming.py builds them
H = hamming.generate_H(3, move_I=True)
G = hamming.generate_G(H)
k, n, r = len(G), len(G[0]), len(H)
PART, IDENT = "#2a78d6", "#eb6834"


def draw(ax, M, title, ident_cols):
    rows, cols = len(M), len(M[0])
    ax.set_xlim(-0.6, cols + 0.1)
    ax.set_ylim(4.1, -1.4)
    ax.axis("off")
    ax.text(-0.1, -0.85, title, fontsize=15, color=INK, weight="bold", ha="left", va="center")
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            col = IDENT if j in ident_cols else PART
            ax.add_patch(FancyBboxPatch((j + 0.07, i + 0.07), 0.86, 0.86, boxstyle="round,pad=0,rounding_size=0.14",
                                        facecolor=col if v else SURFACE, edgecolor=col, linewidth=1.4,
                                        alpha=1 if v else 0.9))
            ax.text(j + 0.5, i + 0.52, str(v), ha="center", va="center", fontsize=13,
                    color="white" if v else INK2, weight="bold" if v else "normal")


fig = plt.figure(figsize=(11, 3.6), dpi=120, facecolor=SURFACE)
a1 = fig.add_axes([0.04, 0.05, 0.36, 0.9])
draw(a1, H, r"$H = [\,P \mid I_3\,]$", ident_cols=range(n - r, n))
a2 = fig.add_axes([0.47, 0.05, 0.36, 0.9])
draw(a2, G, r"$G = [\,I_4 \mid P^{T}\,]$", ident_cols=range(0, k))
fig.text(0.86, 0.62, "data bits first,", fontsize=11.5, color=INK2)
fig.text(0.86, 0.53, "parity bits last", fontsize=11.5, color=INK2)
fig.text(0.86, 0.38, r"$G\,H^{T} = 0$", fontsize=13, color=INK, weight="bold")
fig.savefig(OUT / "matrices.png", facecolor=SURFACE)
plt.close(fig)

# the identity the figure states
GH = hamming.multiply_matrices(G, hamming.transpose(H))
assert all(v == 0 for row in GH for v in row), "G · Hᵀ should vanish"
print("figures written; G·Hᵀ = 0 holds")
