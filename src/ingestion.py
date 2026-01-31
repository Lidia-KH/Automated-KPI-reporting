import pandas as pd


def load_csv(path):
    df = pd.read_csv(path)
    df['Total Price'] = df['Price'] * df['Quantity']
    df.drop(columns=['Price'])
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])


    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    print(df.shape)
    print(df)
    return df