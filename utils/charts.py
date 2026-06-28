import plotly.express as px

def monthly_sales_chart(df):

    fig = px.line(
        df,
        x="Month Name",
        y="Sales",
        color="Year",
        markers=True
    )

    fig.update_layout(
        template="plotly_white",
        height=450
    )

    return fig

def category_chart(df):

    fig = px.bar(
        df,
        x="Category",
        y="Sales",
        color="Category",
        text_auto=".2s"
    )

    fig.update_layout(
        template="plotly_white",
        showlegend=False
    )

    return fig

def region_chart(df):

    fig = px.bar(
        df,
        x="Region",
        y="Sales",
        color="Region",
        text_auto=".2s"
    )

    return fig

def top_product_chart(df):

    fig = px.bar(
        df,
        x="Sales",
        y="Product Name",
        orientation="h",
        text_auto=".2s"
    )

    return fig

