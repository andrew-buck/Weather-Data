from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import logging
import os
import numpy as np
import joblib
import json
from datetime import datetime, timedelta
# Add imports for model evaluation and tuning
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit  # Changed to RandomizedSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# Create necessary directories
os.makedirs('./logging', exist_ok=True)
os.makedirs('./models', exist_ok=True)
os.makedirs('./model_evaluation', exist_ok=True)  # New directory for evaluation results
logging.basicConfig(filename='./logging/logging.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("my_logger")

# Add a flag to control evaluation intensity
FAST_MODE = True  # Set to False for full evaluation

# Load your weather data
weather_df = pd.DataFrame()
try:
    # Use SQLAlchemy to connect to the database
    engine = create_engine(f'sqlite:///{"weather.db"}')
    
    # Query all numeric columns for potential use in the models
    column_list = """
    location, min_temp, max_temp, rainfall, evaporation, sunshine, 
    wind_gust_speed, windspeed9am, windspeed3pm, humidity9am, humidity3pm, 
    pressure9am, pressure3pm, cloud9am, cloud3pm, 
    temp9am, temp3pm, rain_tomorrow
    """
    weather_df = pd.read_sql(f'SELECT {column_list} FROM weather', engine)

    # Update your column mapping to match the actual database column names
    column_mapping = {
        'location': 'Location',
        'min_temp': 'MinTemp',
        'max_temp': 'MaxTemp',
        'rainfall': 'Rainfall',
        'evaporation': 'Evaporation',
        'sunshine': 'Sunshine',
        'wind_gust_speed': 'WindGustSpeed',
        'windspeed9am': 'WindSpeed9am',
        'windspeed3pm': 'WindSpeed3pm',
        'humidity9am': 'Humidity9am',
        'humidity3pm': 'Humidity3pm',
        'pressure9am': 'Pressure9am',
        'pressure3pm': 'Pressure3pm',
        'cloud9am': 'Cloud9am',
        'cloud3pm': 'Cloud3pm',
        'temp9am': 'Temp9am',
        'temp3pm': 'Temp3pm',
        'rain_tomorrow': 'RainTomorrow'
    }
    
    # Rename columns as needed
    for old_name, new_name in column_mapping.items():
        if old_name in weather_df.columns:
            weather_df = weather_df.rename(columns={old_name: new_name})
except sqlite3.Error as e:
    logger.error(f"SQLite error: {e}")
except Exception as e:
    logger.error(f"Error reading from database: {e}")


# Get unique location values
locations = weather_df['Location'].unique()

# Dictionary to store DataFrames for each location
location_dfs = {}

# Dictionary to store columns available for each location after filtering
location_columns = {}

threshold = 30.0
# Split the data by location and store in dictionary
for location in locations:
    # Filter data for this location
    location_dfs[location] = weather_df[weather_df['Location'] == location].copy()
    
    # Remove the Location column since it's now redundant
    location_dfs[location] = location_dfs[location].drop(columns=['Location'])
    
    # Handle missing values by dropping columns if more than threshold% of the data is missing
    missing_percentage = location_dfs[location].isna().mean() * 100
    columns_to_drop = missing_percentage[missing_percentage > threshold].index.tolist()
    location_dfs[location] = location_dfs[location].drop(columns=columns_to_drop)
    
    # Fill missing values with linear interpolation
    location_dfs[location] = location_dfs[location].interpolate(method='linear')
    
    # Store the columns available for this location after filtering
    location_columns[location] = location_dfs[location].columns.tolist()
    
    print(f"Created DataFrame for {location} with {len(location_dfs[location])} rows and {len(location_columns[location])} columns")
    
    # Print which columns were dropped due to missing data
    all_possible_cols = set(weather_df.columns) - {'Location'}
    dropped_cols = all_possible_cols - set(location_columns[location])
    if dropped_cols:
        print(f"  Columns dropped for {location} due to missing data: {', '.join(dropped_cols)}")

# Initialize metadata dictionary
model_metadata = {}

# Train multivariate models for each location
for location, df in location_dfs.items():
    print(f"\nTraining multivariate model for {location}...")
    
    # Get all model features (excluding target variable if present)
    all_cols = location_columns[location].copy()
    if 'RainTomorrow' in all_cols:
        all_cols.remove('RainTomorrow')
    
    # Skip location if not enough columns remain after filtering
    if len(all_cols) < 2:
        print(f"  WARNING: Not enough columns for {location} after filtering. Skipping.")
        continue
    
    # Create model metadata entry with evaluation metrics section
    model_metadata[location] = {
        'available_columns': all_cols,
        'db_column_mapping': {col: next((k for k, v in column_mapping.items() if v == col), None) for col in all_cols},
        'n_lags': 14,  # Use 14 days of history
        'model_path': f'./models/multivariate_{location}.joblib',
        'train_stats': {
            col: {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max())
            } for col in all_cols
        },
        'eval_metrics': {},  # Will store evaluation metrics
        'hyperparameters': {}  # Will store best hyperparameters
    }
    
    # Prepare data for multivariate forecasting using 14 days of history
    n_lags = 14
    X_multi = []
    y_multi = []
    
    # For each possible window in the dataset
    for i in range(n_lags, len(df)):
        # Get the window of 14 days for all features
        window_data = df[all_cols].iloc[i-n_lags:i].values.flatten()
        
        # The target is the next day's values for all features
        target = df[all_cols].iloc[i].values
        
        X_multi.append(window_data)
        y_multi.append(target)
    
    # Convert to numpy arrays
    X_multi = np.array(X_multi)
    y_multi = np.array(y_multi)
    
    print(f"  Training on {len(X_multi)} samples with {X_multi.shape[1]} features to predict {len(all_cols)} outputs")
    print(f"  Using columns: {', '.join(all_cols)}")
    
    try:
        # Define time series cross-validation with fewer splits in fast mode
        tscv = TimeSeriesSplit(n_splits=3 if FAST_MODE else 5)
        
        # Define parameter grid for hyperparameter tuning - reduced in fast mode
        if FAST_MODE:
            param_grid = {
                'n_estimators': [50, 100],
                'max_depth': [10, 20],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2]
            }
            # Number of iterations for RandomizedSearchCV
            n_iter_search = 5
        else:
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            # Number of iterations for RandomizedSearchCV
            n_iter_search = 10
        
        print(f"  Performing hyperparameter tuning with RandomizedSearchCV...")
        
        # Initialize the base model
        base_model = RandomForestRegressor(random_state=42, n_jobs=-1)
        
        # Use RandomizedSearchCV instead of GridSearchCV - much faster
        search = RandomizedSearchCV(
            estimator=base_model,
            param_distributions=param_grid,
            cv=tscv,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=0,
            n_iter=n_iter_search
        )
        
        # Fit RandomizedSearchCV
        search.fit(X_multi, y_multi)
        
        # Get best parameters and model
        best_params = search.best_params_
        best_model = search.best_estimator_
        
        print(f"  Best parameters: {best_params}")
        
        # Store hyperparameters in metadata
        model_metadata[location]['hyperparameters'] = best_params
        
        # Evaluate model using cross-validation
        print(f"  Evaluating model with time series cross-validation...")
        
        # Initialize metrics dictionaries
        metrics = {
            'rmse': [],
            'mae': [],
            'r2': []
        }
        
        # Perform time series cross-validation for evaluation
        for train_idx, test_idx in tscv.split(X_multi):
            X_train, X_test = X_multi[train_idx], X_multi[test_idx]
            y_train, y_test = y_multi[train_idx], y_multi[test_idx]
            
            # Fit model on training set
            best_model.fit(X_train, y_train)
            
            # Predict on test set
            y_pred = best_model.predict(X_test)
            
            # Calculate metrics for each target variable
            for i, col in enumerate(all_cols):
                y_test_col = y_test[:, i]
                y_pred_col = y_pred[:, i]
                
                # Calculate metrics
                rmse = np.sqrt(mean_squared_error(y_test_col, y_pred_col))
                mae = mean_absolute_error(y_test_col, y_pred_col)
                r2 = r2_score(y_test_col, y_pred_col)
                
                # Store metrics by column
                if col not in metrics:
                    metrics[col] = {'rmse': [], 'mae': [], 'r2': []}
                
                metrics[col]['rmse'].append(rmse)
                metrics[col]['mae'].append(mae)
                metrics[col]['r2'].append(r2)
        
        # Calculate average metrics across folds
        avg_metrics = {}
        for col in metrics:
            if col in ['rmse', 'mae', 'r2']:
                continue
                
            avg_metrics[col] = {
                'rmse': float(np.mean(metrics[col]['rmse'])),
                'mae': float(np.mean(metrics[col]['mae'])),
                'r2': float(np.mean(metrics[col]['r2']))
            }
            
            # Print metrics for each column
            print(f"  Metrics for {col}:")
            print(f"    RMSE: {avg_metrics[col]['rmse']:.4f}")
            print(f"    MAE: {avg_metrics[col]['mae']:.4f}")
            print(f"    R²: {avg_metrics[col]['r2']:.4f}")
        
        # Store metrics in metadata
        model_metadata[location]['eval_metrics'] = avg_metrics
        
        # Fit final model on all data using best parameters
        final_model = RandomForestRegressor(**best_params, random_state=42, n_jobs=-1)
        final_model.fit(X_multi, y_multi)
        
        # Create visualization of feature importance - skip in fast mode or make it smaller
        if FAST_MODE:
            plt.figure(figsize=(8, 6))
        else:
            plt.figure(figsize=(12, 8))
        
        # Get feature importance
        importances = final_model.feature_importances_
        
        # The features are repeated for each lag, so we need to aggregate them
        n_features = len(all_cols)
        n_lags_used = X_multi.shape[1] // n_features
        
        # Reshape importances to (n_lags, n_features)
        importances_reshaped = importances.reshape(n_lags_used, n_features)
        
        # Sum importance across lags for each feature
        feature_importances = importances_reshaped.sum(axis=0)
        
        # Create indices for sorting
        indices = np.argsort(feature_importances)
        
        # Plot feature importance
        plt.barh(range(len(indices)), feature_importances[indices])
        plt.yticks(range(len(indices)), [all_cols[i] for i in indices])
        plt.xlabel('Feature Importance')
        plt.title(f'Feature Importance for {location}')
        
        # Save plot with lower DPI in fast mode
        plt.tight_layout()
        feature_imp_path = f'./model_evaluation/{location}_feature_importance.png'
        plt.savefig(feature_imp_path, dpi=100 if FAST_MODE else 300)
        plt.close()
        
        # Save model evaluation results
        eval_results = {
            'location': location,
            'metrics': avg_metrics,
            'best_parameters': best_params,
            'n_samples': len(X_multi),
            'feature_importance': {all_cols[i]: float(feature_importances[i]) for i in range(len(all_cols))},
            'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model_path': model_metadata[location]['model_path']
        }
        
        # Save evaluation results to JSON
        eval_path = f'./model_evaluation/{location}_evaluation.json'
        with open(eval_path, 'w') as f:
            json.dump(eval_results, f, indent=4)
        
        print(f"  Model evaluation results saved to {eval_path}")
        print(f"  Feature importance plot saved to {feature_imp_path}")
        
        # Save the final model
        joblib.dump(final_model, model_metadata[location]['model_path'])
        print(f"  Model saved to {model_metadata[location]['model_path']}")
        
    except Exception as e:
        logger.error(f"Error training multivariate model for {location}: {e}")
        print(f"  Error: {e}")

# Save the model metadata to a JSON file
with open('./models/multivariate_model_metadata.json', 'w') as f:
    json.dump(model_metadata, f, indent=2)

# Create a separate utility file for the forecaster class
print("\nMultivariate model training complete!")
print(f"Created models for {len(model_metadata)} locations.")
print("All models are saved in the 'models' directory in .joblib format.")
print("Model metadata is saved to 'models/multivariate_model_metadata.json'.")
print("Use the separate multivariate_forecaster.py file to generate forecasts.")