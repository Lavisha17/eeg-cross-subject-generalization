from pathlib import Path
import numpy as np

DATA_DIR = Path(r"C:\Users\lavis\Downloads\STEW\STEW")

def main():
    total = 0
    problems = []

    for subject in range(1, 49):
        for condition in ["lo", "hi"]:
            filename = f"sub{subject:02d}_{condition}.txt"
            filepath = DATA_DIR / filename

            if not filepath.exists():
                problems.append(f"Missing: {filename}")
                continue

            try:
                eeg = np.loadtxt(filepath)
                total += 1

                if eeg.shape != (19200, 14):
                    problems.append(f"Unexpected shape: {filename}: {eeg.shape}")

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

if __name__ == "__main__":
    main()
