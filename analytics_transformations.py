import os
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from config import get_secret
from dotenv import load_dotenv


load_dotenv('noenseafood.env')



google_cred = {
    'type': get_secret('TYPE'),
    'project_id': get_secret('PROJECT_ID'),
    'private_key_id': get_secret('PRIVATE_KEY_ID'),
    'private_key': get_secret('PRIVATE_KEY').replace('\\n', '\n') if get_secret('PRIVATE_KEY') else None,
    'client_email': get_secret('CLIENT_EMAIL'),
    'client_id': get_secret('CLIENT_ID'),
    'auth_uri': get_secret('AUTH_URI'),
    'token_uri': get_secret('TOKEN_URI'),
    'auth_provider_x509_cert_url': get_secret('AUTH_PROVIDER_X509_CERT_URL'),
    'client_x509_cert_url': get_secret('CLIENT_X509_CERT_URL'),
    'universe_domain': get_secret('UNIVERSE_DOMAIN'),
}


def load_data():
        """Load and cache data from Google Sheets"""
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(google_cred, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet_id = get_secret('SHEET_ID')
        workbook = client.open_by_key(sheet_id)  
        
        df_sales = pd.DataFrame(workbook.worksheet("OneUp - Invoices").get_all_records()).drop_duplicates()
        df_product = pd.DataFrame(workbook.worksheet("OneUp - Products").get_all_records()).drop_duplicates()
        df_customers = pd.DataFrame(workbook.worksheet("OneUp - Customers").get_all_records()).drop_duplicates()
        df_transactions_sumup = pd.DataFrame(workbook.worksheet("SumUp - Product Transaction").get_all_records()).drop_duplicates()
        df_product_inventory_analysis = pd.DataFrame(workbook.worksheet("Product Inventory Consumption - Merged").get_all_records()).drop_duplicates()
        df_product_inventory = pd.DataFrame(workbook.worksheet("Product Inventory").get_all_records()).drop_duplicates()
        return df_sales, df_product, df_customers, df_transactions_sumup, df_product_inventory_analysis, df_product_inventory


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

        # Add product name to sales orders
        df_sales_order = pd.merge(
            df_sales_order,
            df_product[["id", "name"]],
            left_on="item_id",
            right_on="id",
            how="left"
        ).drop(columns="id")
        df_sales_order.rename(columns={"name": "product_name"}, inplace=True)


        # Create invoices metadata dataframe
        df_invoices = df_sales[
            ["invoice_id", "customer_name", "country", "city", "date", "due_date", "updated_at", "amount", "sent", "paid", "source"]
        ].sort_values("updated_at", ascending=False).drop_duplicates("invoice_id")

        # SumUp sales
        df_sales_sumup = df_transactions_sumup[
            ["id", "date", "total_price", "product_name", "customer_name", "country", "city", "source"]
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

# Save to google sheets
def save_to_google_sheets(df: pd.DataFrame, sheet_name: str):
    """Save DataFrame to Google Sheets"""
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(google_cred, scopes=scope)
    client = gspread.authorize(creds)
    
    sheet_id = "1IwUYDdmj7nPgii-zCTjwXJRyP7Szhvc_qu9HANMB4hI"
    workbook = client.open_by_key(sheet_id)
    
    try:
        worksheet = workbook.worksheet(sheet_name)
        workbook.del_worksheet(worksheet)
    except gspread.exceptions.WorksheetNotFound:
        pass
    
    worksheet = workbook.add_worksheet(title=sheet_name, rows="1000", cols="20")
    
    # Set the header
    worksheet.append_row(df.columns.tolist())
    
    # Append the data
    for row in df.itertuples(index=False):
        worksheet.append_row(list(row))


# Example usage:
save_to_google_sheets(df_sales_order_merged, "sales orders")

print(df_sales_order_merged.head(10))
