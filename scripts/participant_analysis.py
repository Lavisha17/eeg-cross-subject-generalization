
import numpy as np
import pandas as pd

# 1. Load actual participant-level results
df = pd.read_csv("results/participant_results.csv")


# 2. Bootstrap confidence interval
def bootstrap_ci(scores, repetitions=10000, seed=42):
    rng = np.random.default_rng(seed)

    bootstrap_means = []

    for _ in range(repetitions):
        sample = rng.choice(
            scores,
            size=len(scores),
            replace=True
        )
        bootstrap_means.append(sample.mean())

    lower = np.percentile(bootstrap_means, 2.5)
    upper = np.percentile(bootstrap_means, 97.5)

    return lower, upper


# 3. Calculate statistics for each model
summary = []

for model_name, group in df.groupby("Model", sort=False):

    scores = group["Balanced Accuracy"].to_numpy()

    lower, upper = bootstrap_ci(scores)

    summary.append({
        "Model": model_name,
        "Participants": len(scores),
        "Mean Balanced Accuracy": scores.mean(),
        "Standard Deviation": scores.std(ddof=1),
        "CI Lower": lower,
        "CI Upper": upper
    })

    print("\n", model_name)
    print(f"Participants: {len(scores)}")
    print(f"Mean accuracy: {scores.mean():.4f}")
    print(f"Standard deviation: {scores.std(ddof=1):.4f}")
    print(f"95% bootstrap CI: [{lower:.4f}, {upper:.4f}]")


# 4. Paired comparison across the same participants
pivot = df.pivot(
    index="Participant",
    columns="Model",
    values="Balanced Accuracy"
)

differences = (
    pivot["Full 56 features"] -
    pivot["Targeted 8 features"]
).to_numpy()

lower, upper = bootstrap_ci(differences)

summary.append({
    "Model": "Paired difference (Full - Targeted)",
    "Participants": len(differences),
    "Mean Balanced Accuracy": differences.mean(),
    "Standard Deviation": differences.std(ddof=1),
    "CI Lower": lower,
    "CI Upper": upper
})

print("\nPaired model comparison")
print(f"Mean difference: {differences.mean():.4f}")
print(f"95% bootstrap CI: [{lower:.4f}, {upper:.4f}]")


# 5. Save summary
summary_df = pd.DataFrame(summary)

summary_df.to_csv(
    "results/participant_summary.csv",
    index=False
)

print("\nSaved to results/participant_summary.csv")
