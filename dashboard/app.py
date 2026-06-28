"""Main Streamlit entrypoint for the Retail Sales Analytics Dashboard."""

from pathlib import Path
import sys

import streamlit as st

# Make project-level packages importable when launched with:
# streamlit run dashboard/app.py
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.filters import sidebar_filters
from utils.loader import load_data
from utils.metrics import calculate_kpis


st.set_page_config(
    page_title="Retail Sales Analytics",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_css() -> None:
    """Apply shared dashboard styling."""
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

        .intro-panel {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            color: #334155;
            padding: 1.1rem 1.25rem;
            margin-bottom: 1.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    """Render a message when filters return no data."""
    st.warning(
        "No records match the selected filters. Adjust the sidebar filters "
        "to continue."
    )


def render_kpis(filtered_df) -> None:
    """Render landing-page KPI cards."""
    kpis = calculate_kpis(filtered_df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"${kpis['total_sales']:,.0f}")
    col2.metric("Orders", f"{kpis['total_orders']:,}")
    col3.metric("Customers", f"{kpis['customers']:,}")
    col4.metric("Products", f"{kpis['products']:,}")


def render_download(filtered_df) -> None:
    """Add CSV download for filtered records."""
    st.download_button(
        label="Download filtered data as CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="retail_sales_filtered.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    """Render the dashboard landing page."""
    apply_css()

    df = load_data()
    filtered_df = sidebar_filters(df)

    st.title("Retail Sales Analytics Dashboard")
    st.markdown(
        """
        <div class="intro-panel">
            Use the sidebar filters to scope the analysis, then open the pages
            menu to review executive, sales, customer, product, geography, and
            recommendation views.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if filtered_df.empty:
        render_empty_state()
        return

    render_kpis(filtered_df)
    st.divider()
    render_download(filtered_df)


if __name__ == "__main__":
    main()