
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.colors import LinearSegmentedColormap


# ==========================================
# 1. OUTPUT FOLDER
# ==========================================

Path("figures").mkdir(exist_ok=True)


# ==========================================
# 2. ACADEMIC PLOT SETTINGS
# ==========================================

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.titleweight": "semibold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white"
})


# ==========================================
# 3. COLOUR PALETTE
# ==========================================

FULL_COLOR = "#245B70"       # Deep teal
TARGETED_COLOR = "#D88763"   # Muted terracotta
REFERENCE_COLOR = "#59636B"  # Slate grey
GRID_COLOR = "#E8EFF2"        # Pale blue-grey

teal_cmap = LinearSegmentedColormap.from_list(
    "academic_teal",
    ["#E8EFF2", "#76A6AD", "#245B70"]
)



# ==========================================
# FIGURE 1: CONFUSION MATRIX
# ==========================================

cm = np.array([
    [303, 67],
    [53, 317]
])

fig, ax = plt.subplots(figsize=(7, 5.5))

# Draw confusion matrix directly using Matplotlib
im = ax.imshow(cm, cmap=teal_cmap)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Number of windows", rotation=90, labelpad=12)

labels = ["Resting", "Multitasking"]

ax.set_xticks([0, 1])
ax.set_yticks([0, 1])

ax.set_xticklabels(labels)
ax.set_yticklabels(labels)

# Add values inside each cell
for i in range(2):
    for j in range(2):
        value = cm[i, j]

        text_color = "white" if value > cm.max() / 2 else "#243746"

        ax.text(
            j, i, str(value),
            ha="center",
            va="center",
            fontsize=18,
            color=text_color
        )

ax.set_xlabel("Predicted condition")
ax.set_ylabel("Actual condition")

ax.set_title(
    "Confusion Matrix: Full 56-Feature Model",
    pad=15
)

fig.tight_layout()

fig.savefig(
    "figures/figure1_confusion_matrix.png",
    bbox_inches="tight"
)

plt.close(fig)


# ==========================================
# FIGURE 2: PARTICIPANT-WISE ACCURACY
# ==========================================

participants = [
    "05", "13", "20", "25", "26",
    "27", "28", "38", "41", "44"
]

full_scores = [
    0.824, 0.973, 0.946, 0.635, 0.824,
    0.946, 0.622, 0.838, 0.986, 0.784
]

targeted_scores = [
    0.541, 0.946, 0.378, 0.568, 0.378,
    0.784, 0.527, 0.514, 0.284, 0.770
]

x = np.arange(len(participants))
width = 0.36

fig, ax = plt.subplots(figsize=(10, 5.5))

ax.bar(
    x - width / 2,
    np.array(full_scores) * 100,
    width,
    label="Full 56 features",
    color=FULL_COLOR
)

ax.bar(
    x + width / 2,
    np.array(targeted_scores) * 100,
    width,
    label="Targeted 8 features",
    color=TARGETED_COLOR
)

ax.axhline(
    50,
    linestyle="--",
    linewidth=1.4,
    color=REFERENCE_COLOR,
    label="Chance reference"
)

ax.set_xticks(x)
ax.set_xticklabels(participants)

ax.set_xlabel("Held-out participant")
ax.set_ylabel("Balanced accuracy (%)")

ax.set_title(
    "Generalisation Across Unseen Participants",
    pad=28
)

ax.set_ylim(0, 105)

ax.legend(
    frameon=False,
    ncol=2,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.20)
)

ax.grid(
    axis="y",
    color=GRID_COLOR,
    linewidth=1
)

ax.set_axisbelow(True)

fig.tight_layout()
fig.subplots_adjust(bottom=0.25)
fig.canvas.draw()
renderer = fig.canvas.get_renderer()

print("\nFIGURE 2 LAYOUT CHECK")
print("Title:", ax.title.get_window_extent(renderer).bounds)
print("Legend:", ax.get_legend().get_window_extent(renderer).bounds)
print("Plot:", ax.get_window_extent(renderer).bounds)

fig.savefig(
    "figures/figure2_participant_accuracy.png",
    bbox_inches="tight"
)

plt.close(fig)


# ==========================================
# FIGURE 3: MODEL PERFORMANCE COMPARISON
# ==========================================

results = pd.read_csv("results/model_results.csv")

model_results = results[
    results["Model"].isin([
        "Full 56 features",
        "Targeted 8 features"
    ])
]

# Keep the intended model order
model_results = (
    model_results
    .set_index("Model")
    .loc[["Full 56 features", "Targeted 8 features"]]
    .reset_index()
)

metrics = [
    "CV Balanced Accuracy",
    "Test Balanced Accuracy",
    "Test Macro F1",
    "Test ROC-AUC"
]

labels = [
    "CV balanced\naccuracy",
    "Test balanced\naccuracy",
    "Test macro F1",
    "Test ROC-AUC"
]

x = np.arange(len(metrics))
width = 0.36

fig, ax = plt.subplots(figsize=(10, 5.5))

colors = [FULL_COLOR, TARGETED_COLOR]

for i, (_, row) in enumerate(model_results.iterrows()):

    values = [
        row[metric] * 100
        for metric in metrics
    ]

    ax.bar(
        x + (i - 0.5) * width,
        values,
        width,
        label=row["Model"],
        color=colors[i]
    )

ax.set_xticks(x)
ax.set_xticklabels(labels)

ax.set_ylabel("Score (%)")

ax.set_title(
    "EEG Feature Comparison: Cross-Validation vs Test Performance",
    pad=15
)

ax.set_ylim(0, 105)

ax.legend(
    frameon=False,
    ncol=2,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.18)
)


ax.grid(
    axis="y",
    color=GRID_COLOR,
    linewidth=1
)

ax.set_axisbelow(True)

fig.tight_layout()
fig.subplots_adjust(bottom=0.25)

fig.canvas.draw()
renderer = fig.canvas.get_renderer()

print("\nFIGURE 3 LAYOUT CHECK")
print("Title:", ax.title.get_window_extent(renderer).bounds)
print("Legend:", ax.get_legend().get_window_extent(renderer).bounds)
print("Plot:", ax.get_window_extent(renderer).bounds)

fig.savefig(
    "figures/figure3_model_comparison.png",
    bbox_inches="tight"
)

plt.close(fig)


# ==========================================
# 4. COMPLETION MESSAGE
# ==========================================

print("\nFIGURES GENERATED SUCCESSFULLY\n")

for file in sorted(Path("figures").glob("*.png")):
    print(file)

print("\nAll figures saved at 300 DPI.")
