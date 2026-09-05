#!/usr/bin/env python
# coding: utf-8

# In[17]:


import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# In[2]:


st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)


# In[18]:


@st.cache_data
def load_data():
    data_path = Path("Telco_Cusomer_Churn.csv")
    if not data_path.exists():
        data_path = Path("Task 5") / "Telco_Cusomer_Churn.csv"

    df = pd.read_csv(data_path)

    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce"
    )

    df["TotalCharges"] = df["TotalCharges"].fillna(0)

    df["Revenue"] = df["MonthlyCharges"]

    df["ActiveUser"] = df["Churn"].apply(
        lambda x: 1 if x == "No" else 0
    )

    df["TicketSize"] = df["MonthlyCharges"]

    regions = ["North", "South", "East", "West"]

    df["Region"] = [
        regions[i % len(regions)]
        for i in range(len(df))
    ]

    df["Category"] = df["InternetService"]

    return df
df = load_data()


# In[16]:


st.title("📊 Customer Analytics & Churn Dashboard")

st.markdown(
    "Interactive business intelligence dashboard "
    "for customer revenue, engagement and churn analysis."
)

st.divider()



# In[19]:


st.sidebar.header("🔎 Dashboard Filters")

# Region filter
region_options = sorted(df["Region"].unique())

selected_regions = st.sidebar.multiselect(
    "Region",
    region_options,
    default=region_options
)

# Category filter
category_options = sorted(df["Category"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Category",
    category_options,
    default=category_options
)

# Contract filter
contract_options = sorted(df["Contract"].unique())

selected_contracts = st.sidebar.multiselect(
    "Contract Type",
    contract_options,
    default=contract_options
)

# Churn filter
churn_options = sorted(df["Churn"].unique())

selected_churn = st.sidebar.multiselect(
    "Customer Status",
    churn_options,
    default=churn_options
)


# In[20]:


filtered_df = df[
    (df["Region"].isin(selected_regions)) &
    (df["Category"].isin(selected_categories)) &
    (df["Contract"].isin(selected_contracts)) &
    (df["Churn"].isin(selected_churn))
]


# In[21]:


total_revenue = filtered_df["Revenue"].sum()

active_users = filtered_df["ActiveUser"].sum()

total_users = len(filtered_df)

if total_users > 0:
    churn_rate = (
        (filtered_df["Churn"] == "Yes").sum()
        / total_users
    ) * 100
else:
    churn_rate = 0

avg_ticket_size = filtered_df["TicketSize"].mean()

if pd.isna(avg_ticket_size):
    avg_ticket_size = 0


# In[22]:


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Revenue",
        f"${total_revenue:,.2f}"
    )

with col2:
    st.metric(
        "👥 Active Users",
        f"{active_users:,}"
    )

with col3:
    st.metric(
        "📉 Churn Rate",
        f"{churn_rate:.2f}%"
    )

with col4:
    st.metric(
        "🎫 Avg Ticket Size",
        f"${avg_ticket_size:,.2f}"
    )

st.divider()


# In[23]:


col1, col2 = st.columns(2)

# Churn by Contract
with col1:

    contract_churn = (
        filtered_df
        .groupby(["Contract", "Churn"])
        .size()
        .reset_index(name="Customers")
    )

    fig1 = px.bar(
        contract_churn,
        x="Contract",
        y="Customers",
        color="Churn",
        barmode="group",
        title="Customer Churn by Contract Type"
    )

    fig1.update_layout(
        xaxis_title="Contract Type",
        yaxis_title="Number of Customers"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# Churn by Category
with col2:

    category_churn = (
        filtered_df
        .groupby(["Category", "Churn"])
        .size()
        .reset_index(name="Customers")
    )

    fig2 = px.bar(
        category_churn,
        x="Category",
        y="Customers",
        color="Churn",
        barmode="group",
        title="Churn by Service Category"
    )

    fig2.update_layout(
        xaxis_title="Category",
        yaxis_title="Customers"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# In[24]:


col1, col2 = st.columns(2)

# Revenue by Region
with col1:

    region_revenue = (
        filtered_df
        .groupby("Region")["Revenue"]
        .sum()
        .reset_index()
    )

    fig3 = px.bar(
        region_revenue,
        x="Region",
        y="Revenue",
        title="Revenue by Region",
        text_auto=".2s"
    )

    fig3.update_layout(
        xaxis_title="Region",
        yaxis_title="Revenue"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# Customer Distribution
with col2:

    status_data = (
        filtered_df["Churn"]
        .value_counts()
        .reset_index()
    )

    status_data.columns = [
        "Status",
        "Customers"
    ]

    fig4 = px.pie(
        status_data,
        names="Status",
        values="Customers",
        title="Customer Status Distribution",
        hole=0.45
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )


# In[25]:


st.subheader("📈 Customer Charges Analysis")

fig5 = px.histogram(
    filtered_df,
    x="MonthlyCharges",
    color="Churn",
    nbins=30,
    title="Monthly Charges Distribution"
)

fig5.update_layout(
    xaxis_title="Monthly Charges",
    yaxis_title="Number of Customers"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)


# In[26]:


st.subheader("📋 Filtered Customer Data")

display_columns = [
    "customerID",
    "gender",
    "tenure",
    "Contract",
    "InternetService",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
    "Region"
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    height=350
)


# In[27]:


csv = filtered_df.to_csv(index=False)

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv,
    file_name="filtered_customer_data.csv",
    mime="text/csv"
)


# In[28]:


st.divider()

st.caption(
    "Customer Analytics Dashboard | "
    "Built with Python, Streamlit, Pandas & Plotly"
)

