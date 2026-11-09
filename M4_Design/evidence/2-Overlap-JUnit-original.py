# %%
import pandas as pd
from itertools import combinations
from collections import defaultdict

# %%
# Function to read and process the combined benchmark to methods data
def read_test_to_methods(filename):
    df = pd.read_csv(filename)
    df['Methods'] = df['Methods'].str.split(',')
    df = df.explode('Methods')
    df['Methods'] = df['Methods'].str.strip()
    df = df[df['Methods'] != '']  # Remove empty strings
    return df

# Function to read and process the combined methods to benchmarks data
def read_methods_to_test(filename):
    df = pd.read_csv(filename)
    df['Tested_by'] = df['Tested_by'].str.split(',')
    df = df.explode('Tested_by')
    df['Tested_by'] = df['Tested_by'].str.strip()
    return df

# Function to calculate the Overlap Ratio for a given project
def calculate_overlap_ratio(df):
    tests = df.groupby('Test Name')['Methods'].apply(set)
    intersections = set()
    union = set()
    for t1, t2 in combinations(tests.index, 2):
        intersection = tests[t1] & tests[t2]
        intersections |= intersection
        union |= tests[t1] | tests[t2]
    return len(intersections) / len(union) if union else 0

# Main script
if __name__ == "__main__":
    # Read the combined data
    df_test_to_methods = read_test_to_methods("../inputs/wrangled/u2m/00_combined_test_to_methods.csv")
    df_methods_to_test = read_methods_to_test("../inputs/wrangled/m2u/00_combined_methods_to_test.csv")

    # Calculate the Overlap Ratio for each project
    overlap_ratios = {}
    for project in df_test_to_methods['Project Name'].unique():
        df_project = df_test_to_methods[df_test_to_methods['Project Name'] == project]
        overlap_ratios[project] = calculate_overlap_ratio(df_project)

    # Create a DataFrame from the Overlap Ratios
    df_overlap_ratios = pd.DataFrame.from_dict(overlap_ratios, orient='index', columns=['Overlap Ratio'])

    # Rename the first column to 'Project Name'
    df_overlap_ratios = df_overlap_ratios.rename_axis('Project Name').reset_index()

    # Format the Overlap Ratio to display two decimal places
    df_overlap_ratios['Overlap Ratio'] = df_overlap_ratios['Overlap Ratio'].map('{:.2f}'.format)

    df_overlap_ratios.to_csv("../outputs/Overlap_Ratios_Junit.csv", index=False)
    # Print the DataFrame
    print(df_overlap_ratios)

    


