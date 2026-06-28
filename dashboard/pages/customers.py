"""Customer analysis page for the Retail Sales Analytics Dashboard."""

from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.filters import sidebar_filters
from utils.loader import load_data
from utils.metrics import top_customers


st.set_page_config(
    page_title="Customer Analysis",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def format_currency(value: float) -> str:
    """Format values as currency."""
    return f"${value:,.0f}"


def style_figure(fig, height: int = 430):
    """Apply consistent Plotly styling."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=50, b=30),
        font=dict(family="Arial", size=12, color="#334155"),
        legend_title_text="",
    )
    return fig


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
            color: #334155;
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Render the customers page."""
    apply_css()

    df = load_data()
    filtered_df = sidebar_filters(df)

    st.title("Customer Analysis")
    st.caption("Customer contribution, segment mix, and high-value accounts.")

    if filtered_df.empty:
        st.warning("No customer records match the selected filters.")
        return

    total_sales = filtered_df["Sales"].sum()
    customer_count = filtered_df["Customer ID"].nunique()
    order_count = filtered_df["Order ID"].nunique()
    average_customer_value = total_sales / customer_count

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Customer Sales", format_currency(total_sales))
    col2.metric("Customers", f"{customer_count:,}")
    col3.metric("Orders", f"{order_count:,}")
    col4.metric("Avg Customer Value", format_currency(average_customer_value))

    customer_sales = top_customers(filtered_df).sort_values(
        "Sales",
        ascending=True,
    )

    segment_sales = (
        filtered_df.groupby("Segment", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    customer_orders = (
        filtered_df.groupby("Customer Name", as_index=False)
        .agg(Sales=("Sales", "sum"), Orders=("Order ID", "nunique"))
        .sort_values("Orders", ascending=False)
        .head(15)
        .sort_values("Orders", ascending=True)
    )

    top_customer = customer_sales.sort_values("Sales", ascending=False).iloc[0]
    top_segment = segment_sales.iloc[0]

    st.markdown(
        f"""
        <div class="insight-box">
            <strong>{top_customer['Customer Name']}</strong> is the top customer
            with <strong>{format_currency(top_customer['Sales'])}</strong> in sales.
            The strongest segment is <strong>{top_segment['Segment']}</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Top Customers by Sales")
        fig = px.bar(
            customer_sales,
            x="Sales",
            y="Customer Name",
            orientation="h",
            color="Sales",
            color_continuous_scale="Greens",
            text_auto=".2s",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_figure(fig, height=500), use_container_width=True)

    with right:
        st.subheader("Sales by Segment")
        fig = px.pie(
            segment_sales,
            names="Segment",
            values="Sales",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(style_figure(fig, height=500), use_container_width=True)

    st.subheader("Most Frequent Customers")
    fig = px.bar(
        customer_orders,
        x="Orders",
        y="Customer Name",
        orientation="h",
        color="Sales",
        color_continuous_scale="Blues",
        text_auto=True,
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(style_figure(fig, height=560), use_container_width=True)

    st.download_button(
        label="Download customer data as CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="customer_filtered_data.csv",
        mime="text/csv",
        use_container_width=True,
    )


main()