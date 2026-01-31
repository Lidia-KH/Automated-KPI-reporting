# Assuming Revenue is defined as the sum of total_price per day.
# Negative values are included (refunds).
from src.config import TIME_GRAIN, INCLUDE_NEGATIVE_AMOUNTS

def calculate_revenue(df):
    df_copy = df.copy()
    
    if not INCLUDE_NEGATIVE_AMOUNTS:
        df_copy = df_copy[df_copy['quantity']>=0]
    
    df_revenue = (
        df_copy
        .set_index('invoicedate')
        .resample(TIME_GRAIN)['price']
        .sum()
        .reset_index()
        .rename(columns={'price':'revenue'})
    )
    return df_revenue