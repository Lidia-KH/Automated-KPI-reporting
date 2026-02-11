import pandas as pd

required_fields = {"price", "quantity", "invoicedate", "customer_id"}

def validate(df):
    for col in required_fields:
        if col in df.columns:
            print("The required column is present")
        else:
            raise Exception("The required column does not exist")
    
    col_missing_values = len(df) - len(df.dropna())
    print(f"The number of rows with missing values to be dropped is : {col_missing_values}")

    duplicates = df.duplicated().sum()
    df.drop_duplicates(inplace=True)
    print(f"The number of rows duplicated to be dropped is : {duplicates}")

    negative_quantity = (df["quantity"] < 0).sum()
    print(f"Number of negative quantity : {negative_quantity}")

    df['total_price'] = df['price'] * df['quantity']
    # df.drop(columns=['Price'])
    df['invoicedate'] = pd.to_datetime(df['invoicedate'])

    return df