
import pandas as pd
from collections import Counter


# Function to read and process the combined benchmark to methods data
def read_test_to_methods(filename):
    df = pd.read_csv(filename)
    df['Methods'] = df['Methods'].str.split(',')
    df = df.explode('Methods')
    df['Methods'] = df['Methods'].str.strip()
    df = df[df['Methods'] != '']
    return df


# Function to read and process the combined methods to benchmarks data
def read_methods_to_test(filename):
    df = pd.read_csv(filename)
    df['Tested_by'] = df['Tested_by'].str.split(',')
    df = df.explode('Tested_by')
    df['Tested_by'] = df['Tested_by'].str.strip()
    return df


# M4 optimisation: replace pairwise test comparisons
# with method-frequency counting.
def calculate_overlap_ratio(df):
    tests = df.groupby('Test Name')['Methods'].apply(set)

    # Preserve the original behaviour for fewer than two tests.
    if len(tests) < 2:
        return 0

    method_counts = Counter()

    for methods in tests:
        method_counts.update(methods)

    # Methods covered by at least two distinct tests.
    overlapping_methods = sum(
        1 for count in method_counts.values() if count >= 2
    )

    # All methods covered by the test suite.
    total_methods = len(method_counts)

    return overlapping_methods / total_methods if total_methods else 0


if __name__ == "__main__":
    df_test_to_methods = read_test_to_methods(
        "../inputs/wrangled/u2m/00_combined_test_to_methods.csv"
    )

    df_methods_to_test = read_methods_to_test(
        "../inputs/wrangled/m2u/00_combined_methods_to_test.csv"
    )

    overlap_ratios = {}

    for project in df_test_to_methods['Project Name'].unique():
        df_project = df_test_to_methods[
            df_test_to_methods['Project Name'] == project
        ]
        overlap_ratios[project] = calculate_overlap_ratio(df_project)

    df_overlap_ratios = pd.DataFrame.from_dict(
        overlap_ratios,
        orient='index',
        columns=['Overlap Ratio']
    )

    df_overlap_ratios = (
        df_overlap_ratios.rename_axis('Project Name').reset_index()
    )

    df_overlap_ratios['Overlap Ratio'] = (
        df_overlap_ratios['Overlap Ratio'].map('{:.2f}'.format)
    )

    df_overlap_ratios.to_csv(
        "../outputs/Overlap_Ratios_Junit.csv",
        index=False
    )

    print(df_overlap_ratios)
