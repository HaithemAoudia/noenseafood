import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import altair as alt
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
from io import BytesIO
from PyPDF2 import PdfMerger
import base64
import json
from gspread_dataframe import set_with_dataframe
import plotly.graph_objects as go
import streamlit_authenticator as stauth
import pickle
from pathlib import Path
import smtplib
from email.message import EmailMessage
import os

print("Hello")

names = ["Chems"]
usernames = ["Noen Seafood"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)


authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    "Neon_Seafood_Analytics",  # no spaces for cookie name
    "abcdef", 
    cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("Username or Password is Incorrect")

if authentication_status is None:
    st.warning("Please enter your username and password")

if authentication_status:

# ========== PAGE CONFIG ==========
    st.set_page_config(
        page_title="NOEN Seafood Analytics",
        page_icon="🐟",
        layout="wide",
        initial_sidebar_state="collapsed"
    )


        # ========== PAGE CONFIG ==========
    st.set_page_config(
        page_title="NOEN Seafood Analytics",
        page_icon="🐟",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

        # ========== API CREDENTIALS ==========
    API_EMAIL = os.getenv('API_EMAIL')
    API_KEY = os.getenv('API_KEY')

    email_sender = os.getenv('EMAIL_SENDER')
    email_password = os.getenv('EMAIL_PASSWORD')

    google_cred = {
    'type': os.getenv('TYPE'),
    'project_id': os.getenv('PROJECT_ID'),
    'private_key_id': os.getenv('PRIVATE_KEY_ID'),
    'private_key': os.getenv('PRIVATE_KEY').replace('\\n', '\n') if os.getenv('PRIVATE_KEY') else None,
    'client_email': os.getenv('CLIENT_EMAIL'),
    'client_id': os.getenv('CLIENT_ID'),
    'auth_uri': os.getenv('AUTH_URI'),
    'token_uri': os.getenv('TOKEN_URI'),
    'auth_provider_x509_cert_url': os.getenv('AUTH_PROVIDER_X509_CERT_URL'),
    'client_x509_cert_url': os.getenv('CLIENT_X509_CERT_URL'),
    'universe_domain': os.getenv('UNIVERSE_DOMAIN'),
}
    st.markdown("""
    <style>
        .stApp {
            background-color: #f0f9ff;
        }
        
        .main {
            background-color: #f0f9ff;
        }
        
        [data-testid="stAppViewContainer"] {
            background-color: #f0f9ff;
        }
        
        [data-testid="stHeader"] {
            background-color: #f0f9ff;
        }
        /* Header styling */
        h1 {
            color: #0c4a6e;
            font-weight: 700;
            padding-bottom: 0.5rem;
        }
        
        h2 {
            color: #075985;
            font-weight: 600;
            padding-top: 1rem;
            padding-bottom: 0.5rem;
        }
        
        h3 {
            color: #0369a1;
            font-weight: 600;
            font-size: 1.2rem;
        }
        
        /* Logo header container */
        .logo-header {
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
            padding: 1.5rem 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(14, 116, 144, 0.1);
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 2px solid #bae6fd;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        
        .logo-image {
            max-height: 120px;
            width: auto;
        }
        
        .company-title {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #0c4a6e 0%, #0891b2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
        }
        
        .tagline {
            color: #0369a1;
            font-size: 0.95rem;
            font-weight: 500;
            margin-top: 0.25rem;
        }
        
        /* Metric cards with light blue theme */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(14, 116, 144, 0.12);
            border: 1px solid #bae6fd;
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            box-shadow: 0 4px 12px rgba(14, 116, 144, 0.2);
            transform: translateY(-2px);
        }
        
        [data-testid="stMetricLabel"] {
            font-weight: 600;
            color: #0369a1;
            font-size: 0.9rem;
        }
        
        [data-testid="stMetricValue"] {
            color: #0c4a6e;
        }
        
        /* Dataframe styling */
        [data-testid="stDataFrame"] {
            border-radius: 0.75rem;
            overflow: hidden;
            border: 1px solid #bae6fd;
        }
        
        /* Filter section */
        .filter-container {
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(14, 116, 144, 0.12);
            margin-bottom: 2rem;
            border: 1px solid #bae6fd;
        }
        
        /* Divider */
        hr {
            margin: 2rem 0;
            border: none;
            border-top: 2px solid #bae6fd;
        }
        
        /* Tab styling with light blue */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
            padding: 1rem 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(14, 116, 144, 0.12);
            border: 1px solid #bae6fd;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            padding: 0 2rem;
            font-weight: 600;
            color: #0369a1;
            border-radius: 0.5rem;
            transition: all 0.2s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e0f2fe;
            color: #0c4a6e;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
            color: white !important;
            box-shadow: 0 2px 4px rgba(8, 145, 178, 0.3);
        }
        
        /* Checkbox styling */
        [data-testid="stCheckbox"] {
            padding: 0.5rem;
        }
        
        /* Button styling with light blue theme */
        .stButton > button {
            font-weight: 600;
            border-radius: 0.5rem;
            padding: 0.5rem 2rem;
            transition: all 0.3s ease;
            background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
            color: white;
            border: none;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(8, 145, 178, 0.3);
            background: linear-gradient(135deg, #0e7490 0%, #0891b2 100%);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f0f9ff 0%, #e0f2fe 100%);
        }
        
        /* Input fields */
        .stTextInput input, .stSelectbox select, .stMultiSelect select {
            border: 1px solid #bae6fd;
            border-radius: 0.5rem;
            transition: all 0.2s ease;
        }
        
        .stTextInput input:focus, .stSelectbox select:focus, .stMultiSelect select:focus {
            border-color: #0891b2;
            box-shadow: 0 0 0 2px rgba(8, 145, 178, 0.2);
        }
        
        /* Success/Info messages */
        .stSuccess {
            background-color: #cffafe;
            border-left: 4px solid #06b6d4;
        }
        
        .stInfo {
            background-color: #e0f2fe;
            border-left: 4px solid #0891b2;
        }
    </style>
    """, unsafe_allow_html=True)
    

    
    # ========== DATA LOADING ==========
    @st.cache_data(ttl=300, show_spinner=False)
    def load_data():
        """Load and cache data from Google Sheets"""
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(google_cred, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet_id = os.getenv('SHEET_ID')
        workbook = client.open_by_key(sheet_id)
        
        df_sales = pd.DataFrame(workbook.worksheet("OneUp - Invoices").get_all_records()).drop_duplicates()
        df_product = pd.DataFrame(workbook.worksheet("OneUp - Products").get_all_records()).drop_duplicates()
        df_customers = pd.DataFrame(workbook.worksheet("OneUp - Customers").get_all_records()).drop_duplicates()
        df_transactions_sumup = pd.DataFrame(workbook.worksheet("SumUp - Product Transaction").get_all_records()).drop_duplicates()
        df_product_inventory_analysis = pd.DataFrame(workbook.worksheet("Product Inventory Consumption - Merged").get_all_records()).drop_duplicates()
        df_product_inventory = pd.DataFrame(workbook.worksheet("Product Inventory").get_all_records()).drop_duplicates()
        return df_sales, df_product, df_customers, df_transactions_sumup, df_product_inventory_analysis, df_product_inventory


    @st.cache_data(ttl=300, show_spinner=False)
    def prepare_data(_df_sales, _df_product, _df_transactions_sumup):
        """Prepare and transform data once - cached for performance"""
        df_sales = _df_sales.copy()
        df_product = _df_product.copy()
        df_transactions_sumup = _df_transactions_sumup.copy()
        
        # Convert data types
        df_sales["date"] = pd.to_datetime(df_sales["date"], errors="coerce")
        df_sales["paid"] = pd.to_numeric(df_sales["paid"] - df_sales["tax_amount"], errors="coerce")
        df_sales["subtotal"] = pd.to_numeric(df_sales["subtotal"], errors="coerce")
        df_sales["quantity"] = pd.to_numeric(df_sales["quantity"], errors="coerce")
        df_sales["unit_price"] = pd.to_numeric(df_sales["unit_price"], errors="coerce")
        df_sales["total_order_line"] = pd.to_numeric(df_sales["total_order_line"], errors="coerce")
        df_product["purchase_price"] = pd.to_numeric(df_product["purchase_price"], errors="coerce")
        df_transactions_sumup["date"] = pd.to_datetime(df_transactions_sumup["timestamp"], errors="coerce")
        
        # Filter successful transactions only
        df_transactions_sumup = df_transactions_sumup[df_transactions_sumup["status"] == "SUCCESSFUL"]
        
        # Create sales order dataframe
        df_sales_order = df_sales[
            ["invoice_id", "date", "paid", "total_order_line", "item_id", "customer_name", "country", "city", "source"]
        ].drop_duplicates()
        
        # Create invoices metadata dataframe
        df_invoices = df_sales[
            ["invoice_id", "customer_name", "country", "city", "date", "due_date", "amount", "sent", "paid", "source"]
        ].drop_duplicates()
        
        # SumUp sales
        df_sales_sumup = df_transactions_sumup[
            ["id", "date", "total_price", "customer_name", "country", "city", "source"]
        ].drop_duplicates()

        df_sales_sumup.rename(columns={"total_price": "total_order_line"}, inplace=True)

        df_sales_sumup["item_id"] = None
        
        # Merge sales orders
        df_sales_order_merged = pd.concat([
            df_sales_order.rename(columns={'invoice_id': 'id'}),
            df_sales_sumup
        ], ignore_index=True)
        
        df_sales_order_merged = pd.merge(df_sales_order_merged, df_product[['id','item_family_name']],
                                         left_on="item_id", right_on="id")
        
        
        # Prepare product sales data
        df_product_sales_oneup = df_sales[
            ["invoice_id", "customer_name", "item_id", "country", "date", "unit_price", "total_order_line", "quantity", "source"]
        ]

        # Merge One up Sales with One up Products to get product name based on id
        df_product_sales_oneup["product_name"] = df_product_sales_oneup["item_id"].map(df_product.set_index("id")["name"])

        
        df_product_sales_sumup = df_transactions_sumup[
            ["id", "customer_name", "product_name", "country", "timestamp", "price", "total_price", "quantity", "source"]
        ].rename(columns={
            "timestamp": "date",
            "price": "unit_price",
            "total_price": "total_order_line"
        })
        
        df_product_sales_sumup["item_id"] = 0
        df_product_sales_sumup = df_product_sales_sumup[
            ["id", "customer_name", "item_id", "product_name", "country", "date", "unit_price", "total_order_line", "quantity", "source"]
        ]
        
        df_product_sales_merged = pd.concat([
            df_product_sales_oneup.rename(columns={"invoice_id": "id"}),
            df_product_sales_sumup
        ], ignore_index=True)
        
        df_product_sales_merged["date"] = pd.to_datetime(df_product_sales_merged["date"])
        
        return df_sales_order_merged, df_invoices, df_product_sales_merged, df_product

    
    df_sales, df_product, df_customers, df_transactions_sumup, df_product_inventory_analysis, df_product_inventory  = load_data()
    df_sales_order_merged, df_invoices, df_product_sales_merged, df_product_clean = prepare_data(
        df_sales, df_product, df_transactions_sumup
    )

    # ========== HELPER FUNCTIONS ==========
    def print_invoice(invoice_id, format):
        url = f"https://api.oneup.com/v1/invoices/{invoice_id}/print.{format}"
        response = requests.get(url, auth=HTTPBasicAuth(API_EMAIL, API_KEY), verify=False)
        
        if response.status_code == 200:
            if format == 'pdf':
                with open(f"invoice_{invoice_id}.pdf", "wb") as f:
                    f.write(response.content)
                print("PDF saved successfully!")
            elif format == 'json':
                return json.loads(response.content)["url"]
        else:
            error = f"Error {response.status_code}: {response.text}"
            return error


    def trigger_manual_refresh():
        token = os.getenv('GITHUB_API')           
        owner = "haithemaoudia"
        repo = "noen_data_pipeline"
        workflow = "main.yml"                
        branch = "main"                        

        url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow}/dispatches"

        payload = {
            "ref": branch,
        }

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))


        if response.status_code == 204:
            print("Workflow dispatched successfully!")
        else:
            print("Failed to trigger workflow:", response.status_code, response.text)

    def send_email_invoice(file_data, email_sender, email_password, email_reciever, subject, body, invoice_number):
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = email_sender
            msg["To"] = email_reciever
            msg.set_content(body)
            
            # Add PDF attachment from BytesIO data
            msg.add_attachment(
                file_data, 
                maintype='application', 
                subtype='pdf',
                filename=f'invoice {invoice_number}.pdf'
            )
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(email_sender, email_password)
                server.send_message(msg)
            
            return True, "Email sent successfully!"
        
        except smtplib.SMTPAuthenticationError:
            return False, "❌ Authentication failed. Please check your email and password/app password."
        
        except smtplib.SMTPRecipientsRefused:
            return False, "❌ Recipient email address was refused. Please check the recipient email."
        
        except smtplib.SMTPException as e:
            return False, f"❌ SMTP error occurred: {str(e)}"
        
        except Exception as e:
            return False, f"❌ Unexpected error: {str(e)}"

    # ========== FILTER FUNCTIONS ==========
    def apply_date_filter(df, start_date, end_date, date_column='date'):
        """Apply date filter efficiently"""
        return df[(df[date_column] >= pd.to_datetime(start_date)) & 
                (df[date_column] <= pd.to_datetime(end_date))]

    def apply_country_filter(df, country):
        """Apply country filter efficiently"""
        if country != "All":
            return df[df["country"] == country]
        return df

    def apply_source_filter(df, sources):
        """Apply source filter efficiently"""
        if sources:
            return df[df["source"].isin(sources)]
        return df

    def apply_invoice_status_filter(df, status):
        if set(status) == {"Paid", "Unpaid"} or not status:
            return df
    
        if "Paid" in status and "Unpaid" not in status:
            return df[df["paid"] != 0]
        

        if "Unpaid" in status and "Paid" not in status:
            return df[df["paid"] == 0]
        

        return df

    def apply_product_family_filter(df, family):
            if len(family) == 0:
                return df
            else:
                return df[df["item_family_name"].isin(family)]

    # ========== ANALYTICS FUNCTIONS ==========
    def calculate_customer_metrics(df):
        """Calculate customer metrics"""
        if len(df) == 0:
            return pd.DataFrame(columns=["customer_name", "num_transactions", "total_revenue", "AOV", "transaction_frequency"])
        
        
        metrics = (
            df.groupby(["customer_name"], as_index=False)
            .agg({
                "id_x": "nunique",
                "total_order_line": "sum"
            })
            .rename(columns={"id_x": "num_transactions", "total_order_line": "total_revenue"})
        )
        
        metrics["AOV"] = metrics["total_revenue"] / metrics["num_transactions"]
        metrics["transaction_frequency"] = metrics["num_transactions"] / metrics["total_revenue"]
        
        return metrics

    def calculate_product_metrics(df, df_product):
        """Calculate product metrics"""
        if len(df) == 0:
            return pd.DataFrame(columns=["product_name", "item_family_name", "quantity", "revenue", "gross_margin", "margin_%", "margin_contribution_%"])
        
        df_merged = df.merge(
            df_product[["id", "purchase_price", "item_family_name"]],
            how="left",
            left_on="item_id",
            right_on="id"
        )

    

        
        # df_merged = df_merged[df_merged["purchase_price"] > 0]
        df_merged = df_merged[df_merged["product_name"] != '']
        
        df_merged["total_cost"] = df_merged["purchase_price"] * df_merged["quantity"]
        df_merged["total_gross_margin"] = df_merged["total_order_line"] - df_merged["total_cost"]
      
        product_metrics = (
            df_merged.groupby(["product_name", "item_family_name", "customer_name"], as_index=False)
            .agg({
                "quantity": "sum",
                "total_order_line": "sum",
                "total_gross_margin": "sum"
            })
            .rename(columns={"total_order_line": "revenue"})
        )

        
        product_metrics["margin_%"] = (product_metrics["total_gross_margin"] / product_metrics["revenue"]) * 100
        product_metrics = product_metrics[product_metrics["margin_%"] > 0]
        product_metrics["margin_contribution_%"] = (
            (product_metrics["total_gross_margin"] / product_metrics["total_gross_margin"].sum()) * 100
        )
        
        return product_metrics


    # ========= INVENTORY FUNCTIONS ============
    def get_product_inventory(product_name:str):
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(google_cred, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet_id = os.getenv('SHEET_ID')
        workbook = client.open_by_key(sheet_id)
        sheet = workbook.worksheet("Product Inventory")
        
        row = sheet.find(product_name).row
        quantity_available = sheet.get(f"X{row}")[0][0]
        return int(quantity_available)




    #Update Inventory value for a given product name
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(google_cred, scopes=scope)
    client = gspread.authorize(creds)



    def update_product_inventory(new_df):
        sheet_id = os.getenv('SHEET_ID')
        workbook = client.open_by_key(sheet_id)
        sheet = workbook.worksheet("Product Inventory")
        set_with_dataframe(sheet, new_df)



    # ========== HEADER ==========
        # ========== HEADER WITH LOGO ==========
    authenticator.logout("logout", "sidebar")
    
    # Create logo header
    col1, col2 = st.columns([3, 1])
    with open("NOEN-logo.png", "rb") as f:
        data = base64.b64encode(f.read()).decode()
    with col1:
        st.markdown(f"""
        <div class="logo-header">
            <div class="logo-container">
                <img src="data:image/png;base64,{data}" class="logo-image" alt="NOEN Logo">
                <div>
                    <h1 class="company-title">NOEN Seafood Analytics</h1>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)

    # ========== TABS ==========
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "📈 Analytics" 

    manual_refresh = st.button("Trigger Data Refresh")

    if manual_refresh:
        trigger_manual_refresh()


    tab1, tab2, tab3, tab4 = st.tabs(["📈 Analytics", "📦 Inventory", "🚀 Forecast", "🧾 Invoice Manager"])

    # ========================================
    # TAB 1: ANALYTICS DASHBOARD
    # ========================================
    with tab1:
        # ========== FILTERS ==========
        # st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.subheader("🔍 Filters")

        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])

        min_date = df_sales_order_merged["date"].min()
        max_date = df_sales_order_merged["date"].max()
        today = datetime.today()

        with col1:
            date_options = ["YTD","Past Month", "Q1", "Q2", "Q3", "Q4", "Custom Range"]
            selected_range = st.selectbox("📅 Date Range", date_options, index=0)

            if selected_range == "YTD":
                start_date = datetime(max_date.year, 1, 1)
                end_date = max_date
            
            
            elif selected_range == "Past Month":
                start_date = max_date - pd.DateOffset(months=1)
                end_date = max_date
                

            elif selected_range == "Q1":
                start_date = datetime(max_date.year, 1, 1)
                end_date = datetime(max_date.year, 3, 31)

            elif selected_range == "Q2":
                start_date = datetime(max_date.year, 4, 1)
                end_date = datetime(max_date.year, 6, 30)

            elif selected_range == "Q3":
                start_date = datetime(max_date.year, 7, 1)
                end_date = datetime(max_date.year, 9, 30)

            elif selected_range == "Q4":
                start_date = datetime(max_date.year, 10, 1)
                end_date = datetime(max_date.year, 12, 31)

            elif selected_range == "Custom Range":
                start_date = st.date_input("📅 Start Date", value=min_date, min_value=min_date, max_value=max_date)
                end_date = st.date_input("📅 End Date", value=max_date, min_value=min_date, max_value=max_date)

            else:
                start_date, end_date = min_date, max_date

        with col2:
            countries = ["All"] + sorted(df_sales_order_merged["country"].dropna().unique().tolist())
            selected_country = st.selectbox("🌍 Country", countries)

        with col3:  
            source = st.multiselect("Data Source", ["OneUp", "SumUp"])
        
        with col4:
            selected_status = st.multiselect(
            "Select Invoice Status:",
            options=["Paid", "Unpaid"])
        with col5:
            selected_product_family = st.multiselect(
            "Product Family", 
            options=[
    "Filets", "Inktvissen en Celaphoden", "Hele vis", "Snacks",
    "Overig", "PD Garnalen", "HOSO", "Mollusken", "Zeevruchten", "Groente",
    "Steaks", "PUD Cocktail", "Party Garnalen", "Surimi", "HLSO"
])

        st.markdown('</div>', unsafe_allow_html=True)

        # ========== APPLY FILTERS ==========
        filtered_df = apply_date_filter(df_sales_order_merged, start_date, end_date)
        filtered_df = apply_country_filter(filtered_df, selected_country)
        filtered_df = apply_source_filter(filtered_df, source)
        filtered_df = apply_invoice_status_filter(filtered_df, selected_status)
        filtered_df = apply_product_family_filter(filtered_df, selected_product_family)
        
        # ========== CUSTOMER ANALYSIS ==========
        st.header("👥 Customer Analytics")

        # Calculate customer metrics using cached function
        metrics = calculate_customer_metrics(filtered_df)

        # Top customers
        if not metrics.empty:
            # top_revenue = metrics.nlargest(10, "total_revenue")
            #Define Top 10 Using Group By and desc on Customer
            


            top_revenue = metrics.groupby('customer_name').agg({
                        'total_revenue': 'sum',
                        'num_transactions': 'sum',
                        'AOV': 'mean'
                    }).nlargest(10, 'total_revenue').reset_index()






            top_transactions = metrics.groupby('customer_name').agg({
                        'total_revenue': 'sum',
                        'num_transactions': 'sum',
                        'AOV': 'mean'
                    }).nlargest(10, 'num_transactions').reset_index()
            


            # KPI Cards
            col1, col2, col3, col4 = st.columns([0.6, 1, 0.5, 1])

            with col1:
                st.metric("💰 Total Revenue", f"€{metrics['total_revenue'].sum():,.0f}")

            with col2:
                name = top_revenue.iloc[0]['customer_name']
                total_rev = top_revenue.iloc[0]['total_revenue']
                st.metric("🏆 Top Customer", name, f"€{total_rev:,.0f}")
            with col3:
                st.metric("📦 Average Order Value", f"€{metrics['AOV'].mean():,.0f}")
            with col4:
                most_active = top_transactions.iloc[0]
                name = most_active["customer_name"]
                st.metric("🔄 Most Active Customer", name, f"{int(most_active['num_transactions'])} orders")
            st.markdown("---")

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("💰 Top 10 Customers by Revenue")
                chart_revenue = (
                    alt.Chart(top_revenue)
                    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                    .encode(
                        x=alt.X("total_revenue:Q", title="Revenue (€)", axis=alt.Axis(format=".0f")),
                        y=alt.Y("customer_name:N", sort="-x", title=None),
                        color=alt.value("#10b981"),
                        tooltip=[
                            alt.Tooltip("customer_name:N", title="Customer"),
                            alt.Tooltip("total_revenue:Q", title="Revenue", format=".2f"),
                            alt.Tooltip("num_transactions:Q", title="Orders"),
                            alt.Tooltip("AOV:Q", title="AOV", format=".2f")
                        ]
                    )
                    .properties(height=400)
                    .configure(background='#f0f9ff;')
                )
                st.altair_chart(chart_revenue, use_container_width=True)

            with col2:
                st.subheader("🔁 Top 10 by Transaction Count")
                chart_transactions = (
                    alt.Chart(top_transactions)
                    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                    .encode(
                        x=alt.X("num_transactions:Q", title="Number of Transactions"),
                        y=alt.Y("customer_name:N", sort="-x", title=None),
                        color=alt.value("#3b82f6"),
                        tooltip=[
                            alt.Tooltip("customer_name:N", title="Customer"),
                            alt.Tooltip("num_transactions:Q", title="Transactions"),
                            alt.Tooltip("total_revenue:Q", title="Revenue", format=".2f"),
                            alt.Tooltip("AOV:Q", title="AOV", format=".2f")
                        ]
                    )
                    .properties(height=400)
                    .configure(background='#f0f9ff;')
                )
                st.altair_chart(chart_transactions, use_container_width=True)

        st.markdown("""
#### **Revenue Calculations**
- **Total Revenue** = Amount Paid − VAT Tax  
- **Average Order Value (AOV)** = Total Revenue ÷ Number of Transactions  
- **Transaction Count** = Sum of Invoice IDs  
""")

        # ========== PRODUCT ANALYSIS ==========
        st.header("📦 Product Performance")
        # Apply filters to product data
        filtered_sales = apply_date_filter(df_product_sales_merged, start_date, end_date)
        filtered_sales = apply_country_filter(filtered_sales, selected_country)
        filtered_sales = apply_source_filter(filtered_sales, source)
        

        # Calculate product metrics using cached function
        product_metrics = calculate_product_metrics(filtered_sales, df_product_clean)
        product_metrics = apply_product_family_filter(product_metrics, selected_product_family)
        product_metrics = product_metrics[product_metrics["margin_%"] > 0]
        # Top products
        if not product_metrics.empty:
            # top_units = product_metrics.nlargest(10, "quantity")
            top_units = product_metrics.groupby(['product_name', 'item_family_name']).agg({
                        'quantity': 'sum',
                        'revenue': 'sum',
                        'total_gross_margin': 'sum', 
                        'margin_%': 'mean', 
                        'margin_contribution_%': 'mean'
                    }).nlargest(10, 'quantity').reset_index()
      
   
            top_product_revenue = product_metrics.groupby(['product_name', 'item_family_name']).agg({
                        'quantity': 'sum',
                        'revenue': 'sum',
                        'total_gross_margin': 'sum', 
                        'margin_%': 'mean', 
                        'margin_contribution_%': 'mean'
                    }).nlargest(10, 'revenue').reset_index()
            # top_margin = product_metrics.nlargest(10, "total_gross_margin")
            top_margin = product_metrics[product_metrics["margin_%"] != 100].groupby(['product_name', 'item_family_name']).agg({
                        'quantity': 'sum',
                        'revenue': 'sum',
                        'total_gross_margin': 'sum', 
                        'margin_%': 'mean', 
                        'margin_contribution_%': 'mean'
                    }).nlargest(10, 'revenue').reset_index()
            

            top_customer = product_metrics[product_metrics["margin_%"] != 100].groupby(['customer_name']).agg({
                        'quantity': 'sum',
                        'revenue': 'sum',
                        'total_gross_margin': 'sum', 
                        'margin_%': 'mean', 
                        'margin_contribution_%': 'mean'
                    }).nlargest(10, 'revenue').reset_index()

            product_family_margins = product_metrics[product_metrics["margin_%"] != 100].groupby(['item_family_name']).agg({
                        'quantity': 'sum',
                        'revenue': 'sum',
                        'total_gross_margin': 'sum', 
                        'margin_%': 'mean', 
                        'margin_contribution_%': 'mean'
                    }).reset_index()
            
            
            # product_metrics[product_metrics["margin_%"] != 100].nlargest(10, "total_gross_margin", )
   
            # Product KPIs
            col1, col2, col3, col4 = st.columns([0.3, 1, 0.3, 0.3])

            with col1:
                st.metric("📊 Total Units Sold", f"{int(product_metrics['quantity'].sum()):,}")

            with col2:
                best_seller = top_units.iloc[0]
                name = best_seller["product_name"]
                st.metric("🏅 Best Seller", name, f"{int(best_seller['quantity']):,} units")

            with col3:
                st.metric("💵 Total Gross Margin", f"€{product_metrics[product_metrics["margin_%"] != 100]['total_gross_margin'].sum():,.0f}")

            with col4:
                avg_margin = product_metrics[product_metrics["margin_%"] != 100]["margin_%"].mean()
                st.metric("📈 Avg Margin %", f"{avg_margin:.1f}%")

            
            st.markdown("---")


            # Product charts
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📦 Top 10 Products by Units Sold")
                chart_units = (
                    alt.Chart(top_units)
                    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                    .encode(
                        x=alt.X("quantity:Q", title="Units Sold"),
                        y=alt.Y("product_name:N", sort="-x", title=None),
                        color=alt.value("#10b981"),
                        tooltip=[
                            alt.Tooltip("product_name:N", title="Product"),
                            alt.Tooltip("quantity:Q", title="Units Sold", format=","),
                            alt.Tooltip("revenue:Q", title="Revenue", format=".2f"),
                            # alt.Tooltip("margin_%:Q", title="Margin %", format=".1f")
                        ]
                    )
                    .properties(height=400)
                    .configure(background='#f0f9ff;')
                )
                st.altair_chart(chart_units, use_container_width=True)

            with col2:
                st.subheader("💰 Top 10 Products by Revenue")
                chart_prod_revenue = (
                    alt.Chart(top_product_revenue)
                    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                    .encode(
                        x=alt.X("revenue:Q", title="Revenue (€)", axis=alt.Axis(format=".0f")),
                        y=alt.Y("product_name:N", sort="-x", title=None),
                        color=alt.value("#3b82f6"),
                        tooltip=[
                            alt.Tooltip("product_name:N", title="Product"),
                            alt.Tooltip("revenue:Q", title="Revenue", format=".2f"),
                            alt.Tooltip("quantity:Q", title="Units Sold", format=","),
                            # alt.Tooltip("margin_%:Q", title="Margin %", format=".1f")
                        ]
                    )
                    .properties(height=400)
                    .configure(background='#f0f9ff;')
                )
                st.altair_chart(chart_prod_revenue, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🏅 Top 10 Products by Gross Margin")
                chart_margin = (
                    alt.Chart(top_margin)
                    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                    .encode(
                        x=alt.X("total_gross_margin:Q", title="Gross Margin (€)", axis=alt.Axis(format=".0f")),
                        y=alt.Y("product_name:N", sort="-x", title=None),
                        color=alt.value("#f59e0b"),
                        tooltip=[
                            alt.Tooltip("product_name:N", title="Product"),
                            alt.Tooltip("total_gross_margin:Q", title="Total Gross Margin", format=".2f"),
                            alt.Tooltip("margin_%:Q", title="Margin %", format=".1f"),
                            alt.Tooltip("revenue:Q", title="Revenue", format=".2f")
                        ]
                    )
                    .properties(height=400)
                    .configure(background='#f0f9ff;')
                )
                st.altair_chart(chart_margin, use_container_width=True)

            with col2:
                st.subheader("📦 Gross Margin by Product Family")
                chart_margin = (
                    alt.Chart(product_family_margins)
                    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                    .encode(
                        x=alt.X("total_gross_margin:Q", title="Gross Margin (€)", axis=alt.Axis(format=".0f")),
                        y=alt.Y("item_family_name:N", sort="-x", title=None),
                        color=alt.value("#f59e0b"),
                        tooltip=[
                            alt.Tooltip("item_family_name:N", title="Product"),
                            alt.Tooltip("total_gross_margin:Q", title="Total Gross Margin", format=".2f"),
                            alt.Tooltip("margin_%:Q", title="Margin %", format=".1f"),
                            alt.Tooltip("revenue:Q", title="Revenue", format=".2f")
                        ]
                    )
                    .properties(height=400)
                    .configure(background='#f0f9ff;')
                )
                st.altair_chart(chart_margin, use_container_width=True)

            st.subheader("Top 10 Customers by Gross Margin")
            chart_margin = (
                alt.Chart(top_customer)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                .encode(
                    x=alt.X("total_gross_margin:Q", title="Gross Margin (€)", axis=alt.Axis(format=".0f")),
                    y=alt.Y("customer_name:N", sort="-x", title=None),
                    color=alt.value("#360bf5"),
                    tooltip=[
                        alt.Tooltip("customer_name:N", title="Product"),
                        alt.Tooltip("total_gross_margin:Q", title="Total Gross Margin", format=".2f"),
                        alt.Tooltip("margin_%:Q", title="Margin %", format=".1f"),
                        alt.Tooltip("revenue:Q", title="Revenue", format=".2f")
                    ]
                )
                .properties(height=400)
                .configure(background='#f0f9ff;')
            )
            st.altair_chart(chart_margin, use_container_width=True)


        st.markdown("""
    #### **Product Sales Calculations**
    - **Units Sold by Product** = Sum of product sales order line quantity
    - **Revenue Generated per Products** = Sum of Total Order Line                


    #### **Gross Margin Calculations**
    - **Total Cost** = Purchase Price × Quantity  
    - **Total Gross Margin** = Total Order Line (Product Revenue *excl. VAT*) − Total Cost  
    """)



    # ========================================
    # TAB 2: INVENTORY
    # ========================================
    if 'inventory_updated' not in st.session_state:
        st.session_state.inventory_updated = False
    
    with tab2:

        # --- 🧾 Inventory display ---
        st.write("### Product Inventory")

        if st.session_state.inventory_updated:
            st.success("✅ Inventory updated successfully!")
            st.session_state.inventory_updated = False

        # Display headers
        product_list = df_product_inventory["product_name"].tolist()

        search_selection = st.selectbox(
            "Search or select a product",
            options=[""] + product_list,
            index=0,
            placeholder="Type to search for a product..."
        )

        # Filter dataframe
        if search_selection:
            filtered_df = df_product_inventory[df_product_inventory["product_name"] == search_selection]
        else:
            filtered_df = df_product_inventory

        # --- 🧾 Display headers ---
        cols = st.columns([4, 1])
        headers = ["Product Name", "Available Quantity"]
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")

        # --- 🧮 Editable quantities ---
        updated_quantities = {}

        for idx, row in filtered_df.iterrows():
            cols = st.columns([4, 1])
            with cols[0]:
                st.text(row["product_name"])
            with cols[1]:
                updated_quantities[idx] = st.number_input(
                    "",
                    value=int(row["current_quantity"]),
                    min_value=0,
                    key=f"qty_{idx}"
                )

        # --- 💾 Save updates ---
        if st.button("Save Changes"):
            for idx, qty in updated_quantities.items():
                df_product_inventory.at[idx, "current_quantity"] = qty
            update_product_inventory(df_product_inventory)
            load_data.clear()
            st.session_state.inventory_updated = True
            st.rerun()



    # ========================================
    # TAB 3: FORECAST
    # ========================================
    # --- Page Layout ---
    with tab3:
        
        st.session_state.active_tab = "🚀 Forecast"
        # ---- Product detail view ----
        st.subheader("📈 Historical and Forecast Product Units Sold")

        product_options = df_product_inventory_analysis["product_name"].unique()
        
        selected_product = st.selectbox("Select a product to view trend", product_options)

        if selected_product:
            # Prepare product data
            product_df = (
                df_product_inventory_analysis[
                    df_product_inventory_analysis["product_name"] == selected_product
                ]
                .drop(columns=["product_name"])
                .T
                .reset_index()
            )
            product_df.columns = ["Month", "Quantity"]

            # Parse month columns
            product_df["Month"] = pd.to_datetime(product_df["Month"], errors="coerce")

            # Determine historical vs forecast cutoff (based on today's date)
            today = pd.Timestamp(datetime.today().strftime("%Y-%m-01"))  # Start of current month
            product_df["Type"] = product_df["Month"].apply(
                lambda x: "Historical" if x < today else "Forecast"
            )

            # Split data
            hist_df = product_df[product_df["Type"] == "Historical"]
            forecast_df = product_df[product_df["Type"] == "Forecast"]

            # ---- Plot ----
            fig = go.Figure()

            # Historical line
            fig.add_trace(go.Scatter(
                x=hist_df["Month"],
                y=hist_df["Quantity"],
                mode="lines+markers",
                name="Historical",
                line=dict(color="royalblue", width=2),
                marker=dict(size=6),
            ))

            # Forecast line
            fig.add_trace(go.Scatter(
                x=forecast_df["Month"],
                y=forecast_df["Quantity"],
                mode="lines+markers",
                name="Forecast",
                line=dict(color="orange", width=2, dash="dash"),
                marker=dict(size=6),
            ))


            fig.update_layout(
                title=f"📆 Quantity Sold Over Time: {selected_product}",
                xaxis_title="Month",
                yaxis_title="Quantity Sold",
                hovermode="x unified",
                legend_title="Data Type",
                template="plotly_white",
                plot_bgcolor="#f0f9ff",   
                paper_bgcolor="#f0f9ff"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Full Data Inventory Consumption")
        # search = st.text_input("🔍 Search product name", "")
        filtered = df_product_inventory_analysis[
            df_product_inventory_analysis["product_name"].str.contains(selected_product, case=False, na=False)
        ]
        st.dataframe(filtered, use_container_width=True, height=400)





    # ========================================
    # TAB 3: INVOICE MANAGER
    # ========================================
    with tab4:
        st.header("🧾 Invoice Manager")
        st.markdown("**Select and download invoices in bulk**")
        st.markdown("---")
        
        # ========== INVOICE FILTERS ==========
        st.subheader("🔍 Filter Invoices")
        
        col1, col2, col3 = st.columns(3)

        min_date = df_sales_order_merged["date"].min()
        max_date = df_sales_order_merged["date"].max()
        
        with col1:
            date_options = ["Past Month", "Last 3 Months", "Last 6 Months", "YTD", "Custom Range"]
            selected_range = st.selectbox("📅 Invoice Date Range", date_options, index=0)
            # inv_start_date = df_invoices["date"].min()
            # inv_end_date = df_invoices["date"].max()

            if selected_range == "Past Month":
                inv_start_date = max_date - pd.DateOffset(months=1)
                inv_end_date = max_date
            elif selected_range == "Last 3 Months":
                inv_start_date = max_date - pd.DateOffset(months=3)
                inv_end_date = max_date
            elif selected_range == "Last 6 Months":
                inv_start_date = max_date - pd.DateOffset(months=6)
                inv_end_date = max_date
            elif selected_range == "YTD":
                inv_start_date = datetime(max_date.year, 1, 1)
                inv_end_date = max_date
            elif selected_range == "Custom Range":
                inv_start_date = st.date_input("📅 Start Date ", value=min_date, min_value=min_date, max_value=max_date)
                inv_end_date = st.date_input("📅 End Date ", value=max_date, min_value=min_date, max_value=max_date)
            else:
                inv_start_date, inv_end_date = min_date, max_date

        
        with col2:
            inv_countries = ["All"] + sorted(df_invoices["country"].dropna().unique().tolist())
            inv_selected_country = st.selectbox("🌍 Country", inv_countries, key="invoice_country")
        
        with col3:
            payment_status = st.selectbox(
                "💳 Payment Status", 
                ["All", "Paid", "Unpaid"],
                key="payment_status"
            )
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            sent_status = st.selectbox(
                "📧 Sent Status", 
                ["All", "Sent", "Not Sent"],
                key="sent_status"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ========== APPLY INVOICE FILTERS ==========
        filtered_invoices = apply_date_filter(df_invoices, inv_start_date, inv_end_date)
        filtered_invoices = apply_country_filter(filtered_invoices, inv_selected_country)
        
        if payment_status == "Paid":
            filtered_invoices = filtered_invoices[filtered_invoices["paid"] > 0]
        elif payment_status == "Unpaid":
            filtered_invoices = filtered_invoices[filtered_invoices["paid"] == 0]
        
        if sent_status == "Sent":
            filtered_invoices = filtered_invoices[filtered_invoices["sent"] == True]
        elif sent_status == "Not Sent":
            filtered_invoices = filtered_invoices[filtered_invoices["sent"] == False]
        
        # ========== SUMMARY METRICS ==========
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Invoices", len(filtered_invoices))
        
        with col2:
            total_amount = filtered_invoices["amount"].sum()
            st.metric("💰 Total Amount", f"€{total_amount:,.2f}")
        
        with col3:
            paid_count = len(filtered_invoices[filtered_invoices["paid"] > 0])
            st.metric("✅ Paid Invoices", paid_count)
        
        with col4:
            unpaid_count = len(filtered_invoices[filtered_invoices["paid"] == 0])
            st.metric("⏳ Unpaid Invoices", unpaid_count)
        
        st.markdown("---")
        
        # ========== INVOICE SELECTION ==========
        st.subheader("📋 Select Invoices to Download")
        
        # Initialize session state for selections
        if 'selected_invoices' not in st.session_state:
            st.session_state.selected_invoices = set()
        
        # Initialize a flag to track if we need to update the selection
        if 'force_select_all' not in st.session_state:
            st.session_state.force_select_all = False
        if 'force_deselect_all' not in st.session_state:
            st.session_state.force_deselect_all = False
        
        # Select All / Deselect All buttons
        col1, col2, col3 = st.columns([1, 1, 8])
        
        with col1:
            if st.button("✅ Select All", use_container_width=True, key="btn_select_all"):
                st.session_state.selected_invoices = set(filtered_invoices["invoice_id"].tolist())
                st.session_state.force_select_all = True
                st.session_state.force_deselect_all = False
        
        with col2:
            if st.button("❌ Deselect All", use_container_width=True, key="btn_deselect_all"):
                st.session_state.selected_invoices = set()
                st.session_state.force_deselect_all = True
                st.session_state.force_select_all = False
        
        st.markdown("---")
        
        # ========== INVOICE TABLE WITH CHECKBOXES ==========
        if len(filtered_invoices) > 0:
            st.markdown("##### Select invoices to download:")
            filtered_invoices = filtered_invoices.sort_values(by='date', ascending= False)
            # Use pagination for large datasets
            items_per_page = 50
            total_pages = (len(filtered_invoices) - 1) // items_per_page + 1
            
            if total_pages > 1:
                page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
                start_idx = (page - 1) * items_per_page
                end_idx = min(start_idx + items_per_page, len(filtered_invoices))
                display_invoices = filtered_invoices.iloc[start_idx:end_idx]
                st.info(f"Showing {start_idx + 1}-{end_idx} of {len(filtered_invoices)} invoices")
            else:
                display_invoices = filtered_invoices
            
            # Create columns for the header
            header_cols = st.columns([0.5, 2, 2, 1.5, 1.5, 1, 1, 1, 1.5])
            headers = ["Select", "Invoice ID", "Customer", "Country", "City", "Date", "Amount", "Sent", "Status"]
            
            for col, header in zip(header_cols, headers):
                col.markdown(f"**{header}**")
            
            st.markdown("---")
            
            # Display each invoice with checkbox
            for idx, row in display_invoices.iterrows():
                cols = st.columns([0.5, 2, 2, 1.5, 1.5, 1, 1, 1, 1.5])
                
                with cols[0]:
                    is_selected = row["invoice_id"] in st.session_state.selected_invoices
                    checkbox_changed = st.checkbox(
                        "", 
                        value=is_selected, 
                        key=f"check_{row['invoice_id']}_{is_selected}"  # Dynamic key forces re-render
                    )
                    
                    # Update selection based on checkbox state
                    if checkbox_changed:
                        st.session_state.selected_invoices.add(row["invoice_id"])
                    else:
                        st.session_state.selected_invoices.discard(row["invoice_id"])
                    
                    # Reset the force flags after processing
                    if idx == display_invoices.index[-1]:  # Last item
                        st.session_state.force_select_all = False
                        st.session_state.force_deselect_all = False
                
                with cols[1]:
                    st.text(row["invoice_id"])
                
                with cols[2]:
                    customer_name = row["customer_name"]
                    st.text(customer_name[:25] + "..." if len(customer_name) > 25 else customer_name)
                
                with cols[3]:
                    st.text(row["country"])
                
                with cols[4]:
                    st.text(row["city"])
                
                with cols[5]:
                    st.text(row["date"].strftime("%Y-%m-%d"))
                
                with cols[6]:
                    st.text(f"€{row['amount']:,.2f}")
                
                with cols[7]:
                    st.text("✅" if row["sent"] else "❌")
                
                with cols[8]:
                    status = "✅ Paid" if row["paid"] > 0 else "⏳ Unpaid"
                    st.text(status)
            
            st.markdown("---")
            
        st.subheader(f"📥 Download Selected Invoices ({len(st.session_state.selected_invoices)} selected)")
        st.session_state.selected_invoices
        if len(st.session_state.selected_invoices) > 0:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info(f"Ready to download {len(st.session_state.selected_invoices)} invoice(s)")
            
            with col2:
                if st.button("🚀 Download PDFs", type="primary", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    total_invoices = len(st.session_state.selected_invoices)
                    
                    # Fetch PDF URLs
                    status_text.text("🔄 Fetching invoice URLs...")
                    pdf_urls = []
                    for i, invoice_id in enumerate(st.session_state.selected_invoices):
                        pdf_urls.append(print_invoice(invoice_id, 'json'))
                        progress_bar.progress((i + 1) / total_invoices)
                    
                    # Merge PDFs
                    merger = PdfMerger()
                    status_text.text("🔄 Merging PDFs...")

                    for i, url in enumerate(pdf_urls, start=1):
                        try:
                            response = requests.get(url)
                            response.raise_for_status()
                            merger.append(BytesIO(response.content))
                        except Exception as e:
                            st.error(f"❌ Failed to load PDF {url}: {e}")

                    # Write merged PDF to in-memory buffer
                    merged_pdf = BytesIO()
                    merger.write(merged_pdf)
                    merger.close()
                    merged_pdf.seek(0)

                    # Store in session state for email button
                    st.session_state.merged_pdf_data = merged_pdf.read()
                    merged_pdf.seek(0)

                    # Encode for new tab view
                    b64_pdf = base64.b64encode(st.session_state.merged_pdf_data).decode("utf-8")

                    status_text.text("✅ PDFs merged successfully!")
                    progress_bar.progress(1.0)

                    # Display link to open in new tab
                    pdf_display_link = f'<a href="data:application/pdf;base64,{b64_pdf}" target="_blank">📂 Open Merged PDF in New Tab</a>'
                    st.markdown(pdf_display_link, unsafe_allow_html=True)
                    
            # Show download and email buttons if PDF exists
            
        if 'merged_pdf_data' in st.session_state and st.session_state.merged_pdf_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="⬇️ Download Merged PDF",
                    data=st.session_state.merged_pdf_data,
                    file_name="merged_invoices.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with col2:
                if st.button("📧 Send to Email", use_container_width=True):
                    st.session_state.show_email_form = True
            
            if st.session_state.get('show_email_form', False):
                st.markdown("---")
                st.subheader("📧 Send Invoices via Email")

                # --- Get selected invoices ---
                selected_invoices_df = filtered_invoices[
                    filtered_invoices["invoice_id"].isin(st.session_state.selected_invoices)
                ]

                st.info(f"📊 {len(selected_invoices_df)} invoice(s) will be sent individually")

                # Initialize session state for email customizations
                if 'email_customizations' not in st.session_state:
                    st.session_state.email_customizations = {}

                st.markdown("---")
                st.markdown("#### Review and Edit Each Email")

                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

                # --- Loop through each selected invoice (one email per invoice) ---
                for _, invoice_row in selected_invoices_df.iterrows():
                    invoice_id = invoice_row["invoice_id"]
                    customer_name = invoice_row["customer_name"]


                    with st.expander(f"📧 {customer_name} — Invoice #{invoice_id}", expanded=True):
                        # --- Fetch customer info ---
                        customer_row = df_customers[df_customers["full_name"] == customer_name]
                        customer_email_default = (
                            customer_row["email"].values[0]
                            if not customer_row.empty else "No email found"
                        )
                        customer_country = (
                            customer_row["country"].values[0].strip().lower()
                            if not customer_row.empty and "country" in customer_row.columns
                            else "unknown"
                        )

                        # --- Determine default language based on country ---
                        if "france" in customer_country:
                            default_language = "French"
                        elif "netherlands" in customer_country or "belgium" in customer_country:
                            default_language = "Dutch"
                        else:
                            default_language = "Dutch"  # fallback

                        # --- Dynamic language selector per invoice ---
                        language_key = f"language_{customer_name}_{invoice_id}"
                        language_selected = st.selectbox(
                            "Select Language",
                            ["Dutch", "French"],
                        )

                        # --- Invoice details ---
                        total_amount = invoice_row["amount"]
                        due_date = invoice_row["due_date"]

                        # --- Generate default subject/body dynamically based on language ---
                        if language_selected == "Dutch":
                            default_subject = f"Factuur {invoice_id} - NOEN Seafood"
                            default_body = body = f"""
                            
Beste {customer_name},,

Hartelijk dank voor uw samenwerking en bestelling. We stellen dit zeer op prijs.

In de bijlage vindt u de bijbehorende factuur met nummer {invoice_id}.
Het totaalbedrag is €{total_amount:.2f}. We verzoeken u vriendelijk om deze te voldoen vóór {due_date}, onder vermelding van het factuurnummer.
Mocht u vragen hebben over de factuur, of als er iets onduidelijk is, neem dan gerust contact met ons op. 

We kijken graag met u mee en helpen u direct verder.

We zien uw betaling tegemoet.

Met vriendelijke groet,

Het team van NOEN Seafood
                            """
                        else:
                            default_subject = f"Facture {invoice_id} - NOEN Seafood"
                            default_body = f"""
Cher/Chère {customer_name},

Nous vous remercions sincèrement pour votre collaboration et votre commande. Nous apprécions grandement la confiance que vous nous accordez.

Veuillez trouver ci-joint la facture correspondante, portant le numéro {invoice_id}.

Le montant total s'élève à €{total_amount:.2f}. Nous vous prions aimablement de bien vouloir effectuer le règlement avant le {due_date}, en rappelant le numéro de facture en référence.

Si vous avez la moindre question concernant cette facture, ou si un point ne vous semble pas clair, n'hésitez surtout pas à nous contacter. Nous serons ravis d'examiner cela avec vous et de vous aider.

Nous vous remercions par avance pour votre règlement.

Cordialement,

L'équipe NOEN Seafood
                                """


                        # --- Unique keys for this invoice (avoid stale state) ---
                        email_key = f"email_{customer_name}_{invoice_id}"
                        subject_key = f"subject_{customer_name}_{invoice_id}_{language_selected}"
                        body_key = f"body_{customer_name}_{invoice_id}_{language_selected}"

                        # --- Editable email fields (reset when language changes) ---
                        customer_email = st.text_input(
                            "Recipient Email",
                            value=customer_email_default,
                            key=email_key,
                            help="Edit the email address if needed"
                        )

                        is_valid_email = bool(re.match(email_pattern, customer_email))
                        if not is_valid_email:
                            st.error("❌ Please enter a valid email address")

                        email_subject = st.text_input("Subject", value=default_subject, key=subject_key)
                        email_body = st.text_area("Message", value=default_body, height=200, key=body_key)

                        # --- Save this invoice's customization ---
                        st.session_state.email_customizations[invoice_id] = {
                            "customer_name": customer_name,
                            "email": customer_email,
                            "subject": email_subject,
                            "body": email_body,
                            "language": language_selected,
                            "is_valid": is_valid_email,
                        }

                        st.markdown(f"**Attachment:** Invoice #{invoice_id}")
                        st.markdown("---")

                # --- Action buttons ---
                st.markdown("#### 3. Send Emails")

                all_valid = all(cust["is_valid"] for cust in st.session_state.email_customizations.values())

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Send All Emails", type="primary", use_container_width=True, disabled=not all_valid):
                        if not all_valid:
                            st.error("❌ Please fix invalid email addresses before sending")
                        else:
                            st.session_state.confirm_send = True
                            st.rerun()

                
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.show_email_form = False
                        st.session_state.confirm_send = False
                        st.session_state.email_customizations = {}
                        st.rerun()

                if st.session_state.get("confirm_send", False):
                    st.markdown("---")
                    st.warning("⚠️ Are you sure you want to send all selected invoices?")

                    col_confirm1, col_confirm2 = st.columns(2)
                    with col_confirm1:
                        if st.button("✅ Yes, Send Now", type="primary", use_container_width=True, key="confirm_send_all"):
                            # Ensure sender credentials are available
                            if not email_sender or not email_password:
                                st.error("❌ Please configure email sender credentials in the sidebar first.")
                            else:
                                success_count = 0
                                failure_count = 0

                                # Loop over each invoice customization and send it
                                for invoice_id, details in st.session_state.email_customizations.items():
                                    try:
                                        # Generate PDF for this invoice
                                        st.write(f"Handling Invoice {invoice_id}")
                                        pdf_url = print_invoice(invoice_id, 'json')
                                        response = requests.get(pdf_url)
                                        response.raise_for_status()

                                        # Wrap in BytesIO for email attachment
                                        pdf_data = BytesIO(response.content).read()

                                        # Send the email
                                        with st.spinner(f"📧 Sending invoice #{invoice_id} to {details['email']}..."):
                                            success, message = send_email_invoice(
                                                file_data=pdf_data,
                                                email_sender=email_sender,
                                                email_password=email_password,
                                                email_reciever=details["email"],
                                                subject=details["subject"],
                                                body=details["body"], 
                                                invoice_number=invoice_id
                                            )

                                        if success:
                                            st.success(f"✅ Invoice #{invoice_id} sent to {details['email']}")
                                            success_count += 1
                                        else:
                                            st.error(f"❌ Failed to send invoice #{invoice_id}: {message}")
                                            failure_count += 1

                                    except Exception as e:
                                        st.error(f"❌ Error sending invoice #{invoice_id}: {e}")
                                        failure_count += 1

                                st.info(f"📬 Sending complete: {success_count} succeeded, {failure_count} failed.")

 

                                # Reset form
                                st.session_state.show_email_form = False
                                st.session_state.confirm_send = False
                                st.session_state.email_customizations = {}
                                

                    with col_confirm2:
                        if st.button("❌ No, Cancel", use_container_width=True, key="cancel_send_all"):
                            st.session_state.confirm_send = False
                            st.rerun()



            else:
                st.warning("⚠️ Please select at least one invoice to download")
        else:
            st.info("No invoices found matching the selected filters")


























