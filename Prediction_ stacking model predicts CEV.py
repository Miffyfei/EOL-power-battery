import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from mlxtend.regressor import StackingCVRegressor

# Load data
data = pd.read_excel('./input data/2016-2030_CEV_data.xlsx', sheet_name='Sheet1')

# Select features for training
features = ['total_GDP', 'Urbanization_rate', 'SumBaidu', 'people', 'Urban_population', 'CEV_Subsidy funds']
target = 'CEV_number'

# Prepare training set (data from 2017 to 2023)
train_data = data[data['Year'] <= 2023]
X_train = train_data[features].values
y_train = train_data[target].values

# Data standardization
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Create stacking regression model
regressors = [
    RandomForestRegressor(n_estimators=100, random_state=42),
    GradientBoostingRegressor(n_estimators=100, random_state=42)
]
stack_gen = StackingCVRegressor(regressors=regressors,
                                meta_regressor=LinearRegression(),
                                use_features_in_secondary=True,
                                cv=5,
                                n_jobs=-1)

# Evaluate model using cross-validation
cv_scores = cross_val_score(stack_gen, X_train_scaled, y_train, cv=5, scoring='neg_mean_squared_error')
mse_scores = -cv_scores
rmse_scores = mse_scores ** 0.5

# Train the model
stack_gen.fit(X_train_scaled, y_train)

test_data = data[data['Year'] > 2023].copy()
X_test = test_data[features].values
X_test_scaled = scaler.transform(X_test)
predictions = stack_gen.predict(X_test_scaled)

# Set predicted values less than 0 to 0
predictions = [max(0, pred) for pred in predictions]

# Add predictions to the original data
test_data.loc[:, 'Predicted_CEV_number'] = predictions

# Combine actual values and predictions
full_data = pd.concat([train_data, test_data], axis=0, sort=False)
0
# Output results to Excel
full_data.to_excel('./output data_prediction/CEV_Predictions_results.xlsx', index=False)
