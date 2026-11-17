from pathlib import Path
import argparse
import numpy as np


def main():
    parser = argparse.ArgumentParser(
        description="Validate the STEW EEG dataset."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/STEW"),
        help="Directory containing the STEW recordings."
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    total = 0
    problems = []

    if not data_dir.exists():
        raise SystemExit(f"Dataset directory not found: {data_dir}")

    for subject in range(1, 49):
        for condition in ["lo", "hi"]:
            filename = f"sub{subject:02d}_{condition}.txt"
            filepath = data_dir / filename

            if not filepath.exists():
                problems.append(f"Missing: {filename}")
                continue

            try:
                eeg = np.loadtxt(filepath)
                total += 1

                if eeg.shape != (19200, 14):
                    problems.append(
                        f"Unexpected shape: {filename}: {eeg.shape}"
                    )

                if not np.isfinite(eeg).all():
                    problems.append(f"Non-finite values: {filename}")

            except Exception as error:
                problems.append(f"Could not read {filename}: {error}")

    print(f"Recordings successfully read: {total}/96")
    print(f"Problems found: {len(problems)}")

    for problem in problems:
        print(problem)

    if total == 96 and not problems:
        print("DATASET VALIDATION PASSED")
    else:
        raise SystemExit("DATASET VALIDATION FAILED")


if __name__ == "__main__":
    main()
