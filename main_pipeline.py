from pipeline.resources.load import load_data


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
    load_data(type="invoices", sheet_name="OneUp - Invoices", nk="order_line_id", google_cred=google_cred)
    load_data(type="items", sheet_name="OneUp - Products", nk="id", google_cred=google_cred)
    load_data(type="customers", sheet_name="OneUp - Customers", nk="id", google_cred=google_cred)
