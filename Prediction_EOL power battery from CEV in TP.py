import numpy as np
import pandas as pd
from random import uniform
from scipy.stats import weibull_min

# Load passenger vehicle data
file_path_passenger = './output data_prediction/CEV_Predictions_results.xlsx'

# Load data
passenger_data = pd.read_excel(file_path_passenger)

# Ensure "Year" column is integer type
passenger_data['Year'] = passenger_data['Year'].astype(int)

# Load vehicle proportion data
file_path_proportion = './input data/Changes in the proportion of CEV type.xlsx'   # Replace with actual file path
vehicle_proportion_data = pd.read_excel(file_path_proportion)
vehicle_proportion_data.set_index('Year', inplace=True)

# Load baseline scenario vehicle proportion data
years = list(range(2017, 2031))
vehicle_proportion = pd.DataFrame({
    'BCEV_LFP': [0.410943396, 0.376493506, 0.306554622, 0.345123967, 0.508817204, 0.607159763, 0.6566, 0.6566, 0.6566, 0.6566, 0.6566, 0.6566, 0.6566, 0.6566],
    'BCEV_NCM111': [0.062762264, 0.047109957, 0.019542857, 0.024542149, 0.008023656, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'BCEV_NCM523': [0.387033962, 0.388657143, 0.4104, 0.325183471, 0.20196129, 0.097928994, 0.049, 0.049, 0.049, 0.049, 0.049, 0.049, 0.049, 0.049],
    'BCEV_NCM622': [0.067992453, 0.105997403, 0.123771429, 0.122710744, 0.079845161, 0.088136095, 0.0784, 0.0784, 0.0784, 0.0784, 0.0784, 0.0784, 0.0784, 0.0784],
    'BCEV_NCM811': [0.002615094, 0.023554978, 0.071657143, 0.134981818, 0.169083871, 0.176272189, 0.1862, 0.1862, 0.1862, 0.1862, 0.1862, 0.1862, 0.1862, 0.1862],
    'BCEV_NCA': [0.002615094, 0.023554978, 0.026057143, 0.006135537, 0.010763441, 0.009792899, 0.0098, 0.0098, 0.0098, 0.0098, 0.0098, 0.0098, 0.0098, 0.0098],
    'HCEV_LFP': [0.029056604, 0.013506494, 0.013445378, 0.014876033, 0.011182796, 0.012840237, 0.0134, 0.0134, 0.0134, 0.0134, 0.0134, 0.0134, 0.0134, 0.0134],
    'HCEV_NCM111': [0.004437736, 0.001690043, 0.000857143, 0.001057851, 0.000176344, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'HCEV_NCM523': [0.027366038, 0.013942857, 0.018, 0.014016529, 0.00443871, 0.002071006, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001],
    'HCEV_NCM622': [0.004807547, 0.003802597, 0.005428571, 0.005289256, 0.001754839, 0.001863905, 0.0016, 0.0016, 0.0016, 0.0016, 0.0016, 0.0016, 0.0016, 0.0016],
    'HCEV_NCM811': [0.000184906, 0.000845022, 0.003142857, 0.005818182, 0.003716129, 0.003727811, 0.0038, 0.0038, 0.0038, 0.0038, 0.0038, 0.0038, 0.0038, 0.0038],
    'HCEV_NCA': [0.000184906, 0.000845022, 0.001142857, 0.000264463, 0.000236559, 0.000207101, 0.0002, 0.0002, 0.0002, 0.0002, 0.0002, 0.0002, 0.0002, 0.0002]
}, index=years)

# Merge baseline scenario data before 2023 and Excel data after 2024
for year in years:
    if year <= 2023:
        vehicle_proportion_data.loc[year] = vehicle_proportion.loc[year]

# Vehicle proportion, sum to 1
vehicle_proportion = vehicle_proportion_data.loc[years]

weibull_params = {
    'BCEV_LFP': {'shape': 3.5, 'scale': 6.5},
    'BCEV_NCM111': {'shape': 3.5, 'scale': 5.5},
    'BCEV_NCM523': {'shape': 3.5, 'scale': 5.5},
    'BCEV_NCM622': {'shape': 3.5, 'scale': 6},
    'BCEV_NCM811': {'shape': 3.5, 'scale': 6.5},
    'BCEV_NCA': {'shape': 3.5, 'scale': 7},
    'HCEV_LFP': {'shape': 3.5, 'scale': 6.8},
    'HCEV_NCM111': {'shape': 3.5, 'scale': 7},
    'HCEV_NCM523': {'shape': 3.5, 'scale': 7},
    'HCEV_NCM622': {'shape': 3.5, 'scale': 7.5},
    'HCEV_NCM811': {'shape': 3.5, 'scale': 8},
    'HCEV_NCA': {'shape': 3.5, 'scale': 8.5},
}

# Battery weight ranges (based on average)
battery_weights = {
    "BCEV_LFP": 790, "BCEV_NCM111": 762, "BCEV_NCM523": 783, "BCEV_NCM622": 833,
    "BCEV_NCM811": 846, "BCEV_NCA": 926, "HCEV_LFP": 160, "HCEV_NCM111": 170,
    "HCEV_NCM523": 174, "HCEV_NCM622": 188, "HCEV_NCM811": 190, "HCEV_NCA": 204
}

# Estimated battery capacity
estimated_battery_capacity = {
    'BCEV_LFP': 150 * uniform(0.6, 0.8),
    'BCEV_NCM111': 160 * uniform(0.6, 0.8),
    'BCEV_NCM523': 180 * uniform(0.6, 0.8),
    'BCEV_NCM622': 180 * uniform(0.6, 0.8),
    'BCEV_NCM811': 200 * uniform(0.6, 0.8),
    'BCEV_NCA': 220 * uniform(0.6, 0.8),
    'HCEV_LFP': 30 * uniform(0.6, 0.8),
    'HCEV_NCM111': 35 * uniform(0.6, 0.8),
    'HCEV_NCM523': 40 * uniform(0.6, 0.8),
    'HCEV_NCM622': 48 * uniform(0.6, 0.8),
    'HCEV_NCM811': 55 * uniform(0.6, 0.8),
    'HCEV_NCA': 64 * uniform(0.6, 0.8),
}

# Calculate Weibull distribution retirement probability
def calculate_weibull_retirement(sales_year, current_year, shape, scale):
    if current_year <= sales_year:
        return 0
    age = current_year - sales_year
    return weibull_min.cdf(age, shape, scale=scale)

# Calculate retired batteries and energy
def calculate_retired_batteries_and_energy(city_data, years, vehicle_proportion, battery_weights, weibull_params, estimated_battery_capacity):
    city_retired_batteries = {}
    for city in city_data['City'].unique():
        city_sales = city_data[city_data['City'] == city]
        city_retired_batteries[city] = {}
        for year in years:
            if year not in city_retired_batteries[city]:
                city_retired_batteries[city][year] = {}
            for model in vehicle_proportion.columns:
                model_weight = battery_weights[model]
                weibull_dist_params = weibull_params[model]
                retired_battery_count = 0
                for sales_year in city_sales['Year'].unique():
                    sales_in_year = city_sales[city_sales['Year'] == sales_year]['CEV_number'].sum()
                    if pd.isna(sales_in_year):
                        sales_in_year = 0
                    retirement_probability = calculate_weibull_retirement(sales_year, year, weibull_dist_params['shape'], weibull_dist_params['scale'])
                    retired_battery_count += sales_in_year * retirement_probability * vehicle_proportion[model].loc[sales_year]
                retired_battery_weight = retired_battery_count * model_weight
                retired_battery_capacity = retired_battery_count * estimated_battery_capacity[model] / 1e6  # Convert to MWh
                city_retired_batteries[city][year][model] = {
                    'retired_battery_weight': retired_battery_weight,
                    'retired_battery_capacity': retired_battery_capacity
                }
    return city_retired_batteries

# Initialize results storage
results = []

# Calculate by battery type
for city in passenger_data['City'].unique():
    city_data = passenger_data[passenger_data['City'] == city]
    retired_data = calculate_retired_batteries_and_energy(city_data, years, vehicle_proportion, battery_weights, weibull_params, estimated_battery_capacity)
    for year in years:
        if year not in retired_data[city]:
            retired_data[city][year] = {}
        for model in vehicle_proportion.columns:
            if model not in retired_data[city][year]:
                retired_data[city][year][model] = {
                    'retired_battery_weight': 0,
                    'retired_battery_capacity': 0
                }
            data = retired_data[city][year][model]
            results.append({
                'City': city,
                'Year': year,
                'Battery type': model,
                'Weight (thousand t)': data['retired_battery_weight'] / 1000000,  # Convert to thousand tons
                'Capacity (GWh)': data['retired_battery_capacity']
            })

# Convert to DataFrame
results_df = pd.DataFrame(results)

# Save results to Excel file
results_df.to_excel('./output data_prediction/TP_EOL power battery from CEV.xlsx', index=False)

print("City retired battery count and energy calculation completed. Results have been saved to an Excel file.")