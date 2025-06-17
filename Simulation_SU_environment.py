import pandas as pd

# File paths
data_path = './input data/EOL LFP and NCM battery.xlsx'
proportion_data_path = './input data/Proportion of recycling technologies under BS.xlsx'
environment_impact_path = './input data/LCA data includes secondary-use technology.xlsx'

# Load data
df = pd.read_excel(data_path)  # Battery retirement data
proportion_df = pd.read_excel(proportion_data_path)  # Recycling technology proportion data
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

# Merge data: match by Year, Province and City
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
    print("Please check if proportion_df contains the required columns.")
    raise

# Check if merged results contain NaN values
new_methods = ['Outdated Pyrometallurgical Recovery NCM', 'Outdated Pyrometallurgical Recovery LFP',
               'Outdated Hydrometallurgical Recovery NCM', 'Hydrometallurgical Recovery NCM',
               'Hydrometallurgical Recovery LFP', 'Pyro-Hydrometallurgical Recovery NCM']
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

# impacts list
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
    # Assume environmental impact data exists for Secondary Use LFP
    environment_impact[(row['Province'], 'Secondary Use LFP', 'LFP', impact)] = row.get('Secondary Use LFP', 0)
    # Add environmental impact data for Secondary Use NCM
    environment_impact[(row['Province'], 'Secondary Use NCM', 'NCM', impact)] = row.get('Secondary Use NCM', 0)

# Secondary use ratios
second_use_ratios = [0.2, 0.4, 0.6]

# Metal recovery efficiency
recovery_efficiency = {
    'Outdated Pyrometallurgical Recovery NCM': {'nickel': 0.7, 'cobalt': 0.7, 'lithium': 0.5, 'manganese': 0.7},
    'Outdated Pyrometallurgical Recovery LFP': {'nickel': 0.0, 'cobalt': 0, 'lithium': 0.5, 'manganese': 0},
    'Outdated Hydrometallurgical Recovery NCM': {'nickel': 0.75, 'cobalt': 0.75, 'lithium': 0.6, 'manganese': 0.75},
    'Hydrometallurgical Recovery NCM': {'nickel': 0.98, 'cobalt': 0.98, 'lithium': 0.9, 'manganese': 0.98},
    'Hydrometallurgical Recovery LFP': {'nickel': 0, 'cobalt': 0, 'lithium': 0.9, 'manganese': 0},
    'Pyro-Hydrometallurgical Recovery NCM': {'nickel': 0.98, 'cobalt': 0.98, 'lithium': 0.9, 'manganese': 0.98},
    'Secondary Use LFP': {'nickel': 0, 'cobalt': 0, 'lithium': 0.8, 'manganese': 0},  # Adjusted lithium recovery rate to 80%
    'Secondary Use NCM': {'nickel': 0.8, 'cobalt': 0.8, 'lithium': 0.8, 'manganese': 0.8}  # Added NCM secondary use recovery rate
}


# Initialize result storage
all_results = {}

# Check if proportion columns contain NaN
if df[new_methods].isnull().any().any():
    print("The following rows have NaN proportion data:")
    print(df[df[new_methods].isnull().any(axis=1)][['Year', 'Province', 'City']])
    raise ValueError("Incomplete proportion data, please check data source.")

# Iterate through three secondary use scenarios
for second_use_ratio in second_use_ratios:
    results = []
    for index, row in df.iterrows():
        city = row['City']
        province = row['Province']
        year = row['Year']
        scenario = row['Scenario']
        battery_type = row['Battery type']
        battery_weight = row['Weight (thousand t)'] * 1e3  # Convert to tons
        battery_capacity_gwh = row['Capacity (GWh)']
        battery_capacity_kwh = battery_capacity_gwh * 1000000  # Convert to kWh

        impact_totals = {impact: 0 for impact in impacts}
        total_metals = {'nickel': 0, 'cobalt': 0, 'lithium': 0, 'manganese': 0}

        # Get applicable process list
        applicable_methods = [m for m in new_methods if (battery_type == 'LFP' and 'LFP' in m) or
                              (battery_type == 'NCM' and 'NCM' in m)]

        # Validate sum of process proportions
        total_proportion = row[applicable_methods].sum()
        if abs(total_proportion - 1) > 1e-6:
            print(f"Warning: Sum of {battery_type} battery process proportions in {city} is {total_proportion}, not equal to 1")

        # Process secondary use
        if int(year) >= 2024:
            # Secondary use portion
            second_use_amount = battery_weight * second_use_ratio
            second_use_amount_kwh = battery_capacity_kwh * second_use_ratio

            remaining_amount = battery_weight - second_use_amount
            remaining_amount_kwh = battery_capacity_kwh - second_use_amount_kwh

            # Environmental impact of secondary use
            second_use_method = f'Secondary Use {battery_type}'
            for impact in impacts:
                impact_value = environment_impact.get((province, second_use_method, battery_type, impact), 0)
                impact_totals[impact] += second_use_amount * impact_value

            # Metal recovery from secondary use
            for metal, content in battery_metal_content[battery_type].items():
                total_metals[metal] += second_use_amount_kwh * content * recovery_efficiency[second_use_method][metal]

            # Process remaining battery recycling
            for method in applicable_methods:
                proportion = row[method]

                # Calculate battery amount processed by this method
                battery_amount = remaining_amount * proportion
                battery_amount_kwh = remaining_amount_kwh * proportion

                # Check if valid data exists
                if battery_amount >= 0:
                    for impact in impacts:
                        impact_value = environment_impact.get((province, method, battery_type, impact), 0)
                        impact_totals[impact] += battery_amount * impact_value

                    # Calculate key metal recovery
                    for metal, content in battery_metal_content[battery_type].items():
                        total_metals[metal] += battery_amount_kwh * content * recovery_efficiency[method][metal]
                else:
                    print(f"Skipping invalid data: {city}, {method}, battery amount: {battery_amount}")
        else:
            # Before 2024, secondary use is not considered
            for method in applicable_methods:
                proportion = row[method]

                if pd.isnull(proportion) or proportion == 0:
                    continue  # Skip processes with NaN or 0 proportion

                battery_amount = battery_weight * proportion
                battery_amount_kwh = battery_capacity_kwh * proportion

                # 检查是否有有效数据
                if battery_amount >= 0:
                    for impact in impacts:
                        impact_value = environment_impact.get((province, method, battery_type, impact), 0)
                        impact_totals[impact] += battery_amount * impact_value

                    # 计算关键金属回收量
                    for metal, content in battery_metal_content[battery_type].items():
                        total_metals[metal] += battery_amount_kwh * content * recovery_efficiency[method][metal]
                else:
                    print(f"Skipping invalid data: {city}, {method}, battery amount: {battery_amount}")

        # 保存结果
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

    all_results[second_use_ratio] = pd.DataFrame(results)

# Export results to different sheets in Excel
output_path = './output data_simulation/Environmental impact and metal recovery results under SU scenario.xlsx'
with pd.ExcelWriter(output_path) as writer:
    for ratio, df_result in all_results.items():
        sheet_name = str(ratio)
        df_result.to_excel(writer, sheet_name=sheet_name, index=False)

# Calculate annual environmental impact and metal recovery totals for 2020 - 2030
years = [str(year) for year in range(2020, 2031)]
combined_df = pd.concat(all_results.values())
for year in years:
    year_df = combined_df[combined_df['Year'] == year]
    total_impacts = year_df[impacts].sum()
    total_metals = year_df[['nickel', 'cobalt', 'lithium', 'manganese']].sum()

    print(f"Year: {year}")
    print("Total environmental impact:")
    for impact, total in total_impacts.items():
        print(f"{impact}: {total}")
    print("Total metal recovery:")
    for metal, total in total_metals.items():
        print(f"{metal}: {total}")
    print("-" * 50)

# Output file path
print("Result file path:", output_path)