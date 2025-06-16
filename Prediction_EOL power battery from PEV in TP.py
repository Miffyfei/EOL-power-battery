import numpy as np
from random import uniform
import pandas as pd
from scipy.stats import weibull_min

# Load passenger vehicle data
file_path_passenger = './output data_prediction/PEV_Predictions_results.xlsx'
# Load data
passenger_data = pd.read_excel(file_path_passenger)
# Ensure "Year" column is integer type
passenger_data['Year'] = passenger_data['Year'].astype(int)

# Load vehicle proportion data
file_path_proportion = './input data/Changes in the proportion of PEV type.xlsx'  # Replace with actual file path
vehicle_proportion_data = pd.read_excel(file_path_proportion)
vehicle_proportion_data.set_index('Year', inplace=True)

# Load baseline scenario vehicle proportion data
years = list(range(2016, 2031))
vehicle_proportion = pd.DataFrame({
    'BPEV_LFP': [0.543065476, 0.355647668, 0.29184876, 0.251713961, 0.288924559, 0.4394, 0.49042, 0.49781, 0.49781, 0.49781, 0.49781, 0.49781, 0.49781, 0.49781, 0.49781],
    'BPEV_NCM111': [0.028836012, 0.054317098, 0.036518511, 0.016046765, 0.020545746, 0.006929, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'BPEV_NCM523': [0.168579762, 0.33495544, 0.301277719, 0.336982066, 0.27223114, 0.174408, 0.0791, 0.03715, 0.03715, 0.03715, 0.03715, 0.03715, 0.03715, 0.03715, 0.03715],
    'BPEV_NCM622': [0.022181548, 0.058843523, 0.082166651, 0.101629512, 0.102728732, 0.068952, 0.07119, 0.05944, 0.05944, 0.05944, 0.05944, 0.05944, 0.05944, 0.05944, 0.05944],
    'BPEV_NCM811': [0.001109077, 0.002263212, 0.018259256, 0.058838138, 0.113001605, 0.146016, 0.14238, 0.14117, 0.14117, 0.14117, 0.14117, 0.14117, 0.14117, 0.14117, 0.14117],
    'BPEV_NCA': [0.001109077, 0.002263212, 0.018259256, 0.021395687, 0.005136437, 0.009295, 0.00791, 0.00743, 0.00743, 0.00743, 0.00743, 0.00743, 0.00743, 0.00743, 0.00743],
    'HPEV_LFP': [0.166934524, 0.084352332, 0.09815124, 0.068286039, 0.071075441, 0.0806, 0.12958, 0.17219, 0.17219, 0.17219, 0.17219, 0.17219, 0.17219, 0.17219, 0.17219],
    'HPEV_NCM111': [0.008863988, 0.012882902, 0.012281489, 0.004353235, 0.005054254, 0.001271, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'HPEV_NCM523': [0.051820238, 0.07944456, 0.101322281, 0.091417934, 0.06696886, 0.031992, 0.0209, 0.01285, 0.01285, 0.01285, 0.01285, 0.01285, 0.01285, 0.01285, 0.01285],
    'HPEV_NCM622': [0.006818452, 0.013956477, 0.027633349, 0.027570488, 0.025271268, 0.012648, 0.01881, 0.02056, 0.02056, 0.02056, 0.02056, 0.02056, 0.02056, 0.02056, 0.02056],
    'HPEV_NCM811': [0.000340923, 0.000536788, 0.006140744, 0.015961862, 0.027798395, 0.026784, 0.03762, 0.04883, 0.04883, 0.04883, 0.04883, 0.04883, 0.04883, 0.04883, 0.04883],
    'HPEV_NCA': [0.000340923, 0.000536788, 0.006140744, 0.005804313, 0.001263563, 0.001705, 0.00209, 0.00257, 0.00257, 0.00257, 0.00257, 0.00257, 0.00257, 0.00257, 0.00257]
}, index=years)

# Merge baseline scenario data before 2023 and Excel data after 2024
for year in years:
    if year <= 2023:
        vehicle_proportion_data.loc[year] = vehicle_proportion.loc[year]

# Vehicle proportion, sum to 1
vehicle_proportion = vehicle_proportion_data.loc[years]

weibull_params = {
    'BPEV_LFP': {'shape': 3.5, 'scale': 9},
    'BPEV_NCM111': {'shape': 3.5, 'scale': 8},
    'BPEV_NCM523': {'shape': 3.5, 'scale': 9},
    'BPEV_NCM622': {'shape': 3.5, 'scale': 10},
    'BPEV_NCM811': {'shape': 3.5, 'scale': 10.5},
    'BPEV_NCA': {'shape': 3.5, 'scale': 11},
    'HPEV_LFP': {'shape': 3.5, 'scale': 10.5},
    'HPEV_NCM111': {'shape': 3.5, 'scale': 9.5},
    'HPEV_NCM523': {'shape': 3.5, 'scale': 10.5},
    'HPEV_NCM622': {'shape': 3.5, 'scale': 11.5},
    'HPEV_NCM811': {'shape': 3.5, 'scale': 12},
    'HPEV_NCA': {'shape': 3.5, 'scale': 12.5},
}

# Battery weight ranges (based on average)
battery_weights = {
    "BPEV_LFP": 350, "BPEV_NCM111": 349, "BPEV_NCM523": 303, "BPEV_NCM622": 305,
    "BPEV_NCM811": 479, "BPEV_NCA": 208, "HPEV_LFP": 357, "HPEV_NCM111": 333,
    "HPEV_NCM523": 278, "HPEV_NCM622": 250, "HPEV_NCM811": 227, "HPEV_NCA": 278,
}

# Estimated battery capacity
estimated_battery_capacity = {
    'BPEV_LFP': 50 * uniform(0.6, 0.8),
    'BPEV_NCM111': 42 * uniform(0.6, 0.8),
    'BPEV_NCM523': 40.5 * uniform(0.6, 0.8),
    'BPEV_NCM622': 54 * uniform(0.6, 0.8),
    'BPEV_NCM811': 78 * uniform(0.6, 0.8),
    'BPEV_NCA': 75 * uniform(0.6, 0.8),
    'HPEV_LFP': 15 * uniform(0.6, 0.8),
    'HPEV_NCM111': 20 * uniform(0.6, 0.8),
    'HPEV_NCM523': 18 * uniform(0.6, 0.8),
    'HPEV_NCM622': 35 * uniform(0.6, 0.8),
    'HPEV_NCM811': 40 * uniform(0.6, 0.8),
    'HPEV_NCA': 15 * uniform(0.6, 0.8),
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
                    sales_in_year = city_sales[city_sales['Year'] == sales_year]['PEV_number'].sum()
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
results_df.to_excel('./output data_prediction/TP_EOL power battery from PEV.xlsx', index=False)

print("City retired battery count and energy calculation completed. Results have been saved to an Excel file.")