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

# Initialize results storage
results = []

# Check if there are NaN values in the proportion columns
if df[new_methods].isnull().any().any():
    print("The following rows have NaN proportion data:")
    print(df[df[new_methods].isnull().any(axis=1)][['Year', 'Province', 'City']])
    raise ValueError("Incomplete proportion data. Please check the data source.")

# Calculate results for each scenario and battery type
for index, row in df.iterrows():
    city = row['City']
    province = row['Province']
    year = row['Year']
    scenario = row['Scenario']
    battery_type = row['Battery type']
    battery_weight = row['Weight (thousand t)'] * 1e3  # Convert to tons
    battery_capacity_gwh = row['Capacity (GWh)']  # Retired battery total capacity (GWh)
    battery_capacity_kwh = battery_capacity_gwh * 1e6  # Convert to kWh

    impact_totals = {impact: 0 for impact in impacts}
    total_metals = {'nickel': 0, 'cobalt': 0, 'lithium': 0, 'manganese': 0}

    # Filter available methods based on battery type
    if battery_type == 'LFP':
        available_methods = [m for m in new_methods if 'LFP' in m]
    else:  # NCM
        available_methods = [m for m in new_methods if 'NCM' in m]

    # Verify if the sum of proportions of available processes is 1
    total_proportion = sum(row[m] for m in available_methods)
    if abs(total_proportion - 1) > 0.001:
        print(f"Warning: The sum of proportions of available processes for {city} {battery_type} is {total_proportion:.4f}, not equal to 1")

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

        proportion = row[method]  # Proportion of current process

        # Calculate amounts for environmental impact and metal recovery separately
        battery_amount_tons = battery_weight * proportion  # Tons, for environmental impact
        battery_amount_kwh = battery_capacity_kwh * proportion  # kWh, for metal recovery

        # Check if there is valid data
        if battery_amount_tons >= 0 and battery_amount_kwh >= 0:
            # Environmental impact calculation (in tons)
            for impact in impacts:
                impact_value = environment_impact.get((province, method, battery_type, impact), 0)
                impact_totals[impact] += battery_amount_tons * impact_value

            # Metal recovery calculation (in kWh, metal content unit is kg/kWh, result unit is kg)
            for metal, content in battery_metal_content[battery_type].items():
                total_metals[metal] += battery_amount_kwh * content * efficiency.get(metal, 0)
        else:
            print(f"Skipping invalid data: {city}, {method}, Battery weight: {battery_amount_tons}, Battery capacity: {battery_amount_kwh}")

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

# Export results to Excel (remove summary table, keep detailed results only)
output_path = './output data_simulation/Environmental impact and metal recovery results under BS scenario.xlsx'
results_df.to_excel(output_path, index=False)

# Output the total value of each indicator
print("Total values for each indicator:")
for impact in impacts + ['lithium', 'nickel', 'cobalt', 'manganese']:
    print(f"{impact}: {results_df[impact].sum()}")

# Output file path
print("Result file path:", output_path)
