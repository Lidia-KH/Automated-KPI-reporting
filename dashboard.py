import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
from io import BytesIO
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="KPI Revenue Dashboard",
    page_icon="📊",
    layout="wide"
)

def check_password():
    if st.session_state.get("authenticated"):
        return True
    
    st.title("📊 Automated KPI Revenue Dashboard")
    st.markdown("Please Enter The Password To Access The App.")

    pwd = st.text_input("Password", placeholder="Enter password ...", type="password")

    if pwd:
        if pwd == st.secrets["APP_PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect Password ! Please Try Again.")
    return False

if not check_password():
    st.stop()
        


try:
    from src.ingestion import load_csv
    from src.validation import validate
    from src.metrics import calculate_revenue
    from src.config import TIME_GRAIN
    from src.reporting import export_csv, plot_revenue
    FUNCTIONS_AVAILABLE = True
except ImportError:
    FUNCTIONS_AVAILABLE = False
    st.warning("Could not import project functions. Make sure this file is in the project root.")



# Title and description
st.title("📊 Automated KPI Revenue Dashboard")
st.markdown("Upload your CSV file and select reporting period to analyze revenue trends")

# Sidebar for controls
with st.sidebar:
    st.header("Controls")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=['csv'],
        help="Upload your retail data CSV file"
    )
    
    # Date aggregation selection
    aggregation = st.selectbox(
        "Select Reporting Period (TIME_GRAIN)",
        options=['D', 'W', 'M', 'Y', 'H', 'MIN', 'S'],
        format_func=lambda x: {'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly', 'Y': 'Yearly', 'H':'Hourly', 'MIN':'Every Minutle', 'S':'Every Second'}[x],
        index=2,  # Default to Monthly
        help="This sets the TIME_GRAIN configuration"
    )
    
    st.divider()
    st.markdown("### Data Processing Pipeline:")
    st.code("""
1. Load CSV (ingestion)
2. Validate data
3. Calculate revenue metrics
4. Generate report & plot
    """)

# Main content
if uploaded_file is not None and FUNCTIONS_AVAILABLE:
    try:
        
        # Save uploaded file temporarily
        temp_path = Path("temp_upload.csv")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # store raw df in session_state
        if "raw_df" not in st.session_state:
            st.session_state.raw_df = load_csv(temp_path)
        
        # Show processing steps
        with st.spinner("Processing data..."):
            # Step 1: Load CSV
            with st.expander("📥 Step 1: Loading CSV", expanded=False):
                df = st.session_state.raw_df
                st.divider()
                st.subheader("Column Mapping")

                columns = df.columns.tolist()

                date_col = st.selectbox("Select Date Column", columns)

                revenue_mode = st.radio(
                    "Revenue Source",
                    ["Use existing revenue column", "Calculate revenue (Quantity x Unit Price)"]
                )

                if revenue_mode == "Use existing revenue column":
                    revenue_col = st.selectbox("Select Revenue Column", columns)
                    

                else:
                    qty = st.selectbox("Select Quantity Column", columns)
                    up = st.selectbox("Select Unit Price Column", columns)
                    

                # df["__date__"] = pd.to_datetime(df[date_col])
                if st.button("Generate Report"):
                    if revenue_mode == "Use existing revenue column":
                        df["__revenue__"] = df[revenue_col]
                    else:
                        df["__revenue__"] = df[qty] * df[up]

                    df = df.rename(columns={
                        "__date__": "invoicedate",
                        "__revenue__": "revenue"
                    })

                    st.success(f"✅ Loaded {len(df)} rows")
                    st.dataframe(df.head(), use_container_width=True)
            
                    # Step 2: Validate
                    with st.expander("✔️ Step 2: Validating Data", expanded=False):
                        df = validate(df)
                        st.success(f"✅ Validation complete: {len(df)} valid rows")
                        st.dataframe(df.head(), use_container_width=True)
                    
                    # Step 3: Calculate Revenue (using selected TIME_GRAIN)
                    with st.expander("💰 Step 3: Calculating Revenue", expanded=False):
                        # Temporarily update the TIME_GRAIN config
                        import src.config as config
                        original_grain = config.TIME_GRAIN
                        config.TIME_GRAIN = aggregation
                        
                        df_revenue = calculate_revenue(df)
                        
                        # Restore original grain
                        config.TIME_GRAIN = original_grain
                        
                        st.success(f"✅ Revenue calculated by {aggregation}")
                        st.dataframe(df_revenue, use_container_width=True)
        
                    # Clean up temp file
                    if temp_path.exists():
                        temp_path.unlink()
                    
                    # Display metrics
                    st.divider()
                    st.subheader("📊 Key Metrics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    # Assuming df_revenue has a 'Revenue' or similar column
                    revenue_col = None
                    for col in df_revenue.columns:
                        if 'revenue' in col.lower():
                            revenue_col = col
                            break
                    
                    if revenue_col:
                        with col1:
                            total_revenue = df_revenue[revenue_col].sum()
                            st.metric("Total Revenue", f"${total_revenue:,.2f}")
                        
                        with col2:
                            avg_revenue = df_revenue[revenue_col].mean()
                            st.metric(f"Avg Revenue", f"${avg_revenue:,.2f}")
                        
                        with col3:
                            max_revenue = df_revenue[revenue_col].max()
                            st.metric("Peak Revenue", f"${max_revenue:,.2f}")
                        
                        with col4:
                            num_periods = len(df_revenue)
                            st.metric(f"Total Periods", num_periods)
                    
                    st.divider()
                    
                    # Create two columns for report and plot
                    col_report, col_plot = st.columns([1, 2])
                    
                    with col_report:
                        st.subheader("📋 Revenue Report")
                        
                        # Display the revenue dataframe
                        st.dataframe(
                            df_revenue,
                            use_container_width=True,
                            height=400
                        )
                        
                        # Export CSV button
                        csv_buffer = BytesIO()
                        df_revenue.to_csv(csv_buffer, index=True)
                        csv_buffer.seek(0)
                        
                        st.download_button(
                            label="📥 Download Report as CSV",
                            data=csv_buffer,
                            file_name=f"revenue_report_{aggregation}.csv",
                            mime="text/csv"
                        )
                    
                    with col_plot:
                        st.subheader("📈 Revenue Trend")
                        
                        # Generate plot using your existing function
                        plot_path = Path("outputs/temp_plot.png")
                        plot_path.parent.mkdir(exist_ok=True)
                        
                        # Update TIME_GRAIN temporarily for plotting
                        import src.config as config
                        original_grain = config.TIME_GRAIN
                        config.TIME_GRAIN = aggregation
                        
                        plot_revenue(df_revenue, str(plot_path))
                        
                        config.TIME_GRAIN = original_grain
                        
                        # Display the plot
                        if plot_path.exists():
                            image = Image.open(plot_path)
                            st.image(image, use_container_width=True)
                            
                            # Offer download
                            with open(plot_path, "rb") as file:
                                st.download_button(
                                    label="📥 Download Plot",
                                    data=file,
                                    file_name=f"revenue_plot_{aggregation}.png",
                                    mime="image/png"
                                )
                            
                            # Clean up
                            plot_path.unlink()
                    
                    # Additional insights
                    st.divider()
                    st.subheader("📊 Additional Insights")
                    
                    if revenue_col:
                        insight_col1, insight_col2, insight_col3 = st.columns(3)
                        
                        with insight_col1:
                            # Growth calculation
                            if len(df_revenue) > 1:
                                first_revenue = df_revenue[revenue_col].iloc[0]
                                last_revenue = df_revenue[revenue_col].iloc[-1]
                                if abs(first_revenue) > 1e-6:
                                    growth = ((last_revenue - first_revenue) / abs(first_revenue)) * 100
                                else:
                                    growth = 0
                                st.metric("Overall Growth", f"{growth:+.2f}%")
                            else:
                                st.metric("Overall Growth", "N/A")
                        
                        with insight_col2:
                            min_revenue = df_revenue[revenue_col].min()
                            st.metric("Lowest Revenue", f"${min_revenue:,.2f}")
                        
                        with insight_col3:
                            median_revenue = df_revenue[revenue_col].median()
                            st.metric("Median Revenue", f"${median_revenue:,.2f}")
                    
                    st.success("✅ Report generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.exception(e)
        
        # Clean up temp file on error
        if Path("temp_upload.csv").exists():
            Path("temp_upload.csv").unlink()

elif not FUNCTIONS_AVAILABLE:
    st.error("❌ Cannot import project functions. Please ensure:")
    st.code("""
1. This file is in your project root directory
2. The 'src' folder is in the same directory
3. All required modules are installed
    """)
    
else:
    # Show instructions when no file is uploaded
    st.info("Please upload a CSV file to get started")
    
    st.markdown("### Project Structure Expected:")