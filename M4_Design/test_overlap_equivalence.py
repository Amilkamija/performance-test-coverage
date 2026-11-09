
from pathlib import Path
import importlib.util
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


original = load_module(
    "original",
    ROOT / "M4_Design/evidence/2-Overlap-JUnit-original.py"
)

optimised = load_module(
    "optimised",
    ROOT / "analysis/2-Overlap-JUnit.py"
)


def check(name, dataframe):
    before = original.calculate_overlap_ratio(dataframe)
    after = optimised.calculate_overlap_ratio(dataframe)

    assert abs(before - after) < 1e-12, (
        f"{name}: original={before}, optimised={after}"
    )

    print(f"PASS: {name} ({before:.12f})")


# Check all projects in the real replication dataset.
data = optimised.read_test_to_methods(
    str(ROOT / "inputs/wrangled/u2m/00_combined_test_to_methods.csv")
)

for project, project_data in data.groupby("Project Name"):
    check(project, project_data)


# Additional edge cases.
cases = {
    "single test": [
        ("test1", "methodA"),
    ],
    "no shared methods": [
        ("test1", "methodA"),
        ("test2", "methodB"),
    ],
    "shared method": [
        ("test1", "methodA"),
        ("test2", "methodA"),
    ],
    "identical coverage": [
        ("test1", "methodA"),
        ("test1", "methodB"),
        ("test2", "methodA"),
        ("test2", "methodB"),
    ],
    "mixed coverage": [
        ("test1", "methodA"),
        ("test1", "methodB"),
        ("test2", "methodB"),
        ("test2", "methodC"),
    ],
    "duplicate entries": [
        ("test1", "methodA"),
        ("test1", "methodA"),
        ("test2", "methodA"),
    ],
}

for name, rows in cases.items():
    df = pd.DataFrame(rows, columns=["Test Name", "Methods"])
    check(name, df)

print("\nPASS: all original and optimised calculations match.")
