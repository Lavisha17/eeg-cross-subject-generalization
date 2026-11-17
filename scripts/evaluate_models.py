
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import (
    train_test_split,
    StratifiedGroupKFold,
    GridSearchCV
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# 1. Load the extracted EEG features
df = pd.read_csv("results/features.csv")

metadata = ["subject", "condition", "label", "window"]
all_features = [c for c in df.columns if c not in metadata]

# 2. Recreate the same participant-independent split
subjects = sorted(df["subject"].unique())

train_subjects, test_subjects = train_test_split(
    subjects,
    test_size=10,
    random_state=42
)

train_df = df[df["subject"].isin(train_subjects)].copy()
test_df = df[df["subject"].isin(test_subjects)].copy()

y_train = train_df["label"]
y_test = test_df["label"]

# 3. Define the 8 targeted features
targeted_features = [
    "AF3_theta", "AF4_theta", "F3_theta", "F4_theta",
    "P7_alpha", "P8_alpha", "O1_alpha", "O2_alpha"
]

# 4. Grouped cross-validation:
# All windows from one participant stay in the same fold.
cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

# Store participant-wise evaluation results
participant_results = []

# 5. Define the model and hyperparameter search
def evaluate_model(feature_columns, model_name):

    X_train = train_df[feature_columns]
    X_test = test_df[feature_columns]

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42
        ))
    ])

    search = GridSearchCV(
        estimator=pipeline,
        param_grid={
            "classifier__C": [0.01, 0.1, 1, 10]
        },
        scoring="balanced_accuracy",
        cv=cv,
        n_jobs=-1
    )

    # Only training participants are used for model selection.
    search.fit(
        X_train,
        y_train,
        groups=train_df["subject"]
    )

    # Evaluate the selected model on unseen participants.
    predictions = search.predict(X_test)
    probabilities = search.predict_proba(X_test)[:, 1]

    if model_name == "Full 56 features":
        from sklearn.metrics import confusion_matrix, classification_report

        cm = confusion_matrix(y_test, predictions)

        print("\nCONFUSION MATRIX")
        print("Rows = Actual, Columns = Predicted")
        print("Labels: 0 = Resting, 1 = Multitasking")
        print(cm)

        print("\nCLASSIFICATION REPORT")
        print(classification_report(
            y_test,
            predictions,
            target_names=["Resting", "Multitasking"],
            digits=3
        ))

        print("\nPer-participant test balanced accuracy:")

    for subject in sorted(test_df["subject"].unique()):
        mask = (test_df["subject"] == subject).to_numpy()

        score = balanced_accuracy_score(
            y_test.to_numpy()[mask],
            predictions[mask]
        )

        participant_results.append({
            "Model": model_name,
            "Participant": subject,
            "Balanced Accuracy": score
        })

        print(f"Participant {subject:02d}: {score:.3f}")

    results = {
        "Model": model_name,
        "Features": len(feature_columns),
        "Best C": search.best_params_["classifier__C"],
        "CV Balanced Accuracy": search.best_score_,
        "Test Balanced Accuracy": balanced_accuracy_score(
            y_test, predictions
        ),
        "Test Macro F1": f1_score(
            y_test, predictions, average="macro"
        ),
        "Test ROC-AUC": roc_auc_score(
            y_test, probabilities
        )
    }

    print("\n", "=" * 50)
    print(model_name)
    print("=" * 50)

    for key, value in results.items():
        print(f"{key}: {value}")

    return results


# 6. Majority-class baseline
dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(
    np.zeros((len(train_df), 1)),
    y_train
)

dummy_predictions = dummy.predict(
    np.zeros((len(test_df), 1))
)

results = [{
    "Model": "Majority baseline",
    "Features": 0,
    "Best C": "N/A",
    "CV Balanced Accuracy": "N/A",
    "Test Balanced Accuracy": balanced_accuracy_score(
        y_test, dummy_predictions
    ),
    "Test Macro F1": f1_score(
        y_test, dummy_predictions, average="macro"
    ),
    "Test ROC-AUC": "N/A"
}]

# 7. Evaluate both EEG feature sets
results.append(
    evaluate_model(all_features, "Full 56 features")
)

results.append(
    evaluate_model(targeted_features, "Targeted 8 features")
)

# 8. Save the results
results_df = pd.DataFrame(results)

Path("results").mkdir(exist_ok=True)
results_df.to_csv("results/model_results.csv", index=False)

print("\n\nFINAL RESULTS")
print(results_df.to_string(index=False))
print("\nSaved to results/model_results.csv")

# Save participant-wise results
participant_df = pd.DataFrame(participant_results)

participant_df.to_csv(
    "results/participant_results.csv",
    index=False
)

print("\nSaved to results/participant_results.csv")

