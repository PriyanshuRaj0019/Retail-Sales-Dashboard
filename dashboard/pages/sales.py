"""Sales analysis page for the Retail Sales Analytics Dashboard."""

from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.filters import sidebar_filters
from utils.loader import load_data


MONTH_ORDER = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


st.set_page_config(
    page_title="Sales Analysis",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def format_currency(value: float) -> str:
    """Format values as currency."""
    return f"${value:,.0f}"


def style_figure(fig, height: int = 430):
    """Apply consistent chart styling."""
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Render the sales page."""
    apply_css()

    df = load_data()
    filtered_df = sidebar_filters(df)

    st.title("Sales Analysis")
    st.caption("Revenue trends, order patterns, and sales performance.")

    if filtered_df.empty:
        st.warning("No sales records match the selected filters.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenue", format_currency(filtered_df["Sales"].sum()))
    col2.metric("Average Sale", f"${filtered_df['Sales'].mean():,.2f}")
    col3.metric("Highest Sale", format_currency(filtered_df["Sales"].max()))
    col4.metric("Lowest Sale", format_currency(filtered_df["Sales"].min()))

    st.divider()

    monthly = (
        filtered_df.groupby(["Year", "Month Name"], sort=False)["Sales"]
        .sum()
        .reset_index()
    )
    monthly["Month Sort"] = monthly["Month Name"].map(
        {month: index for index, month in enumerate(MONTH_ORDER, start=1)}
    )
    monthly = monthly.sort_values(["Year", "Month Sort"])

    quarter = (
        filtered_df.groupby(["Year", "Quarter"], as_index=False)["Sales"]
        .sum()
    )

    subcategory = (
        filtered_df.groupby("Sub-Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=True)
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Monthly Sales Trend")
        fig = px.line(
            monthly,
            x="Month Name",
            y="Sales",
            color="Year",
            markers=True,
        )
        fig.update_xaxes(categoryorder="array", categoryarray=MONTH_ORDER)
        st.plotly_chart(style_figure(fig), use_container_width=True)

    with right:
        st.subheader("Quarterly Sales")
        fig = px.bar(
            quarter,
            x="Quarter",
            y="Sales",
            color="Year",
            barmode="group",
            text_auto=".2s",
        )
        st.plotly_chart(style_figure(fig), use_container_width=True)

    st.subheader("Sales by Sub-Category")
    fig = px.bar(
        subcategory,
        x="Sales",
        y="Sub-Category",
        orientation="h",
        color="Sales",
        color_continuous_scale="Blues",
        text_auto=".2s",
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(style_figure(fig, height=560), use_container_width=True)

    st.download_button(
        label="Download sales data as CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="sales_filtered_data.csv",
        mime="text/csv",
        use_container_width=True,
    )


main()