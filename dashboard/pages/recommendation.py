"""Business recommendations page for the Retail Sales Analytics Dashboard."""

from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.filters import sidebar_filters
from utils.loader import load_data


st.set_page_config(
    page_title="Recommendations",
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

        .recommendation-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-left: 4px solid #2563eb;
            border-radius: 8px;
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
        }

        .recommendation-title {
            color: #0f172a;
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .recommendation-text {
            color: #475569;
            font-size: 0.95rem;
            line-height: 1.45;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_currency(value: float) -> str:
    """Format numbers as currency."""
    return f"${value:,.0f}"


def style_figure(fig, height: int = 430):
    """Apply shared Plotly styling."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=50, b=30),
        font=dict(family="Arial", size=12, color="#334155"),
        legend_title_text="",
    )
    return fig


def render_empty_state() -> None:
    """Render empty-state guidance."""
    st.warning("No records match the selected filters.")


def build_recommendations(df) -> list[tuple[str, str]]:
    """Create practical recommendations from filtered sales data."""
    total_sales = df["Sales"].sum()

    category_sales = (
        df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    region_sales = (
        df.groupby("Region", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    segment_sales = (
        df.groupby("Segment", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    subcategory_sales = (
        df.groupby("Sub-Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    slow_shipping = (
        df.groupby("Ship Mode", as_index=False)
        .agg(Sales=("Sales", "sum"), Average_Shipping_Days=("Shipping Days", "mean"))
        .sort_values("Average_Shipping_Days", ascending=False)
    )

    top_category = category_sales.iloc[0]
    top_region = region_sales.iloc[0]
    top_segment = segment_sales.iloc[0]
    top_subcategory = subcategory_sales.iloc[0]
    slowest_ship_mode = slow_shipping.iloc[0]

    category_share = top_category["Sales"] / total_sales
    region_share = top_region["Sales"] / total_sales

    return [
        (
            "Prioritize the strongest category",
            (
                f"{top_category['Category']} generates "
                f"{format_currency(top_category['Sales'])}, equal to "
                f"{category_share:.1%} of filtered sales. Increase visibility, "
                "inventory readiness, and promotional focus for this category."
            ),
        ),
        (
            "Protect the leading region",
            (
                f"The {top_region['Region']} region contributes "
                f"{format_currency(top_region['Sales'])}, or {region_share:.1%} "
                "of sales. Maintain service quality here while using its product "
                "mix as a benchmark for weaker regions."
            ),
        ),
        (
            "Target the highest-value customer segment",
            (
                f"The {top_segment['Segment']} segment is the strongest buyer group "
                f"with {format_currency(top_segment['Sales'])} in sales. Build "
                "segment-specific campaigns and bundles around its purchase behavior."
            ),
        ),
        (
            "Expand winning sub-categories",
            (
                f"{top_subcategory['Sub-Category']} is the top sub-category at "
                f"{format_currency(top_subcategory['Sales'])}. Feature it in "
                "cross-sell recommendations and use it to anchor category-level offers."
            ),
        ),
        (
            "Monitor fulfillment experience",
            (
                f"{slowest_ship_mode['Ship Mode']} has the longest average shipping "
                f"time at {slowest_ship_mode['Average_Shipping_Days']:.1f} days. "
                "Review carrier performance and customer expectations for this mode."
            ),
        ),
    ]


def render_kpis(df) -> None:
    """Render recommendation KPI cards."""
    total_sales = df["Sales"].sum()
    orders = df["Order ID"].nunique()
    customers = df["Customer ID"].nunique()
    avg_shipping_days = df["Shipping Days"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sales Reviewed", format_currency(total_sales))
    col2.metric("Orders Reviewed", f"{orders:,}")
    col3.metric("Customers Reviewed", f"{customers:,}")
    col4.metric("Avg Shipping Days", f"{avg_shipping_days:.1f}")


def render_recommendations(df) -> None:
    """Render business recommendation cards."""
    recommendations = build_recommendations(df)

    for title, text in recommendations:
        st.markdown(
            f"""
            <div class="recommendation-card">
                <div class="recommendation-title">{title}</div>
                <div class="recommendation-text">{text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_opportunity_charts(df) -> None:
    """Render supporting opportunity charts."""
    category_region = (
        df.groupby(["Region", "Category"], as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    segment_category = (
        df.groupby(["Segment", "Category"], as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    shipping = (
        df.groupby("Ship Mode", as_index=False)
        .agg(Sales=("Sales", "sum"), Average_Shipping_Days=("Shipping Days", "mean"))
        .sort_values("Sales", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Regional Category Opportunity")
        fig = px.bar(
            category_region,
            x="Region",
            y="Sales",
            color="Category",
            barmode="group",
            text_auto=".2s",
        )
        st.plotly_chart(style_figure(fig), use_container_width=True)

    with right:
        st.subheader("Segment Category Fit")
        fig = px.bar(
            segment_category,
            x="Segment",
            y="Sales",
            color="Category",
            barmode="group",
            text_auto=".2s",
        )
        st.plotly_chart(style_figure(fig), use_container_width=True)

    st.subheader("Shipping Mode Performance")
    fig = px.scatter(
        shipping,
        x="Average_Shipping_Days",
        y="Sales",
        size="Sales",
        color="Ship Mode",
        hover_name="Ship Mode",
        text="Ship Mode",
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(style_figure(fig, height=500), use_container_width=True)


def render_action_table(df) -> None:
    """Render a ranked action table for business users."""
    action_table = (
        df.groupby(["Region", "Category", "Sub-Category"], as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Orders=("Order ID", "nunique"),
            Customers=("Customer ID", "nunique"),
            Average_Shipping_Days=("Shipping Days", "mean"),
        )
        .sort_values("Sales", ascending=False)
        .head(20)
    )

    action_table["Sales"] = action_table["Sales"].round(2)
    action_table["Average_Shipping_Days"] = action_table[
        "Average_Shipping_Days"
    ].round(1)

    st.subheader("Priority Action Areas")
    st.dataframe(action_table, use_container_width=True, hide_index=True)


def render_download(df) -> None:
    """Add CSV download button."""
    st.download_button(
        label="Download recommendation data as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="recommendation_filtered_sales.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    """Render recommendations page."""
    apply_css()

    df = load_data()
    filtered_df = sidebar_filters(df)

    st.title("Business Recommendations")
    st.caption("Data-backed actions for sales growth, customer focus, and operations.")

    if filtered_df.empty:
        render_empty_state()
        return

    render_kpis(filtered_df)
    st.divider()

    st.subheader("Recommended Actions")
    render_recommendations(filtered_df)
    st.divider()

    render_opportunity_charts(filtered_df)
    render_action_table(filtered_df)
    st.divider()
    render_download(filtered_df)


main()