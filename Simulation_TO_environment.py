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

# Clean key columns to ensure consistent formatting
df['Year'] = df['Year'].astype(str).str.strip()
df['Province'] = df['Province'].str.strip()
df['City'] = df['City'].str.strip()
df['Scenario'] = df['Scenario'].str.strip()
df['Battery type'] = df['Battery type'].str.strip()

proportion_df['Year'] = proportion_df['Year'].astype(str).str.strip()
proportion_df['Province'] = proportion_df['Province'].str.strip()
proportion_df['City'] = proportion_df['City'].str.strip()

# Merge two datasets: match by Year, Province, and City
try:
    df = pd.merge(
        df,
        proportion_df[['Year', 'Province', 'City', 'Outdated Pyrometallurgical Recovery NCM',
                       'Outdated Pyrometallurgical Recovery LFP', 'Outdated Hydrometallurgical Recovery NCM',
                       'Hydrometallurgical Recovery NCM', 'Hydrometallurgical Recovery LFP',
                       'Pyro-Hydrometallurgical Recovery NCM']],
        on=['Year', 'Province', 'City'],
        how='left'
    )
except KeyError as e:
    print(f"Error during data merge: {e}")
    print("Please check if proportion_df contains the required columns.")
    raise

# Check if the merge result contains NaN values
new_methods = ['Outdated Pyrometallurgical Recovery NCM', 'Outdated Pyrometallurgical Recovery LFP',
               'Outdated Hydrometallurgical Recovery NCM', 'Hydrometallurgical Recovery NCM',
               'Hydrometallurgical Recovery LFP', 'Pyro-Hydrometallurgical Recovery NCM']
if df[new_methods].isnull().any().any():
    unmatched_rows = df[df[new_methods].isnull().any(axis=1)]
    print("The following rows failed to merge correctly. Please check if the matching keys are correct:")
    print(unmatched_rows[['Year', 'Province', 'City']])
    raise ValueError("Unmatched proportion data detected. Please check data integrity!")

# Battery type metal content - Unit: kg/kWh
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

# Build environmental impact dictionary, adding Province dimension
environment_impact = {}
for index, row in environment_impact_df.iterrows():
    impact = row['Impact']
    for method in new_methods:
        battery_type = 'LFP' if 'LFP' in method else 'NCM'
        environment_impact[(row['Province'], method, battery_type, impact)] = row[method]

# Define ratios
reduction_ratios = [0.20, 0.40, 0.60]

# Initialize ExcelWriter
output_path = './output data_simulation/Environmental impact and metal recovery results under TO scenario.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    for ratio in reduction_ratios:
        adjusted_df = df.copy()
        results = []

        # Adjust process proportions for each battery type
        for index, row in adjusted_df.iterrows():
            year = int(row['Year'])
            if year >= 2024:  # Only adjust proportions for years >= 2024
                # Adjust NCM battery process proportions
                reduction_ncm = row['Hydrometallurgical Recovery NCM'] * ratio
                adjusted_df.at[index, 'Hydrometallurgical Recovery NCM'] = row['Hydrometallurgical Recovery NCM'] - reduction_ncm
                adjusted_df.at[index, 'Pyro-Hydrometallurgical Recovery NCM'] = row['Pyro-Hydrometallurgical Recovery NCM'] + reduction_ncm

                # Adjust LFP battery process proportions
                reduction_lfp = row['Outdated Pyrometallurgical Recovery LFP'] * ratio
                adjusted_df.at[index, 'Outdated Pyrometallurgical Recovery LFP'] = row['Outdated Pyrometallurgical Recovery LFP'] - reduction_lfp
                adjusted_df.at[index, 'Hydrometallurgical Recovery LFP'] = row['Hydrometallurgical Recovery LFP'] + reduction_lfp

        # Calculate results for each scenario and battery type
        for index, row in adjusted_df.iterrows():
            city = row['City']
            province = row['Province']
            year = row['Year']
            scenario = row['Scenario']
            battery_type = row['Battery type']
            battery_weight = row['Weight (thousand t)'] * 1000  # Convert to tons
            battery_capacity_gwh = row['Capacity (GWh)']
            battery_capacity_kwh = battery_capacity_gwh * 1000000  # Convert to kWh

            impact_totals = {impact: 0 for impact in impacts}
            total_metals = {'nickel': 0, 'cobalt': 0, 'lithium': 0, 'manganese': 0}

            # Filter available methods based on battery type
            if battery_type == 'LFP':
                available_methods = [m for m in new_methods if 'LFP' in m]
            else:  # NCM
                available_methods = [m for m in new_methods if 'NCM' in m]

            for method in available_methods:
                if method == 'Outdated Pyrometallurgical Recovery NCM':
                    efficiency = {'nickel': 0.7, 'cobalt': 0.7, 'lithium': 0.55, 'manganese': 0.7}
                elif method == 'Outdated Pyrometallurgical Recovery LFP':
                    efficiency = {'nickel': 0.0, 'cobalt': 0, 'lithium': 0.55, 'manganese': 0}
                elif method == 'Outdated Hydrometallurgical Recovery NCM':
                    efficiency = {'nickel': 0.75, 'cobalt': 0.75, 'lithium': 0.65, 'manganese': 0.75}
                elif method == 'Hydrometallurgical Recovery NCM':
                    efficiency = {'nickel': 0.983, 'cobalt': 0.983, 'lithium': 0.91, 'manganese': 0.983}
                elif method == 'Hydrometallurgical Recovery LFP':
                    efficiency = {'nickel': 0, 'cobalt': 0, 'lithium': 0.92, 'manganese': 0}
                elif method == 'Pyro-Hydrometallurgical Recovery NCM':
                    efficiency = {'nickel': 0.985, 'cobalt': 0.985, 'lithium': 0.95, 'manganese': 0.985}

                proportion = adjusted_df.at[index, method]  # 当前工艺的占比

                if pd.isnull(proportion):
                    print(f"Warning: Proportion for {method} in {city} is NaN, skipping this method")
                    continue

                battery_amount = battery_weight * proportion
                battery_amount_kwh = battery_capacity_kwh * proportion

                # Check if there is valid data
                if battery_amount >= 0:
                    for impact in impacts:
                        impact_value = environment_impact.get((province, method, battery_type, impact), 0)
                        impact_totals[impact] += battery_amount * impact_value

                    # Calculate critical metal recovery (result unit: kg)
                    for metal, content in battery_metal_content[battery_type].items():
                        total_metals[metal] += battery_amount_kwh * content * efficiency.get(metal, 0)
                else:
                    print(f"Skipping invalid data: {city}, {method}, Battery amount: {battery_amount}")

            # Save results
            result_entry = {
                'Year': year,
                'City': city,
                'Province': province,
                'Scenario': scenario,
                'Battery Type': battery_type,
            }
            result_entry.update(impact_totals)
            result_entry.update(total_metals)
            results.append(result_entry)

        # Convert to DataFrame
        results_df = pd.DataFrame(results)

        # Calculate total values for impact indicators
        total_impacts = results_df[impacts].sum()

        # Output total values for each indicator
        print(f"Total values for each indicator with {ratio * 100}% reduction:")
        for impact, total in total_impacts.items():
            print(f"{impact}: {total}")

        # Write results to different sheets in Excel
        sheet_name = f"{ratio * 100}%"
        results_df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Result file path:", output_path)