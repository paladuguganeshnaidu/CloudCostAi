# CloudCostAI Model Diagnostic Report

## Summary
- The inference pipeline now uses the same preprocessing and feature-generation logic as training.
- Negative predictions are clipped to zero only when the trained model produces them, with a warning logged.
- The app validates input ranges and rejects impossible dates and values before prediction.

## Sample Evaluation
The following checks were executed on the available dataset:
- Sample size: 20 rows
- Minimum prediction: 0.0
- Maximum prediction: 345252.7483495633
- Negative predictions: 0

## Notes
- Training uses a LinearRegression model from scikit-learn.
- Feature engineering creates Usage Duration (Hours) and Total Network Traffic to match the training feature contract.
- Categorical fields are encoded through a ColumnTransformer with OneHotEncoder and numerical values are standardized via StandardScaler.
