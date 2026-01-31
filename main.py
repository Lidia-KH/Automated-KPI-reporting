from fastapi import FastAPI
from fastapi.security import HTTPBearer
from src.ingestion import load_csv
from src.validation import validate
from src.metrics import calculate_revenue
from src.config import TIME_GRAIN
from src.reporting import export_csv, plot_revenue

app = FastAPI(
    title="Automated KPI reporting",
    version="1.0.0"
)

bearer_scheme = HTTPBearer()

app.openapi_schema = None

if __name__ == "__main__" :
    df = load_csv("/home/lidia/windowsBackup/Documents/automated_kpi_reporting/data/raw/online_retail_II.csv")
    df = validate(df)
    df_revenue = calculate_revenue(df)
    # print(f"Computing revenue by {TIME_GRAIN} ...")
    # print(df_revenue)

    export_csv(df_revenue, "outputs/report.csv")
    plot_revenue(df_revenue, "outputs/plots.png")

    print("Report generated successfully !")
