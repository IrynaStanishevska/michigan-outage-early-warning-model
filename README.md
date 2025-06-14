## Early-Warning Model for Large-Scale Power-Outages in Michigan 
### Master's Thesis - Code and Pipelines

This repository contains the code and data pipelines used in my master's thesis, which develops a 48-hour early-warning model for weather-driven large-scale outages (more than 50,000 customers) in Michigan. The project uses entirely open-source EAGLE-I outage records, METAR airport data, U.S. Census population density, and GIS layers. 

1. Project Structure

- spatial_interpolation/
  - kriging (scikit‑gstat + PyKrige)
  - relative humidity gradient computation
  - point‑in‑polygon flags

- features/
  - metar data aggregation
  - data preprocessing
  - feature engineering
    
- modeling/
   - Two-Stage Model
   - One-Step LSMT (Baseline) for comparison

- metrics/
    - Conditional MASE

- docs/ Interactive Visualizations available below

  2. Pipeline:

  1. Data preprocessing (cleaning, hourly aggregation, spatial interpolation for METAR observations)
  2. Feature engineering (lags, rolling stats, inverse-distance wighting, population density)
  3. Two-Stage Model
     - Stage-1 - Logistic Regression Classifier (identifies anomaly outage in 48h == class 1)
     - Stage-2 - LSTM Regression (defines outage magnitude sum_48)
  4. Baseline
     - one-step LSTM regressor trained on the same feature set.
  5. Evaluarion
      - standard metrics (MSE, RMSE, MAE, R2)
      - conditional MASE computed only on peak values
  6. Visualization dashbords (interactive plotly)

      [48-Hour Predict vs. Grounnd Truth, Test 2022](https://irynastanishevska.github.io/michigan-outage-early-warning-model/plot_48h_predict_vs_actual.html)
     
      [24-Hour Lead Peacks vs. Ground Truth](https://irynastanishevska.github.io/michigan-outage-early-warning-model/plot_24h_lead_peaks_vs_actual.html)


