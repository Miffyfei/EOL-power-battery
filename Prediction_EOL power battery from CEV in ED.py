import numpy as np
from random import uniform
import pandas as pd
from scipy.stats import weibull_min

# Load passenger vehicle data
file_path_passenger = './output data_prediction/CEV_Predictions_results.xlsx'

# Load data
passenger_data = pd.read_excel(file_path_passenger)

# Ensure "Year" column is integer type
passenger_data['Year'] = passenger_data['Year'].astype(int)
passenger_data.rename(columns={'Year': 'Year', 'City': 'City'}, inplace=True)

# Vehicle proportion (20 types, by year), sum to 1
years = list(range(2016, 2031))
vehicle_proportion = pd.DataFrame({
    'BCEV_LFP': [
        0.543065476, 0.355647668, 0.29184876, 0.251713961, 0.288924559,
        0.4394, 0.49042, 0.49781, 0.49781, 0.49781, 0.49781, 0.49781, 0.49781, 0.49781, 0.49781
    ],
    'BCEV_NCM111': [
        0.028836012, 0.054317098, 0.036518511, 0.016046765, 0.020545746,
        0.006929, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ],
    'BCEV_NCM523': [
        0.168579762, 0.33495544, 0.301277719, 0.336982066, 0.27223114,
        0.174408, 0.0791, 0.03715, 0.03715, 0.03715, 0.03715, 0.03715, 0.03715, 0.03715, 0.03715
    ],
    'BCEV_NCM622': [
        0.022181548, 0.058843523, 0.082166651, 0.101629512, 0.102728732,
        0.068952, 0.07119, 0.05944, 0.05944, 0.05944, 0.05944, 0.05944, 0.05944, 0.05944, 0.05944
    ],
    'BCEV_NCM811': [
        0.001109077, 0.002263212, 0.018259256, 0.058838138, 0.113001605,
        0.146016, 0.14238, 0.14117, 0.14117, 0.14117, 0.14117, 0.14117, 0.14117, 0.14117, 0.14117
    ],
    'BCEV_NCA': [
        0.001109077, 0.002263212, 0.018259256, 0.021395687, 0.005136437,
        0.009295, 0.00791, 0.00743, 0.00743, 0.00743, 0.00743, 0.00743, 0.00743, 0.00743, 0.00743
    ],
    'HCEV_LFP': [
        0.166934524, 0.084352332, 0.09815124, 0.068286039, 0.071075441,
        0.0806, 0.12958, 0.17219, 0.17219, 0.17219, 0.17219, 0.17219, 0.17219, 0.17219, 0.17219
    ],
    'HCEV_NCM111': [
        0.008863988, 0.012882902, 0.012281489, 0.004353235, 0.005054254,
        0.001271, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ],
    'HCEV_NCM523': [
        0.051820238, 0.07944456, 0.101322281, 0.091417934, 0.06696886,
        0.031992, 0.0209, 0.01285, 0.01285, 0.01285, 0.01285, 0.01285, 0.01285, 0.01285, 0.01285
    ],
    'HCEV_NCM622': [
        0.006818452, 0.013956477, 0.027633349, 0.027570488, 0.025271268,
        0.012648, 0.01881, 0.02056, 0.02056, 0.02056, 0.02056, 0.02056, 0.02056, 0.02056, 0.02056
    ],
    'HCEV_NCM811': [
        0.000340923, 0.000536788, 0.006140744, 0.015961862, 0.027798395,
        0.026784, 0.03762, 0.04883, 0.04883, 0.04883, 0.04883, 0.04883, 0.04883, 0.04883, 0.04883
    ],
    'HCEV_NCA': [
        0.000340923, 0.000536788, 0.006140744, 0.005804313, 0.001263563,
        0.001705, 0.00209, 0.00257, 0.00257, 0.00257, 0.00257, 0.00257, 0.00257, 0.00257, 0.00257
    ]
}, index=years)

weibull_params = {
    'BCEV_LFP': {'shape': 3.5, 'scale': 9},
    'BCEV_NCM111': {'shape': 3.5, 'scale': 8},
    'BCEV_NCM523': {'shape': 3.5, 'scale': 9},
    'BCEV_NCM622': {'shape': 3.5, 'scale': 10},
    'BCEV_NCM811': {'shape': 3.5, 'scale': 10.5},
    'BCEV_NCA': {'shape': 3.5, 'scale': 11},
    'HCEV_LFP': {'shape': 3.5, 'scale': 10.5},
    'HCEV_NCM111': {'shape': 3.5, 'scale': 9.5},
    'HCEV_NCM523': {'shape': 3.5, 'scale': 10.5},
    'HCEV_NCM622': {'shape': 3.5, 'scale': 11.5},
    'HCEV_NCM811': {'shape': 3.5, 'scale': 12},
    'HCEV_NCA': {'shape': 3.5, 'scale': 12.5},
}

# Battery weight ranges (based on average)
battery_weights = {
    "BCEV_LFP": 350, "BCEV_NCM111": 349, "BCEV_NCM523": 303, "BCEV_NCM622": 305,
    "BCEV_NCM811": 479, "BCEV_NCA": 208, "HCEV_LFP": 357, "HCEV_NCM111": 333,
    "HCEV_NCM523": 278, "HCEV_NCM622": 250, "HCEV_NCM811": 227, "HCEV_NCA": 278,
}
# Estimated battery capacity
original_estimated_battery_capacity = {
    'BCEV_LFP': 50 * uniform(0.6, 0.8),
    'BCEV_NCM111': 42 * uniform(0.6, 0.8),
    'BCEV_NCM523': 40.5 * uniform(0.6, 0.8),
    'BCEV_NCM622': 54 * uniform(0.6, 0.8),
    'BCEV_NCM811': 78 * uniform(0.6, 0.8),
    'BCEV_NCA': 75 * uniform(0.6, 0.8),
    'HCEV_LFP': 15 * uniform(0.6, 0.8),
    'HCEV_NCM111': 20 * uniform(0.6, 0.8),
    'HCEV_NCM523': 18 * uniform(0.6, 0.8),
    'HCEV_NCM622': 35 * uniform(0.6, 0.8),
    'HCEV_NCM811': 40 * uniform(0.6, 0.8),
    'HCEV_NCA': 15 * uniform(0.6, 0.8),
}


# Calculate Weibull distribution retirement probability
def calculate_weibull_retirement(sales_year, current_year, shape, scale):
    if current_year <= sales_year:
        return 0
    age = current_year - sales_year
    return weibull_min.cdf(age, shape, scale=scale)


# Increase energy density to 1.1 times
energy_density_factor = 1.03


# Dynamically calculate energy density factor based on year
def get_energy_density_factor(year):
    if year <= 2023:
        return 1
    else:
        return 1 * (1.03 ** (year - 2023))


# Select capacity and weight based on year
def get_battery_parameters(year):
    if year <= 2023:
        return original_estimated_battery_capacity, battery_weights
    else:
        current_energy_density_factor = get_energy_density_factor(year)
        adjusted_estimated_battery_capacity = {
            'BCEV_LFP': 50 * uniform(0.7, 0.8) * current_energy_density_factor,
            'BCEV_NCM111': 42 * uniform(0.7, 0.8) * current_energy_density_factor,
            'BCEV_NCM523': 40.5 * uniform(0.7, 0.8) * current_energy_density_factor,
            'BCEV_NCM622': 54 * uniform(0.7, 0.8) * current_energy_density_factor,
            'BCEV_NCM811': 78 * uniform(0.7, 0.8) * current_energy_density_factor,
            'BCEV_NCA': 75 * uniform(0.7, 0.8) * current_energy_density_factor,
            'HCEV_LFP': 15 * uniform(0.7, 0.8) * current_energy_density_factor,
            'HCEV_NCM111': 20 * uniform(0.7, 0.8) * current_energy_density_factor,
            'HCEV_NCM523': 18 * uniform(0.7, 0.8) * current_energy_density_factor,
            'HCEV_NCM622': 35 * uniform(0.7, 0.8) * current_energy_density_factor,
            'HCEV_NCM811': 40 * uniform(0.7, 0.8) * current_energy_density_factor,
            'HCEV_NCA': 15 * uniform(0.7, 0.8) * current_energy_density_factor,
        }
        adjusted_battery_weights = {
            "BCEV_LFP": 350 * uniform(0.95, 1.05),
            "BCEV_NCM111": 349 * uniform(0.95, 1.05),
            "BCEV_NCM523": 303 * uniform(0.95, 1.05),
            "BCEV_NCM622": 305 * uniform(0.95, 1.05),
            "BCEV_NCM811": 479 * uniform(0.95, 1.05),
            "BCEV_NCA": 208 * uniform(0.95, 1.05),
            "HCEV_LFP": 357 * uniform(0.95, 1.05),
            "HCEV_NCM111": 333 * uniform(0.95, 1.05),
            "HCEV_NCM523": 278 * uniform(0.95, 1.05),
            "HCEV_NCM622": 250 * uniform(0.95, 1.05),
            "HCEV_NCM811": 227 * uniform(0.95, 1.05),
            "HCEV_NCA": 278 * uniform(0.95, 1.05),
        }
        return adjusted_estimated_battery_capacity, adjusted_battery_weights


# Calculate retired batteries and energy for each city per year
def calculate_retired_batteries_and_energy(city_data, years, vehicle_prop, weibull_params):
    city_retired_batteries = {}

    for city in city_data['City'].unique():
        city_sales = city_data[city_data['City'] == city]

        city_retired_batteries[city] = {}

        for year in years:
            sales_in_year = city_sales[city_sales['Year'] == year]['CEV_number'].sum()

            # Ensure result includes even zero sales
            if pd.isna(sales_in_year):
                sales_in_year = 0

            estimated_battery_capacity, battery_weights = get_battery_parameters(year)

            # Calculate retired battery count and capacity for each model
            for model in vehicle_prop.columns:
                model_weight = battery_weights[model]
                model_proportion = vehicle_prop[model].loc[year]
                weibull_dist_params = weibull_params[model]
                retired_battery_count = sum(
                    city_sales[city_sales['Year'] == sales_year]['CEV_number'].sum() *
                    calculate_weibull_retirement(sales_year, year, weibull_dist_params['shape'],
                                                 weibull_dist_params['scale'])
                    for sales_year in city_sales['Year'].unique()
                ) * model_proportion

                retired_battery_weight = retired_battery_count * model_weight
                retired_battery_capacity = retired_battery_count * estimated_battery_capacity[
                    model] / 1e6  # Convert to MWh

                if year not in city_retired_batteries[city]:
                    city_retired_batteries[city][year] = {}

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
    retired_data = calculate_retired_batteries_and_energy(city_data, years, vehicle_proportion, weibull_params)
    for year in years:
        if year in retired_data[city]:
            for model, data in retired_data[city][year].items():
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
results_df.to_excel('./output data_prediction/ED_EOL power battery from CEV.xlsx', index=False)

print("Retired battery count and energy calculation completed. Results have been saved to an Excel file.")


# Sensitivity analysis function
def sensitivity_analysis(city_data, years, vehicle_prop, weibull_params, energy_density_factors):
    sensitivity_results = []

    for factor in energy_density_factors:
        # Modify energy density factor
        def get_energy_density_factor(year):
            if year <= 2023:
                return 1
            else:
                return 1 * (factor ** (year - 2023))

        # Calculate retired battery count and capacity
        retired_data = calculate_retired_batteries_and_energy(city_data, years, vehicle_prop, weibull_params)

        for city in retired_data.keys():
            for year in retired_data[city].keys():
                for model, data in retired_data[city][year].items():
                    sensitivity_results.append({
                        'Energy Density Factor': factor,
                        'City': city,
                        'Year': year,
                        'Battery type': model,
                        'Weight (thousand t)': data['retired_battery_weight'] / 1000000,  # Convert to thousand tons
                        'Capacity (GWh)': data['retired_battery_capacity']
                    })

    return sensitivity_results


# Set different energy density factors for sensitivity analysis
energy_density_factors = [1.01, 1.02, 1.03, 1.04, 1.05]
sensitivity_results = sensitivity_analysis(passenger_data, years, vehicle_proportion, weibull_params,
                                           energy_density_factors)

# Convert to DataFrame
sensitivity_results_df = pd.DataFrame(sensitivity_results)

# Save sensitivity analysis results to Excel file, with each factor as a sheet
with pd.ExcelWriter('./sensitivity analysis results/ED_CEV_sensitivity analysis results.xlsx') as writer:
    for factor in energy_density_factors:
        factor_df = sensitivity_results_df[sensitivity_results_df['Energy Density Factor'] == factor]
        factor_df.to_excel(writer, sheet_name=f'Factor_{factor}', index=False)

print("Sensitivity analysis completed. Results have been saved to an Excel file.")
