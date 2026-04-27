import requests
import gspread
from requests.auth import HTTPBasicAuth
import os
import json
import smtplib
from email.message import EmailMessage
from google.oauth2.service_account import Credentials
from config import get_secret
def print_invoice(invoice_id, format, df):
    url = f"https://api.oneup.com/v1/invoices/{invoice_id}/print.{format}"

    account = df[df["invoice_id"] == invoice_id]["account"].values[0]

    if account == "EU":
        API_EMAIL = get_secret('API_EMAIL_EU')
        API_KEY = get_secret('API_KEY_EU')
    elif account == "NL":   
        API_EMAIL = get_secret('API_EMAIL_NL')
        API_KEY = get_secret('API_KEY_NL')
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
    token = get_secret('GITHUB_API')      
    owner = "haithemaoudia"
    repo = "noenseafood"
    workflow = "actions.yaml"                
    branch = "master"                        

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

    return response.status_code

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
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(google_cred, scopes=scope)
    client = gspread.authorize(creds)
    
    sheet_id = get_secret('SHEET_ID')
    workbook = client.open_by_key(sheet_id)
    sheet = workbook.worksheet("Product Inventory")
    
    row = sheet.find(product_name).row
    quantity_available = sheet.get(f"X{row}")[0][0]
    return int(quantity_available)