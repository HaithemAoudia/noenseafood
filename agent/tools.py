import json
import pandas as pd
from datetime import date
from typing import Optional
from langchain_core.tools import tool

from agent.embeddings import similarity_search
from filters import (
    apply_date_filter, apply_country_filter, apply_account_filter,
    apply_customer_filter, apply_product_filter, apply_invoice_filter,
    apply_invoice_status_filter, apply_product_family_filter,
)
from helpers import print_invoice


def create_tools(dataframes, product_embeddings, product_metadata, customer_embeddings, customer_metadata, model):

    df_product_sales = dataframes["df_product_sales_merged"].copy()
    df_invoices = dataframes["df_invoices"].copy()
    df_product_clean = dataframes["df_product_clean"].copy()

    @tool
    def get_current_date() -> str:
        """Returns today's date. Always call this first when the user's query
        involves a relative time period such as 'this year', 'this month',
        'year to date', 'last 30 days', or 'today'."""
        return date.today().isoformat()

    @tool
    def find_products(query: str) -> str:
        """Search for products by name using semantic similarity.
        Returns a JSON list of matching products with their IDs.
        Only to be used be the user explicitly mentioning a product name.
        Use this when you need to find exact product names or IDs."""
        results = similarity_search(query, product_embeddings, product_metadata, model, top_k=10)
        if not results:
            return "No products found."
        return json.dumps(results, ensure_ascii=False)

    @tool
    def find_customer(query: str) -> str:
        """Search for customers by name using semantic similarity.
        Returns a JSON list of matching customers with their IDs.
        Only to be used be the user explicitly mentioning a customer name. 
        Use this when you need to find exact customer names or IDs."""
        results = similarity_search(query, customer_embeddings, customer_metadata, model, top_k=1)
        if not results:
            return "No customers found."
        return json.dumps(results, ensure_ascii=False)

    @tool
    def get_product_sales(
        product_names: Optional[list[str]] = None,
        customer_names: Optional[list[str]] = None,
        product_family: Optional[str] = None,
        account: Optional[str] = None,
        country: Optional[str] = None,
        sort_order: str = "desc",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        group_by: str = "product_customer",
    ) -> str:
        """Query product sales data. Returns a pre-aggregated table (max 30 rows).
        Use find_products or find_customer first to get exact names before calling this.

        Args:
            product_names: List of exact product names from find_products
            customer_names: List of exact customer names from find_customer
            product_family: Product family name (e.g. "Filets", "HOSO", "Mollusken")
            account: Account filter ("NL" or "EU")
            country: Country filter
            sort_order: "desc" for top results by revenue, "asc" for bottom
            start_date: Start date YYYY-MM-DD
            end_date: End date YYYY-MM-DD
            group_by: Aggregation level — use "customer" for total revenue/quantity per customer
                      (e.g. "what is customer X's total revenue?"), "product" for totals per product,
                      or "product_customer" (default) for a breakdown by both
        """
        df = df_product_sales.copy()

        if start_date and end_date:
            try:
                df = apply_date_filter(df, start_date, end_date)
            except Exception:
                pass
        if product_names:
            df = apply_product_filter(df, product_names)
        if customer_names:
            df = apply_customer_filter(df, customer_names)
        if account:
            df = apply_account_filter(df, [account])
        if country and country != "All":
            df = apply_country_filter(df, country)
        if product_family:
            df = pd.merge(df, df_product_clean[["id", "item_family_name"]], left_on="item_id", right_on="id", how="left", suffixes=("", "_prod"))
            df = apply_product_family_filter(df, [product_family])

        if df.empty:
            return "No sales data found for the given filters."

        if group_by == "customer":
            agg = df.groupby("customer_name").agg(
                quantity=("quantity", "sum"),
                revenue=("total_order_line", "sum"),
            ).reset_index()
        elif group_by == "product":
            agg = df.groupby("product_name").agg(
                quantity=("quantity", "sum"),
                revenue=("total_order_line", "sum"),
            ).reset_index()
        else:
            agg = df.groupby(["product_name", "customer_name"]).agg(
                quantity=("quantity", "sum"),
                revenue=("total_order_line", "sum"),
            ).reset_index()

        ascending = sort_order == "asc"
        agg = agg.sort_values("revenue", ascending=ascending).head(30)
        agg["revenue"] = agg["revenue"].round(2)
        agg["quantity"] = agg["quantity"].round(1)

        return agg.to_markdown(index=False)

    @tool
    def get_invoice(
        invoice_number: Optional[str] = None,
        customer_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        payment_status: Optional[str] = None,
        account: Optional[str] = None,
    ) -> str:
        """Retrieve invoice information and PDF URLs.
        Use find_customer first to get exact customer name if needed.

        Args:
            invoice_number: Specific invoice number to look up
            customer_name: Exact customer name to filter by
            start_date: Start date YYYY-MM-DD
            end_date: End date YYYY-MM-DD
            payment_status: "Paid" or "Unpaid"
            account: Account filter ("NL" or "EU")
        """
        df = df_invoices.copy()

        if start_date and end_date:
            try:
                df = apply_date_filter(df, start_date, end_date)
            except Exception:
                pass
        if invoice_number:
            df = apply_invoice_filter(df, [invoice_number])
        if customer_name:
            df = apply_customer_filter(df, [customer_name])
        if account:
            df = apply_account_filter(df, [account])
        if payment_status:
            df = apply_invoice_status_filter(df, [payment_status])

        if df.empty:
            return "No invoices found for the given filters."

        df = df.head(10)
        results = []
        for i, (_, row) in enumerate(df.iterrows()):
            entry = {
                "invoice_id": str(row.get("invoice_id", "")),
                "invoice_number": str(row.get("invoice_number", "")),
                "customer_name": str(row.get("customer_name", "")),
                "amount": float(row.get("amount", 0)),
                "paid": float(row.get("paid", 0)),
                "date": str(row.get("date", "")),
            }
            if i < 5:
                try:
                    pdf_url = print_invoice(str(row["invoice_id"]), "json", df_invoices)
                    if pdf_url and not str(pdf_url).startswith("Error"):
                        entry["pdf_url"] = pdf_url
                except Exception:
                    pass
            results.append(entry)

        return json.dumps(results, ensure_ascii=False, default=str)

    return [get_current_date, find_products, find_customer, get_product_sales, get_invoice]
