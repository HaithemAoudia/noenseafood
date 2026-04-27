
from .extraction import fetch_data
from .transformations import transform_invoices, transform_products, transform_customers
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from google.oauth2.service_account import Credentials
import gspread
import time
from dotenv import load_dotenv
import os





def load_data(type, sheet_name, nk, google_cred):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(google_cred, scopes=scopes)
    client = gspread.authorize(creds)

    sheet_id = os.getenv("SHEET_ID")
    workbook = client.open_by_key(sheet_id)
    sheet = workbook.worksheet(sheet_name)
    next_row = len(sheet.get_all_values())
    batch_size = 100
    header = False
    df_current = get_as_dataframe(workbook.worksheet(sheet_name))
    current_nks = df_current[nk].dropna().unique().tolist()

    for account in ["EU", "NL"]:
        offset = 0
        if account == "EU":
            API_EMAIL = os.getenv("API_EMAIL_EU")
            API_KEY = os.getenv("API_KEY_EU")
        elif account == "NL":
            API_EMAIL = os.getenv("API_EMAIL_NL")
            API_KEY = os.getenv("API_KEY_NL")
        while True:
            try:
                #fetch data from API
                json = fetch_data(type=type, limit="100", offset=f"{offset}", API_EMAIL=API_EMAIL, API_KEY=API_KEY)

                if not json:
                        print("No data returned — finished.")
                        break

                #transform json to pandas df
                if type == 'invoices':
                    df = transform_invoices(json)
                elif type == 'items':
                    df = transform_products(json)
                elif type == 'customers':
                    df = transform_customers(json)
                # Add source column
                df['source'] = 'OneUp'

                df = df[~df[nk].isin(current_nks)]


                if df.empty:
                        print(f"No more new data found at offset {offset}. Stopping.")
                        break

                #append 100 rows to excel sheet

                df["account"] = account
                
                print(df[nk].tolist()[0])

                set_with_dataframe(sheet, df, row=next_row, include_column_header=header)


                next_row = len(sheet.get_all_values()) + 1
                offset += batch_size


                print(f"Uploaded {len(df)} rows (offset={offset})")

                time.sleep(0.3)


            except Exception as e:
                print(f"⚠️ Error at offset {offset}: {e}")
                time.sleep(2)
                continue
        print(f"Finished loading data for account: {account}")
    print("✅ Data loading complete for sheet:", sheet_name)





def full_data_load(type, sheet_name, google_cred):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(google_cred, scopes=scopes)
    client = gspread.authorize(creds)

    sheet_id = os.getenv("SHEET_ID")
    workbook = client.open_by_key(sheet_id)
    sheet = workbook.worksheet(sheet_name)
    sheet.clear() 
    next_row = len(sheet.get_all_values())
    offset = 0
    batch_size = 100
    header = True

    for account in ["EU", "NL"]:
        offset = 0
        if account == "EU":
            API_EMAIL = os.getenv("API_EMAIL_EU")
            API_KEY = os.getenv("API_KEY_EU")
        elif account == "NL":
            API_EMAIL = os.getenv("API_EMAIL_NL")
            API_KEY = os.getenv("API_KEY_NL")
        while True:
            try:
                #fetch data from API
                json = fetch_data(type="invoices", limit="100", offset=f"{offset}", API_EMAIL=API_EMAIL, API_KEY=API_KEY)

                if not json:
                        print("No data returned — finished.")
                        break

                #transform json to pandas df
                if type == 'invoices':
                    df = transform_invoices(json)
                elif type == 'items':
                    df = transform_products(json)
                elif type == 'customers':
                    df = transform_customers(json)

                # Check if there are any row where created date is not 2025 for invoices
                if type == 'invoices':
                    df = df[df["created_at"] > "2025-01-01"]


                if df.empty:
                        print(f"No more data found at offset {offset}. Stopping.")
                        break

                #append 100 rows to excel sheet

                df["account"] = account

                set_with_dataframe(sheet, df, row=next_row, include_column_header=header)

                header = False

                next_row = len(sheet.get_all_values()) + 1
                offset += batch_size


                print(f"Uploaded {len(df)} rows (offset={offset})")

                # time.sleep(0.3)


            except Exception as e:
                print(f"⚠️ Error at offset {offset}: {e}")
                time.sleep(2)
                continue
