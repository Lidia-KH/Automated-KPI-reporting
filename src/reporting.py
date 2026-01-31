import matplotlib.pyplot as plt

def export_csv(df, path):
    df.to_csv(path, index=False)

def plot_revenue(df, path):
    plt.figure()
    plt.plot(df['invoicedate'], df['revenue'])
    plt.xlabel("Invoice Date")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.title("Revenue by invoice date")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

