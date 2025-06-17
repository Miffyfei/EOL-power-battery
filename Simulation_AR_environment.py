import pandas as pd
import random

# File paths
data_path = './input data/EOL LFP and NCM battery.xlsx'
proportion_data_path = './input data/Proportion of recycling technologies under BS.xlsx'
environment_impact_path = './input data/LCA data.xlsx'

# Load data
df = pd.read_excel(data_path)  # Battery retirement data
proportion_df = pd.read_excel(proportion_data_path)  # Proportion of recycling technologies
environment_impact_df = pd.read_excel(environment_impact_path)  # Environmental impact data

# Clean Province column (remove trailing spaces)
environment_impact_df['Province'] = environment_impact_df['Province'].str.strip()

# Output proportion_df column names
print("proportion_df column names:", proportion_df.columns)

# Print environment_impact_df column names for debugging
print("environment_impact_df column names:", environment_impact_df.columns)

# Clean key columns to ensure consistent formatting
df['Year'] = df['Year'].astype(str).str.strip()
df['Province'] = df['Province'].str.strip()
df['City'] = df['City'].str.strip()
df['Scenario'] = df['Scenario'].str.strip()
df['Battery type'] = df['Battery type'].str.strip()

proportion_df['Year'] = proportion_df['Year'].astype(str).str.strip()
proportion_df['Province'] = proportion_df['Province'].str.strip()
proportion_df['City'] = proportion_df['City'].str.strip()

new_methods = ['Outdated Pyrometallurgical Recovery NCM', 'Outdated Pyrometallurgical Recovery LFP',
               'Outdated Hydrometallurgical Recovery NCM', 'Hydrometallurgical Recovery NCM',
               'Hydrometallurgical Recovery LFP', 'Pyro-Hydrometallurgical Recovery NCM']

# Merge data: match by Year, Province and City
try:
    df = pd.merge(
        df,
        proportion_df[['Year', 'Province', 'City'] + new_methods],
        on=['Year', 'Province', 'City'],
        how='left'
    )
except KeyError as e:
    print(f"Error merging data: {e}")
    print("Please check if proportion_df contains the required columns.")
    raise

# Check if merged results contain NaN values
if df[new_methods].isnull().any().any():
    unmatched_rows = df[df[new_methods].isnull().any(axis=1)]
    print("The following rows failed to merge correctly, please check matching keys:")
    print(unmatched_rows[['Year', 'Province', 'City']])
    raise ValueError("Unmatched proportion data exists, please check data integrity!")

# Battery metal content (unit: kg/kWh)
battery_metal_content = {
    'LFP': {'lithium': 0.106, 'nickel': 0, 'cobalt': 0, 'manganese': 0},
    'NCM': {'lithium': 0.109879, 'nickel': 0.6, 'cobalt': 0.23475, 'manganese': 0.24},
}

# New impacts list
impacts = [
    'Abiotic depletion', 'Abiotic depletion (fossil fuels)', 'Acidification',
    'Eutrophication', 'Fresh water aquatic ecotox.', 'Global warming (GWP100a)',
    'Human toxicity', 'Marine aquatic ecotoxicity', 'Ozone layer depletion (ODP)',
    'Photochemical oxidation', 'Terrestrial ecotoxicity'
]

# Build environmental impact dictionary, add province dimension
environment_impact = {}
for index, row in environment_impact_df.iterrows():
    impact = row['Impact']
    for method in new_methods:
        # Determine battery type based on method name
        battery_type = 'LFP' if 'LFP' in method else 'NCM'
        environment_impact[(row['Province'], method, battery_type, impact)] = row[method]

# Check if proportion columns contain NaN
if df[new_methods].isnull().any().any():
    print("The following rows have NaN proportion data:")
    print(df[df[new_methods].isnull().any(axis=1)][['Year', 'Province', 'City']])
    raise ValueError("Incomplete proportion data, please check data source.")

# Define reduction ratios
reduction_ratios = [0.20, 0.40, 0.60]

# Initialize ExcelWriter
output_path = './output data_simulation/Environmental impact and metal recovery results under AR scenario.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    for ratio in reduction_ratios:
        adjusted_df = df.copy()
        results = []

        # Adjust process proportions for each battery type
        for index, row in adjusted_df.iterrows():
            year = int(row['Year'])
            battery_type = row['Battery type']

            # Filter available processes based on battery type
            if battery_type == 'LFP':
                available_methods = [m for m in new_methods if 'LFP' in m]
            else:  # NCM
                available_methods = [m for m in new_methods if 'NCM' in m]

            if year >= 2024:
                # Adjust outdated process proportions (only for current battery type processes)
                if battery_type == 'LFP':
                    reduction_lfp = row['Outdated Pyrometallurgical Recovery LFP'] * ratio
                    adjusted_df.at[index, 'Outdated Pyrometallurgical Recovery LFP'] = row['Outdated Pyrometallurgical Recovery LFP'] - reduction_lfp
                    adjusted_df.at[index, 'Hydrometallurgical Recovery LFP'] = row['Hydrometallurgical Recovery LFP'] + reduction_lfp
                else:  # NCM
                    reduction_ncm = row['Outdated Pyrometallurgical Recovery NCM'] * ratio
                    reduction_wet_ncm = row['Outdated Hydrometallurgical Recovery NCM'] * ratio

                    adjusted_df.at[index, 'Outdated Pyrometallurgical Recovery NCM'] = row['Outdated Pyrometallurgical Recovery NCM'] - reduction_ncm
                    adjusted_df.at[index, 'Outdated Hydrometallurgical Recovery NCM'] = row['Outdated Hydrometallurgical Recovery NCM'] - reduction_wet_ncm
                    adjusted_df.at[index, 'Hydrometallurgical Recovery NCM'] = row['Hydrometallurgical Recovery NCM'] + reduction_ncm + reduction_wet_ncm

            # Ensure sum of available process proportions for current battery type is 1
            current_proportions = adjusted_df.loc[index, available_methods].sum()
            if current_proportions > 0:  # Avoid division by zero
                for method in available_methods:
                    adjusted_df.at[index, method] = adjusted_df.at[index, method] / current_proportions

            # Verify adjusted proportions sum to approximately 1
            new_total_proportion = adjusted_df.loc[index, available_methods].sum()
            if abs(new_total_proportion - 1) > 1e-9:  # Consider floating point error
                print(f"Warning: {battery_type} battery adjusted proportion sum is not 1 in {year}, actual value: {new_total_proportion}, row index: {index}")

        # Calculate results for each scenario and battery type
        for index, row in adjusted_df.iterrows():
            city = row['City']
            province = row['Province']
            year = int(row['Year'])
            scenario = row['Scenario']
            battery_type = row['Battery type']

            # Convert battery weight to tons, get total battery capacity
            battery_weight = row['Weight (thousand t)'] * 1e4
            battery_capacity_gwh = row['Capacity (GWh)']
            battery_capacity_kwh = battery_capacity_gwh * 1000000  # Convert to kWh

            impact_totals = {impact: 0 for impact in impacts}
            total_metals = {'nickel': 0, 'cobalt': 0, 'lithium': 0, 'manganese': 0}

            # Filter available processes based on battery type
            if battery_type == 'LFP':
                available_methods = [m for m in new_methods if 'LFP' in m]
            else:  # NCM
                available_methods = [m for m in new_methods if 'NCM' in m]

            for method in available_methods:
                if method == 'Outdated Pyrometallurgical Recovery NCM':
                    efficiency = {'nickel': 0.7, 'cobalt': 0.7, 'lithium': 0.5, 'manganese': 0.7}
                elif method == 'Outdated Pyrometallurgical Recovery LFP':
                    efficiency = {'nickel': 0.0, 'cobalt': 0, 'lithium': 0.5, 'manganese': 0}
                elif method == 'Outdated Hydrometallurgical Recovery NCM':
                    efficiency = {'nickel': 0.75, 'cobalt': 0.75, 'lithium': 0.6, 'manganese': 0.75}
                elif method == 'Hydrometallurgical Recovery NCM':
                    efficiency = {'nickel': 0.98, 'cobalt': 0.98, 'lithium': 0.9, 'manganese': 0.98}
                elif method == 'Hydrometallurgical Recovery LFP':
                    efficiency = {'nickel': 0, 'cobalt': 0, 'lithium': 0.9, 'manganese': 0}
                elif method == 'Pyro-Hydrometallurgical Recovery NCM':
                    efficiency = {'nickel': 0.98, 'cobalt': 0.98, 'lithium': 0.9, 'manganese': 0.98}

                proportion = adjusted_df.at[index, method]  # Current process proportion

                if pd.isnull(proportion):
                    print(f"Warning: {method} proportion in {city} is NaN, skipping this process")
                    continue

                battery_amount = battery_weight * proportion
                battery_amount_kwh = battery_capacity_kwh * proportion

                # Check if valid data exists
                if battery_amount >= 0:
                    for impact in impacts:
                        impact_value = environment_impact.get((province, method, battery_type, impact), 0)
                        impact_totals[impact] += battery_amount * impact_value

                    # Calculate key metal recovery (result unit: kg, as metal content unit is kg/kWh)
                    for metal, content in battery_metal_content[battery_type].items():
                        total_metals[metal] += battery_amount_kwh * content * efficiency.get(metal, 0)
                else:
                    print(f"Skipping invalid data: {city}, {method}, battery amount: {battery_amount}")

            # Save results
            result_entry = {
                'Year': year,
                'City': city,
                'Province': province,
                'Scenario': scenario,
                'Battery type': battery_type,
            }
            result_entry.update(impact_totals)
            result_entry.update(total_metals)
            results.append(result_entry)

        # Convert to DataFrame
        results_df = pd.DataFrame(results)

        if not results_df.empty:
            # Calculate total values for impact metrics
            total_impacts = results_df[impacts].sum()

            # Write results to Excel sheet, sheet named with adjusted ratio
            sheet_name = f"Adjusted ratio_{ratio}"
            results_df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Output total values for each metric
            print(f"Total values for each metric at adjusted ratio {ratio}:")
            for impact, total in total_impacts.items():
                print(f"{impact}: {total}")
        else:
            print(f"Result DataFrame is empty for adjusted ratio {ratio}, not written to Excel file.")

# Output file path
print("Result file path:", output_path)