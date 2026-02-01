from pipeline.resources.load import load_data


if __name__ == "__main__":
    load_data(type="invoices", sheet_name="OneUp - Invoices", nk="order_line_id")
    load_data(type="items", sheet_name="OneUp - Products", nk="id")
    load_data(type="customers", sheet_name="OneUp - Customers", nk="id")