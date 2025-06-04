<h1 style="text-align: center;">Foodwaste forecasting and recommendation</h1>

Latest model and data tag version: `May_26`

# 1. Transform data

Visit [Transform data tutorial](src/transform_data/README.md) for more information and how to run notebooks

# 2. Forecasting

There are 3 forecasting models. Each of the following trains and stores trained model in `trained_models/`. To execute any of the following, processed data must be available via running notebook in [1. Transform data](#1.-transform-data).

- Forecast POS of whole restaurant: `src/whole_restaurant_waste_forecast/forecast.ipynb`
- Forecast POS of each meal per restaurant: `src/per_meal_pos_forecast/idea9_May14.ipynb`
- Forecast waste of whole restaurant: `src/whole_restaurant_waste_forecast/forecast.ipynb`

# 3. Recommend menus

Notebook `src/recommend_menus/recommend_menus.ipynb` is experiment. To create file containing crafted menu for specific restaurant in specific period, run the following:

```bash
python -m src.recommend_menus.recommend_menus --restaurant <restaurant_id> --date_start <date_start> --date_end <date_end>
```

Example:

```bash
python -m src.recommend_menus.recommend_menus --restaurant 1 --date_start 2025-06-02 --date_end 2025-08-31
```
