"""Reusable business insight helpers for the dashboard."""


def generate_insights(df) -> list[str]:
    """Generate concise business insights from a filtered sales dataframe."""
    if df.empty:
        return ["No records are available for the selected filters."]

    top_region = df.groupby("Region")["Sales"].sum().idxmax()
    top_category = df.groupby("Category")["Sales"].sum().idxmax()
    top_product = df.groupby("Product Name")["Sales"].sum().idxmax()

    return [
        f"Highest sales are generated from the {top_region} region.",
        f"{top_category} is the best-performing category.",
        f"The top-selling product is {top_product}.",
        (
            "Recommendation: increase inventory and promotion focus for the "
            "top-performing category in the strongest region."
        ),
    ]