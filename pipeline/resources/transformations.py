import pandas as pd

def transform_invoices(data):

    records = []

    for invoice in data:
        # Extract invoice-level fields
        po_number = invoice.get("po_number")
        invoice_number = invoice.get("user_code")
        delivery_status = invoice.get("delivery_status")
        invoice_status = invoice.get("invoice_status")
        sent = invoice.get("sent")
        sent_at = invoice.get("sent_at")
        paid = invoice.get("paid")
        unpaid = invoice.get("unpaid")
        customer_id = invoice.get("customer_id")
        customer_name = invoice.get("customer", {}).get("name")
        date = invoice.get("date")

        
        billing = invoice.get("billing_address", {})
        country = billing.get("country")
        city = billing.get("city")
        postal_code = billing.get("postal_code")
        street_line = billing.get("street_line1")
        total_amount = invoice.get("total")

        
        # Each invoice may have multiple installments
        for installment in invoice.get("installments", []):
            invoice_id = installment.get("invoice_id")
            due_date = installment.get("due_date")
            amount = installment.get("amount")
            outstanding_amount = installment.get("outstanding_amount")
            created_at = installment.get("created_at")
            updated_at = installment.get("updated_at")
            
            # Each invoice may have multiple order lines
            for line in invoice.get("order_lines", []):
                record = {
                    "invoice_id": invoice_id,
                    "invoice_number": invoice_number,
                    "date": date,
                    "due_date": due_date,
                    "amount": amount,
                    "outstanding_amount": outstanding_amount,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "po_number": po_number,
                    "invoice_status": invoice_status,
                    "delivery_status": delivery_status,
                    "sent": sent,
                    "sent_at": sent_at,
                    "paid": paid,
                    "unpaid": unpaid,
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "country": country,
                    "city": city,
                    "postal_code": postal_code,
                    "street_line": street_line,
                    "order_line_id": line.get("id"),
                    "item_id": line.get("item_id"),
                    "item_description": line.get("description"),
                    "quantity": line.get("quantity"),
                    "unit_price": line.get("unit_price_wt"),
                    "total_order_line": line.get("total"),
                    "subtotal": invoice.get("subtotal"),
                    "tax_amount": invoice.get("tax_amount"),
                    "total": total_amount,
                    "source": "OneUp"
                }
                records.append(record)

    # Create DataFrame
    df = pd.DataFrame(records)

    return df



def transform_products(data):

    records = []

    for item in data:
        # --- Basic / top-level fields ---
        item_id = item.get("id")
        name = item.get("name")
        type_ = item.get("type")
        item_number = item.get("item_number")
        description = item.get("description")
        sales_price = item.get("sales_price")
        purchase_price = item.get("purchase_price")
        created_at = item.get("created_at")
        updated_at = item.get("updated_at")

        # --- Nested: unit ---
        unit_data = item.get("unit", {}) or {}
        unit_id = unit_data.get("id")
        unit_created_at = unit_data.get("created_at")
        unit_updated_at = unit_data.get("updated_at")

        # --- Nested: item family ---
        family_data = item.get("item_family", {}) or {}
        item_family_name = family_data.get("name")

        # --- Nested: COGS account ---
        cogs_data = item.get("cogs_account", {}) or {}
        cogs_account_name = cogs_data.get("name")
        cogs_account_id = cogs_data.get("id")

        # --- Nested: income account ---
        income_data = item.get("income_account", {}) or {}
        income_account_name = income_data.get("name")
        income_account_id = income_data.get("id")

        # --- Nested: purchase tax ---
        purchase_tax_data = item.get("purchase_tax", {}) or {}
        purchase_tax_name = purchase_tax_data.get("name")
        purchase_tax_rate = purchase_tax_data.get("rate")
        purchase_tax_id = purchase_tax_data.get("id")

        # --- Nested: sales tax ---
        sales_tax_data = item.get("sales_tax", {}) or {}
        sales_tax_name = sales_tax_data.get("name")
        sales_tax_rate = sales_tax_data.get("rate")
        sales_tax_id = sales_tax_data.get("id")

        records.append({
        "id": item_id,
        "created_at": created_at,
        "updated_at": updated_at,
        "unit_id": unit_id,
        "name": name,
        "type": type_,
        "unit_created_at": unit_created_at,
        "unit_updated_at": unit_updated_at,
        "sales_price": sales_price,
        "item_number": item_number,
        "description": description,
        "item_family_name": item_family_name,
        "purchase_price": purchase_price,
        "cogs_account_name": cogs_account_name,
        "cogs_account_id": cogs_account_id,
        "income_account_name": income_account_name,
        "income_account_id": income_account_id,
        "purchase_tax_name": purchase_tax_name,
        "purchase_tax_rate": purchase_tax_rate,
        "purchase_tax_id": purchase_tax_id,
        "sales_tax_name": sales_tax_name,
        "sales_tax_rate": sales_tax_rate,
        "sales_tax_id": sales_tax_id
    })
        # Create DataFrame
    df_items = pd.DataFrame(records)
    return df_items


def transform_customers(data):
    records = []

    for customer in data:
        # --- Top-level fields ---
        customer_id = customer.get("id")
        full_name = customer.get("full_name")
        created_at = customer.get("created_at")
        updated_at = customer.get("updated_at")
        email = customer.get("email")
        opt_in_email = customer.get("opt_in_email")
        industry = customer.get("industry")
        rating = customer.get("rating")

        # --- Nested: address ---
        address = customer.get("address", {}) or {}
        address_line1 = address.get("street_line1")
        postal_code = str(address.get("postal_code")) if address.get("postal_code") is not None else None
        city = address.get("city")
        country = address.get("country")

        # --- Nested: payment terms ---
        payment_terms = customer.get("payment_terms", {}) or {}
        payment_terms_name = payment_terms.get("name")
        payment_terms_id = payment_terms.get("id")

        # --- Nested: sales tax ---
        sales_tax = customer.get("sales_tax", {}) or {}
        sales_tax_id = sales_tax.get("id")
        sales_tax_name = sales_tax.get("name")
        sales_tax_enabled = sales_tax.get("enabled")

        # --- Nested: price family ---
        price_family = customer.get("price_family", {}) or {}
        price_family_standard = price_family.get("name")

        # --- Nested: accounting account ---
        accounting_account = customer.get("accounting_account", {}) or {}
        accounting_account_id = accounting_account.get("id")
 
        # --- Append flattened record ---
        records.append({
            "id": customer_id,
            "full_name": full_name,
            "created_at": created_at,
            "updated_at": updated_at,
            "address_line1": address_line1,
            "postal_code": postal_code,
            "city": city,
            "country": country,
            "email": email,
            "payment_terms_name": payment_terms_name,
            "payment_terms_id": payment_terms_id,
            "sales_tax_id": sales_tax_id,
            "sales_tax_name": sales_tax_name,
            "sales_tax_enabled": sales_tax_enabled,
            "opt_in_email": opt_in_email,
            "price_family_standard": price_family_standard,
            "industry": industry,
            "rating": rating,
            "accounting_account_id": accounting_account_id
        })

    # --- Create DataFrame AFTER the loop ---
    df_customers = pd.DataFrame(records)
    return df_customers
