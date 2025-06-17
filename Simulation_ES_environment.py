import pandas as pd
import random

# Encapsulate function to get recycling process efficiency
def get_efficiency(method, battery_type):
    """
    Get corresponding recovery efficiency based on recycling process and battery type
    :param method: Recycling process name
    :param battery_type: Battery type (LFP or NCM)
    :return: Dictionary containing metal recovery efficiencies
    """
    # Verify if method matches battery type
    if ('NCM' in method and battery_type != 'NCM') or ('LFP' in method and battery_type != 'LFP'):
        print(f"Warning: Process {method} does not match battery type {battery_type}")
        return {}

    efficiency_map = {
        'Outdated Pyrometallurgical Recovery NCM': {'nickel': 0.7, 'cobalt': 0.7, 'lithium': 0.5, 'manganese': 0.7},
        'Outdated Pyrometallurgical Recovery LFP': {'nickel': 0.0, 'cobalt': 0, 'lithium': 0.5, 'manganese': 0},
        'Outdated Hydrometallurgical Recovery NCM': {'nickel': 0.75, 'cobalt': 0.75, 'lithium': 0.6, 'manganese': 0.75},
        'Hydrometallurgical Recovery NCM': {'nickel': 0.98, 'cobalt': 0.98, 'lithium': 0.9, 'manganese': 0.98},
        'Hydrometallurgical Recovery LFP': {'nickel': 0, 'cobalt': 0, 'lithium': 0.9, 'manganese': 0},
        'Pyro-Hydrometallurgical Recovery NCM': {'nickel': 0.98, 'cobalt': 0.98, 'lithium': 0.9, 'manganese': 0.98},
    }

    return efficiency_map.get(method, {})


# Filter applicable recycling processes
def get_applicable_methods(battery_type):
    """
    Get applicable recycling processes based on battery type
    :param battery_type: Battery type (LFP or NCM)
    :return: List of applicable recycling processes
    """
    if battery_type == 'LFP':
        return ['Outdated Pyrometallurgical Recovery LFP', 'Hydrometallurgical Recovery LFP']
    elif battery_type == 'NCM':
        return ['Outdated Pyrometallurgical Recovery NCM', 'Outdated Hydrometallurgical Recovery NCM',
                'Hydrometallurgical Recovery NCM', 'Pyro-Hydrometallurgical Recovery NCM']
    else:
        print(f"Warning: Unknown battery type {battery_type}")
        return []


# Build environmental impact dictionary
def build_environment_impact_dict(df):
    """
    Build environmental impact dictionary based on data
    :param df: DataFrame containing environmental impact data
    :return: Environmental impact dictionary
    """
    environment_impact = {}
    for _, row in df.iterrows():
        province = row['Province']
        impact_category = row['Impact']
        for method in new_methods:
            # Determine battery type based on method name
            if 'NCM' in method:
                battery_type = 'NCM'
            elif 'LFP' in method:
                battery_type = 'LFP'
            else:
                continue  # Skip unmatched processes
            key = (province, method, battery_type, impact_category)
            environment_impact[key] = row[method]
    return environment_impact


# File paths
data_path = './input data/EOL LFP and NCM battery.xlsx'
proportion_data_path = './input data/Proportion of recycling technologies under BS.xlsx'
old_environment_impact_path = './input data/LCA data.xlsx'

# New scenario file paths
ssp3_path = './input data/LCA data about ES3.xlsx'
ssp2_path = './input data/LCA data about ES2.xlsx'
ssp1_path = './input data/LCA data about ES1.xlsx'


# Load data
try:
    df = pd.read_excel(data_path)
    proportion_df = pd.read_excel(proportion_data_path)
    old_environment_impact_df = pd.read_excel(old_environment_impact_path)
    ssp1_df = pd.read_excel(ssp1_path)
    ssp2_df = pd.read_excel(ssp2_path)
    ssp3_df = pd.read_excel(ssp3_path)
except FileNotFoundError as e:
    print(f"File not found: {e}")
    raise

# Clean Province column (remove trailing spaces)
old_environment_impact_df['Province'] = old_environment_impact_df['Province'].str.strip()

# Clean data format
df['Year'] = df['Year'].astype(str).str.strip()
df['Province'] = df['Province'].str.strip()
df['City'] = df['City'].str.strip()
df['Scenario'] = df['Scenario'].str.strip()
df['Battery type'] = df['Battery type'].str.strip()

proportion_df['Year'] = proportion_df['Year'].astype(str).str.strip()
proportion_df['Province'] = proportion_df['Province'].str.strip()
proportion_df['City'] = proportion_df['City'].str.strip()


# Merge proportion data
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
    print(f"Error merging data: {e}")
    raise

# Enhance data integrity check
key_columns = ['Weight (thousand t)', 'Capacity (GWh)']
for col in key_columns:
    if df[col].isnull().any():
        print(f"Data column {col} has missing values!")
        raise ValueError("Incomplete data!")


new_methods = ['Outdated Pyrometallurgical Recovery NCM', 'Outdated Pyrometallurgical Recovery LFP',
               'Outdated Hydrometallurgical Recovery NCM', 'Hydrometallurgical Recovery NCM',
               'Hydrometallurgical Recovery LFP', 'Pyro-Hydrometallurgical Recovery NCM']
if df[new_methods].isnull().any().any():
    unmatched_rows = df[df[new_methods].isnull().any(axis=1)]
    print("The following rows have unmatched proportion data:")
    print(unmatched_rows[['Year', 'Province', 'City']])
    raise ValueError("Incomplete data!")

# Battery metal content (unit: kg/kWh)
battery_metal_content = {
    'LFP': {'lithium': 0.106, 'nickel': 0, 'cobalt': 0, 'manganese': 0},
    'NCM': {'lithium': 0.109879, 'nickel': 0.6, 'cobalt': 0.23475, 'manganese': 0.24},
}

# Environmental impact categories
new_impacts = [
    "Abiotic depletion", "Abiotic depletion (fossil fuels)", "Acidification",
    "Eutrophication", "Fresh water aquatic ecotox.", "Global warming (GWP100a)",
    "Human toxicity", "Marine aquatic ecotoxicity", "Ozone layer depletion (ODP)",
    "Photochemical oxidation", "Terrestrial ecotoxicity"
]

# Build environmental impact dictionaries
old_environment_impact = build_environment_impact_dict(old_environment_impact_df)
ssp1_impact = build_environment_impact_dict(ssp1_df)
ssp2_impact = build_environment_impact_dict(ssp2_df)
ssp3_impact = build_environment_impact_dict(ssp3_df)

# Scenario list
scenarios = ['BS', 'TP', 'ED', 'LE']

# Initialize Excel writer
output_path = './output data_simulation/Environmental impact and metal recovery results under ES scenario.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    # Process three scenarios
    for ssp_impact, ssp_name in zip([ssp1_impact, ssp2_impact, ssp3_impact], ['SSP1', 'SSP2', 'SSP3']):
        all_scenario_results = []
        # Process each scenario
        for scenario in scenarios:
            scenario_results = []
            for index, row in df.iterrows():
                if row['Scenario'] != scenario:
                    continue
                year = int(row['Year'])
                province = row['Province']
                city = row['City']
                battery_type = row['Battery type']
                battery_weight = row['Weight (thousand t)'] * 1e3  # Convert to tons
                battery_capacity_gwh = row['Capacity (GWh)']
                battery_capacity_kwh = battery_capacity_gwh * 1e6  # Convert to kWh

                # Get applicable processes
                applicable_methods = get_applicable_methods(battery_type)

                # Validate sum of process proportions
                total_proportion = row[applicable_methods].sum()
                if abs(total_proportion - 1) > 1e-6:
                    print(f"Warning: Sum of {battery_type} battery process proportions in {city} is {total_proportion}, not equal to 1")

                # Calculate uniform change value
                if year >= 2024 and year < 2030:
                    impact_values = {}
                    for impact in new_impacts:
                        for method in applicable_methods:
                            key = (province, method, battery_type, impact)
                            old_value = old_environment_impact.get(key, 0)
                            new_value = ssp_impact.get(key, 0)
                            diff = (old_value - new_value) / 6  # Change over 6 years from 2024-2029
                            # Apply different change values based on year
                            impact_values[(method, impact)] = old_value - (year - 2023) * diff

                else:
                    current_impact = ssp_impact if year >= 2030 else old_environment_impact

                impact_totals = {impact: 0 for impact in new_impacts}
                total_metals = {'nickel': 0, 'cobalt': 0, 'lithium': 0, 'manganese': 0}

                # Only process applicable methods
                for method in applicable_methods:
                    proportion = row[method]
                    if pd.isna(proportion) or proportion == 0:
                        continue  # Correctly handle proportion of 0

                    battery_amount = battery_weight * proportion
                    battery_amount_kwh = battery_capacity_kwh * proportion

                    # Calculate environmental impact
                    for impact in new_impacts:
                        if year >= 2024 and year < 2030:
                            impact_value = impact_values.get((method, impact), 0)
                        else:
                            key = (province, method, battery_type, impact)
                            impact_value = current_impact.get(key, 0)
                        impact_totals[impact] += battery_amount * impact_value

                    # Calculate metal recovery
                    efficiency = get_efficiency(method, battery_type)
                    for metal, content in battery_metal_content[battery_type].items():
                        # Metal content unit is kg/kWh, result unit is kg
                        total_metals[metal] += battery_amount_kwh * content * efficiency.get(metal, 0)

                # Save current scenario results
                result = {
                    'Year': year,
                    'Province': province,
                    'City': city,
                    'Scenario': scenario,
                    'Battery type': battery_type,
                    **impact_totals,
                    **total_metals
                }
                scenario_results.append(result)
            all_scenario_results.extend(scenario_results)

        # Convert to DataFrame and write to Excel
        combined_df = pd.DataFrame(all_scenario_results)
        sheet_name = f'{ssp_name} scenario'
        combined_df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Processing completed! Results saved to:", output_path)