import requests
import gspread
from requests.auth import HTTPBasicAuth
import os
import json
import smtplib
from email.message import EmailMessage
from google.oauth2.service_account import Credentials

def print_invoice(invoice_id, format):
    url = f"https://api.oneup.com/v1/invoices/{invoice_id}/print.{format}"
    API_EMAIL = os.getenv('API_EMAIL')
    API_KEY = os.getenv('API_KEY')
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