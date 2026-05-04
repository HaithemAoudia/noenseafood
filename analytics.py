import pandas as pd

def calculate_customer_metrics(df):
    """Calculate customer metrics"""
    if len(df) == 0:
        return pd.DataFrame(columns=["customer_name", "num_transactions", "total_revenue", "AOV", "transaction_frequency"])
    
    
    metrics = (
        df.groupby(["customer_name"], as_index=False)
        .agg({
            "invoice_id": "nunique",
            "total_order_line": "sum"
        })
        .rename(columns={"invoice_id": "num_transactions", "total_order_line": "total_revenue"})
    )
    
    metrics["AOV"] = metrics["total_revenue"] / metrics["num_transactions"]
    metrics["transaction_frequency"] = metrics["num_transactions"] / metrics["total_revenue"]
    
    return metrics

def calculate_product_metrics(df, df_product):
    """Calculate product metrics"""
    if len(df) == 0:
        return df
    
    df_merged = df.merge(
        df_product[["id", "purchase_price", "item_family_name"]].drop_duplicates("id"),
        how="left",
        left_on="item_id",
        right_on="id"
    )
    # df_merged = df_merged[df_merged["purchase_price"] > 0]
    df_merged = df_merged[df_merged["product_name"] != '']
    
    df_merged["total_cost"] = df_merged["purchase_price"] * df_merged["quantity"]
    df_merged["total_gross_margin"] = df_merged["total_order_line"] - df_merged["total_cost"]
    
    product_metrics = (
        df_merged.groupby(["product_name", "item_family_name", "customer_name"], as_index=False)
        .agg({
            "quantity": "sum",
            "total_order_line": "sum",
            "total_gross_margin": "sum"
        })
        .rename(columns={"total_order_line": "revenue"})
    )

    
    product_metrics["margin_%"] = (product_metrics["total_gross_margin"] / product_metrics["revenue"]) * 100
    product_metrics = product_metrics[product_metrics["margin_%"] > 0]
    product_metrics["margin_contribution_%"] = (
        (product_metrics["total_gross_margin"] / product_metrics["total_gross_margin"].sum()) * 100
    )
    
    return product_metrics