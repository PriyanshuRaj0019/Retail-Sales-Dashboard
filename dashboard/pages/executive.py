"""Executive overview page for the Retail Sales Analytics Dashboard."""

from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

# Ensure imports work when Streamlit runs this as a multipage app.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.filters import sidebar_filters
from utils.charts import category_chart, monthly_sales_chart, region_chart
from utils.loader import load_data
from utils.metrics import (
    calculate_kpis,
    monthly_sales,
    sales_by_category,
    sales_by_region,
    top_customers,
    top_products,
)


MONTH_ORDER = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


st.set_page_config(
    page_title="Executive Overview",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_css() -> None:
    """Apply dashboard-level styling."""
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

        h1, h2, h3 {
            color: #111827;
            letter-spacing: 0;
        }

        .section-note {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            color: #334155;
            padding: 1rem 1.15rem;
            margin: 0.5rem 0 1.25rem 0;
        }

        .insight-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-left: 4px solid #2563eb;
            border-radius: 8px;
            padding: 1rem 1.15rem;
            min-height: 104px;
        }

        .insight-title {
            color: #0f172a;
            font-size: 0.92rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .insight-text {
            color: #475569;
            font-size: 0.95rem;
            line-height: 1.45;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_currency(value: float) -> str:
    """Format a number as compact US currency."""
    return f"${value:,.0f}"


def render_empty_state() -> None:
    """Render a clear message when filters remove all records."""
    st.warning(
        "No records match the selected filters. Adjust the sidebar filters "
        "to restore the executive dashboard."
    )


def prepare_monthly_sales(df):
    """Return monthly sales sorted in calendar order."""
    monthly_df = monthly_sales(df)
    monthly_df["Month Name"] = monthly_df["Month Name"].astype(str)
    monthly_df["Month Sort"] = monthly_df["Month Name"].map(
        {month: index for index, month in enumerate(MONTH_ORDER, start=1)}
    )
    return monthly_df.sort_values(["Year", "Month Sort"])


def style_figure(fig, height: int = 420):
    """Apply common Plotly presentation settings."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=50, b=30),
        font=dict(family="Arial", size=12, color="#334155"),
        legend_title_text="",
    )
    return fig


def render_kpis(df) -> None:
    """Render executive KPI cards."""
    kpis = calculate_kpis(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", format_currency(kpis["total_sales"]))
    col2.metric("Orders", f"{kpis['total_orders']:,}")
    col3.metric("Customers", f"{kpis['customers']:,}")
    col4.metric("Products", f"{kpis['products']:,}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Average Sale", format_currency(kpis["avg_sales"]))
    col6.metric("States", f"{kpis['states']:,}")
    col7.metric("Cities", f"{kpis['cities']:,}")
    col8.metric("Categories", f"{kpis['categories']:,}")


def render_insights(df) -> None:
    """Generate concise business insights from the filtered data."""
    total_sales = df["Sales"].sum()
    top_category = sales_by_category(df).iloc[0]
    top_region = sales_by_region(df).iloc[0]
    best_customer = top_customers(df).iloc[0]
    avg_shipping_days = df["Shipping Days"].mean()

    category_share = top_category["Sales"] / total_sales
    region_share = top_region["Sales"] / total_sales

    insights = [
        (
            "Category Leader",
            (
                f"{top_category['Category']} leads sales with "
                f"{format_currency(top_category['Sales'])}, representing "
                f"{category_share:.1%} of filtered revenue."
            ),
        ),
        (
            "Regional Concentration",
            (
                f"The {top_region['Region']} region contributes "
                f"{format_currency(top_region['Sales'])}, equal to "
                f"{region_share:.1%} of filtered revenue."
            ),
        ),
        (
            "Customer Value",
            (
                f"{best_customer['Customer Name']} is the highest-value "
                f"customer in this view with {format_currency(best_customer['Sales'])} "
                "in sales."
            ),
        ),
        (
            "Fulfillment Signal",
            (
                f"Average shipping time is {avg_shipping_days:.1f} days. "
                "Monitor this alongside sales growth to protect customer experience."
            ),
        ),
    ]

    cols = st.columns(4)
    for col, (title, text) in zip(cols, insights):
        with col:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-title">{title}</div>
                    <div class="insight-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_charts(df) -> None:
    """Render the main executive charts."""
    monthly_df = prepare_monthly_sales(df)
    category_df = sales_by_category(df)
    region_df = sales_by_region(df)

    left, right = st.columns(2)

    with left:
        st.subheader("Monthly Sales Trend")
        fig = monthly_sales_chart(monthly_df)
        fig.update_xaxes(categoryorder="array", categoryarray=MONTH_ORDER)
        st.plotly_chart(style_figure(fig), use_container_width=True)

    with right:
        st.subheader("Sales by Category")
        fig = category_chart(category_df)
        st.plotly_chart(style_figure(fig), use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.subheader("Sales by Region")
        fig = region_chart(region_df)
        st.plotly_chart(style_figure(fig), use_container_width=True)

    with right:
        st.subheader("Sales by Segment")
        segment_df = df.groupby("Segment", as_index=False)["Sales"].sum()
        fig = px.pie(
            segment_df,
            names="Segment",
            values="Sales",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(style_figure(fig), use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.subheader("Top Products")
        product_df = top_products(df).sort_values("Sales", ascending=True)
        fig = px.bar(
            product_df,
            x="Sales",
            y="Product Name",
            orientation="h",
            text_auto=".2s",
            color="Sales",
            color_continuous_scale="Blues",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_figure(fig, height=460), use_container_width=True)

    with right:
        st.subheader("Top Customers")
        customer_df = top_customers(df).sort_values("Sales", ascending=True)
        fig = px.bar(
            customer_df,
            x="Sales",
            y="Customer Name",
            orientation="h",
            text_auto=".2s",
            color="Sales",
            color_continuous_scale="Greens",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_figure(fig, height=460), use_container_width=True)


def render_download(df) -> None:
    """Add a CSV export for the current filtered dataset."""
    st.download_button(
        label="Download filtered data as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="executive_filtered_sales.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    """Render the executive dashboard page."""
    apply_css()

    df = load_data()
    filtered_df = sidebar_filters(df)

    st.title("Executive Overview")
    st.markdown(
        """
        <div class="section-note">
            A leadership summary of sales performance, customer demand,
            product contribution, and regional concentration based on the
            current sidebar filters.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if filtered_df.empty:
        render_empty_state()
        return

    render_kpis(filtered_df)
    st.divider()

    st.subheader("Business Insights")
    render_insights(filtered_df)
    st.divider()

    render_charts(filtered_df)
    st.divider()

    render_download(filtered_df)


main()