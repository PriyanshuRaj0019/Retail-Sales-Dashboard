def calculate_kpis(df):

    kpis = {

        "total_sales": df["Sales"].sum(),

        "avg_sales": df["Sales"].mean(),

        "total_orders": df["Order ID"].nunique(),

        "customers": df["Customer ID"].nunique(),

        "products": df["Product Name"].nunique(),

        "states": df["State"].nunique(),

        "cities": df["City"].nunique(),

        "categories": df["Category"].nunique()

    }

    return kpis
def sales_by_category(df):

    return (
        df.groupby("Category")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
def sales_by_region(df):

    return (
        df.groupby("Region")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
def monthly_sales(df):

    return (
        df.groupby(["Year", "Month Name"], sort=False)["Sales"]
        .sum()
        .reset_index()
    )
def top_products(df):

    return (
        df.groupby("Product Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
def top_customers(df):

    return (
        df.groupby("Customer Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
def top_states(df):

    return (
        df.groupby("State")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
