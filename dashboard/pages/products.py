"""Product analysis page for the Retail Sales Analytics Dashboard."""

from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.filters import sidebar_filters
from utils.loader import load_data
from utils.metrics import sales_by_category, top_products


st.set_page_config(
    page_title="Product Analysis",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_css() -> None:
    """Apply page styling."""
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1280px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        div[data-testid="metric-container"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
            padding: 1rem;
        }

        .insight-box {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1rem 1.15rem;
            color: #334155;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_currency(value: float) -> str:
    """Format currency values."""
    return f"${value:,.0f}"


def style_figure(fig, height: int = 430):
    """Apply common chart styling."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=50, b=30),
        font=dict(family="Arial", size=12, color="#334155"),
        legend_title_text="",
    )
    return fig


def render_empty_state() -> None:
    """Show message when filtered data is empty."""
    st.warning("No product records match the selected filters.")


def render_kpis(df) -> None:
    """Render product KPI cards."""
    total_sales = df["Sales"].sum()
    products = df["Product Name"].nunique()
    categories = df["Category"].nunique()
    subcategories = df["Sub-Category"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Product Sales", format_currency(total_sales))
    col2.metric("Products", f"{products:,}")
    col3.metric("Categories", f"{categories:,}")
    col4.metric("Sub-Categories", f"{subcategories:,}")


def render_insights(df) -> None:
    """Render product insights."""
    category_sales = sales_by_category(df)
    product_sales = top_products(df)

    top_category = category_sales.iloc[0]
    top_product = product_sales.iloc[0]
    category_share = top_category["Sales"] / df["Sales"].sum()

    st.markdown(
        f"""
        <div class="insight-box">
            <strong>{top_category['Category']}</strong> is the leading category
            with <strong>{format_currency(top_category['Sales'])}</strong>,
            representing <strong>{category_share:.1%}</strong> of filtered sales.
            The top product is <strong>{top_product['Product Name']}</strong>
            with <strong>{format_currency(top_product['Sales'])}</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_charts(df) -> None:
    """Render product performance charts."""
    category_sales = sales_by_category(df)

    subcategory_sales = (
        df.groupby("Sub-Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=True)
    )

    product_sales = top_products(df).sort_values("Sales", ascending=True)

    category_subcategory = (
        df.groupby(["Category", "Sub-Category"], as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Sales by Category")
        fig = px.bar(
            category_sales,
            x="Category",
            y="Sales",
            color="Category",
            text_auto=".2s",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_figure(fig), use_container_width=True)

    with right:
        st.subheader("Category Mix")
        fig = px.pie(
            category_sales,
            names="Category",
            values="Sales",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(style_figure(fig), use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.subheader("Sales by Sub-Category")
        fig = px.bar(
            subcategory_sales,
            x="Sales",
            y="Sub-Category",
            orientation="h",
            color="Sales",
            color_continuous_scale="Blues",
            text_auto=".2s",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_figure(fig, height=520), use_container_width=True)

    with right:
        st.subheader("Top Products")
        fig = px.bar(
            product_sales,
            x="Sales",
            y="Product Name",
            orientation="h",
            color="Sales",
            color_continuous_scale="Greens",
            text_auto=".2s",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_figure(fig, height=520), use_container_width=True)

    st.subheader("Category and Sub-Category Contribution")
    fig = px.treemap(
        category_subcategory,
        path=["Category", "Sub-Category"],
        values="Sales",
        color="Sales",
        color_continuous_scale="Teal",
    )
    st.plotly_chart(style_figure(fig, height=560), use_container_width=True)


def render_product_table(df) -> None:
    """Render detailed product summary table."""
    product_table = (
        df.groupby(["Category", "Sub-Category", "Product Name"], as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Orders=("Order ID", "nunique"),
            Customers=("Customer ID", "nunique"),
        )
        .sort_values("Sales", ascending=False)
    )

    product_table["Sales"] = product_table["Sales"].round(2)

    st.subheader("Product Summary")
    st.dataframe(product_table, use_container_width=True, hide_index=True)


def render_download(df) -> None:
    """Add CSV download button."""
    st.download_button(
        label="Download product data as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="product_filtered_sales.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    """Render products page."""
    apply_css()

    df = load_data()
    filtered_df = sidebar_filters(df)

    st.title("Product Analysis")
    st.caption("Category, sub-category, and product-level performance.")

    if filtered_df.empty:
        render_empty_state()
        return

    render_kpis(filtered_df)
    st.divider()
    render_insights(filtered_df)
    render_charts(filtered_df)
    render_product_table(filtered_df)
    st.divider()
    render_download(filtered_df)


main()