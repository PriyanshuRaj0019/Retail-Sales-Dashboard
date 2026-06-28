import streamlit as st


def sidebar_filters(df):

    st.sidebar.header("Dashboard Filters")

    years = sorted(df["Year"].unique())

    selected_year = st.sidebar.multiselect(
        "Year",
        years,
        default=years
    )

    regions = sorted(df["Region"].unique())

    selected_region = st.sidebar.multiselect(
        "Region",
        regions,
        default=regions
    )

    categories = sorted(df["Category"].unique())

    selected_category = st.sidebar.multiselect(
        "Category",
        categories,
        default=categories
    )

    segments = sorted(df["Segment"].unique())

    selected_segment = st.sidebar.multiselect(
        "Segment",
        segments,
        default=segments
    )

    filtered_df = df[
        (df["Year"].isin(selected_year)) &
        (df["Region"].isin(selected_region)) &
        (df["Category"].isin(selected_category)) &
        (df["Segment"].isin(selected_segment))
    ]

    return filtered_df

