"""Geography analysis page for the Retail Sales Analytics Dashboard."""

from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.filters import sidebar_filters
from utils.loader import load_data
from utils.metrics import top_states


st.set_page_config(
    page_title="Geography Analysis",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_css() -> None:
    """Apply professional page styling."""
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
    """Format values as currency."""
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
    """Show empty dataset guidance."""
    st.warning("No geography records match the selected filters.")


def render_kpis(df) -> None:
    """Render geography KPI cards."""
    total_sales = df["Sales"].sum()
    regions = df["Region"].nunique()
    states = df["State"].nunique()
    cities = df["City"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Geographic Sales", format_currency(total_sales))
    col2.metric("Regions", f"{regions:,}")
    col3.metric("States", f"{states:,}")
    col4.metric("Cities", f"{cities:,}")


def render_insights(df) -> None:
    """Render geography-focused business insights."""
    state_sales = df.groupby("State", as_index=False)["Sales"].sum()
    city_sales = df.groupby("City", as_index=False)["Sales"].sum()
    region_sales = df.groupby("Region", as_index=False)["Sales"].sum()

    top_state = state_sales.sort_values("Sales", ascending=False).iloc[0]
    top_city = city_sales.sort_values("Sales", ascending=False).iloc[0]
    top_region = region_sales.sort_values("Sales", ascending=False).iloc[0]
    region_share = top_region["Sales"] / df["Sales"].sum()

    st.markdown(
        f"""
        <div class="insight-box">
            <strong>{top_region['Region']}</strong> is the strongest region,
            contributing <strong>{format_currency(top_region['Sales'])}</strong>
            or <strong>{region_share:.1%}</strong> of filtered sales.
            The leading state is <strong>{top_state['State']}</strong>, while
            <strong>{top_city['City']}</strong> is the highest-performing city.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_charts(df) -> None:
    """Render geography charts."""
    region_sales = (
        df.groupby("Region", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    state_sales = top_states(df).sort_values("Sales", ascending=True)

    city_sales = (
        df.groupby(["City", "State"], as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
        .head(15)
        .sort_values("Sales", ascending=True)
    )

    ship_mode_region = (
        df.groupby(["Region", "Ship Mode"], as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Sales by Region")
        fig = px.bar(
            region_sales,
            x="Region",
            y="Sales",
            color="Region",
            text_auto=".2s",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_figure(fig), use_container_width=True)

    with right:
        st.subheader("Top States")
        fig = px.bar(
            state_sales,
            x="Sales",
            y="State",
            orientation="h",
            color="Sales",
            color_continuous_scale="Blues",
            text_auto=".2s",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_figure(fig), use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.subheader("Top Cities")
        fig = px.bar(
            city_sales,
            x="Sales",
            y="City",
            color="State",
            orientation="h",
            text_auto=".2s",
        )
        st.plotly_chart(style_figure(fig, height=500), use_container_width=True)

    with right:
        st.subheader("Ship Mode by Region")
        fig = px.bar(
            ship_mode_region,
            x="Region",
            y="Sales",
            color="Ship Mode",
            barmode="group",
            text_auto=".2s",
        )
        st.plotly_chart(style_figure(fig, height=500), use_container_width=True)


def render_download(df) -> None:
    """Add CSV download button."""
    st.download_button(
        label="Download geography data as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="geography_filtered_sales.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    """Render geography page."""
    apply_css()

    df = load_data()
    filtered_df = sidebar_filters(df)

    st.title("Geography Analysis")
    st.caption("Regional, state, and city-level sales performance.")

    if filtered_df.empty:
        render_empty_state()
        return

    render_kpis(filtered_df)
    st.divider()
    render_insights(filtered_df)
    render_charts(filtered_df)
    st.divider()
    render_download(filtered_df)


main()