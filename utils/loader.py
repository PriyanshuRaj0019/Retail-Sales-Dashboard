import streamlit as st
import pandas as pd


@st.cache_data
def load_data():

    df = pd.read_csv("data/clean_sales.csv")

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])

    return df