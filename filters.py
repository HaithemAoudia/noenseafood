import pandas as pd


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
        

def apply_customer_filter(df, customers):
    if len(customers) == 0:
        return df
    else:
        return df[df["customer_name"].isin(customers)]
    

def apply_product_filter(df, products):
    if len(products) == 0:
        return df
    else:
        return df[df["product_name"].isin(products)]
    
def apply_invoice_filter(df, invoice_ids):
    if len(invoice_ids) == 0:
        return df
    else:
        return df[df["invoice_number"].isin(invoice_ids)]
    
def apply_account_filter(df, accounts):
    if len(accounts) == 0:
        return df
    else:
        return df[df["account"].isin(accounts)]