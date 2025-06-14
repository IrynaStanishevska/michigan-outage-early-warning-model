README

This repository contains the code and data pipelines used in my master's thesis, which focuses on forecasting the large-scaled summer outages in Michigan using open source EAGLE-I records and wether and population features. The objective of this project is to build an early-warning model that predicts weather-induced large-scale outages (more than 50,000 customers) 48 hours in advance. The project includes:

- Data prerocessing (outage, weather, population datasets)
- Feature engineering (lags, rolling statistics, IDW)
- Two-Stage Model
    - Stage-1 - Logistic Regression Classifier (anomaly outage in 48h == class 1)
    - Stage-2 - LSTM Regression (defines outage magnitude)
 
- One-Step LSMT (Baseline) for comparison
- Evaluation with  MSE, RMSE, MAE, and R² standard metrics and Conditional MASE (conditional_mase) on high peaks
a Two-Stage LSTM (classification-regression) and a One-Step LSTM baseline. 
- Interactive Visualizations of prediction include: 

1. [48-Hour Predict vs. Grounnd Truth, Test 2022] (https://irynastanishevska.github.io/michigan-outage-early-warning-model/plot_48h_predict_vs_actual.html)
2. [24-Hour Lead Peacks vs. Ground Truth] (https://irynastanishevska.github.io/michigan-outage-early-warning-model/plot_24h_lead_peaks_vs_actual.html)

