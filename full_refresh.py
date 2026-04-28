from pipeline.resources.load import full_data_load
import os

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



if __name__ == "__main__":
    full_data_load(type="invoices", sheet_name="OneUp - Invoices", google_cred=google_cred)
    print("✅ Invoices loaded successfully.")
    full_data_load(type="items", sheet_name="OneUp - Products", google_cred=google_cred)
    print("✅ Products loaded successfully.")
    full_data_load(type="customers", sheet_name="OneUp - Customers", google_cred=google_cred)
    print("✅ Customers loaded successfully.")
