from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import welch

DATA_DIR = Path(r"C:\Users\lavis\Downloads\STEW\STEW")
OUTPUT_FILE = Path("results/features.csv")

CHANNELS = [
    "AF3", "F7", "F3", "FC5", "T7", "P7", "O1",
    "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"
]

BANDS = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
}

FS = 128
WINDOW_SECONDS = 4
WINDOW_SAMPLES = FS * WINDOW_SECONDS


def extract_window_features(window):
    # Remove the mean independently from each channel.
    window = window - window.mean(axis=0, keepdims=True)

    frequencies, psd = welch(
        window,
        fs=FS,
        nperseg=WINDOW_SAMPLES,
        detrend=False,
	axis=0
    )

    features = {}

    for channel_index, channel in enumerate(CHANNELS):
        for band_name, (low, high) in BANDS.items():
            mask = (frequencies >= low) & (frequencies < high)
            power = np.trapezoid(psd[mask, channel_index], frequencies[mask])
            features[f"{channel}_{band_name}"] = np.log10(max(power, 1e-20))

    return features


def main():
    rows = []

    for subject in range(1, 49):
        for condition in ["lo", "hi"]:
            filepath = DATA_DIR / f"sub{subject:02d}_{condition}.txt"
            eeg = np.loadtxt(filepath)

            label = 0 if condition == "lo" else 1

            for window_index, start in enumerate(
                range(0, len(eeg) - WINDOW_SAMPLES + 1, WINDOW_SAMPLES)
            ):
                window = eeg[start:start + WINDOW_SAMPLES]

                row = extract_window_features(window)
                row["subject"] = subject
                row["condition"] = condition
                row["label"] = label
                row["window"] = window_index

                rows.append(row)

    df = pd.DataFrame(rows)

    metadata = ["subject", "condition", "label", "window"]
    feature_columns = [c for c in df.columns if c not in metadata]
    df = df[metadata + feature_columns]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("FEATURE EXTRACTION COMPLETE")
    print("Dataset shape:", df.shape)
    print("Number of windows:", len(df))
    print("Number of EEG features:", len(feature_columns))
    print("Unique participants:", df["subject"].nunique())
    print("Windows per condition:")
    print(df["condition"].value_counts().to_string())
    print("Missing feature values:", df[feature_columns].isna().sum().sum())
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
