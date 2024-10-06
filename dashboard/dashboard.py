import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px

sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)

    return daily_orders_df


def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").order_id.sum(
    ).sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_bycity_df(df):
    bycity_df = df.groupby(
        by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return bycity_df


def create_bystate_df(df):
    bystate_df = df.groupby(
        by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return bystate_df


def create_rfm_df(df):
    snapshot_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_df = df.groupby('customer_id').agg({
        # Recency
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'count',  # Frequency
        'price': 'sum'  # Monetary
    }).reset_index()
    rfm_df.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']
    return rfm_df

def plot_category_sales(df):
    category_sales = df.groupby('product_category_name').agg({'order_id': 'count', 'price': 'sum'}).reset_index()
    category_sales.columns = ['Category Product', 'Sales Amount', 'Total Revenue']

    # Plot Jumlah Penjualan per Kategori Produk
    fig1, ax1 = plt.subplots(figsize=(12, 12))
    sns.barplot(x='Sales Amount', y='Category Product', data=category_sales.sort_values('Sales Amount', ascending=False), ax=ax1)
    ax1.set_title('Total Sales Amount of each Product Category')
    ax1.grid(axis='x', linestyle='--', alpha=1)

    # Tampilkan plot di Streamlit
    st.pyplot(fig1)

    # Plot Total Pendapatan per Kategori Produk
    fig2, ax2 = plt.subplots(figsize=(12, 12))
    sns.barplot(x='Total Revenue', y='Category Product', data=category_sales.sort_values('Total Revenue', ascending=False), ax=ax2)
    ax2.set_title('Total Revenue of each Product Category')
    ax2.grid(axis='x', linestyle='--', alpha=1)

    # Tampilkan plot di Streamlit
    st.pyplot(fig2)

all_df = pd.read_csv("dashboard/main_data.csv")

all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    if start_date > end_date:
        st.error(
            "Rentang tanggal tidak valid. Pastikan tanggal mulai sebelum tanggal akhir.")

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)


st.header("E-Commerce Public Dashboard  " + 
        "![Icon](https://img.icons8.com/?size=100&id=XrEFnp33pJYw&format=png&color=000000)")
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), 'USD', locale='en_US')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)


# Tampilkan hasil RFM
st.subheader("RFM Analysis")
st.dataframe(rfm_df)

st.subheader("Best Customer Based on RFM Parameters") 

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df['Recency'].mean(), 1)  
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df['Frequency'].mean(), 2)  
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df['Monetary'].mean(), 'USD', locale='en_US')  
    st.metric("Average Monetary", value=avg_monetary)

# Mengatur ukuran figure yang lebih kecil
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 10)) 
colors = ["#90CAF9"]

# By Recency
sns.barplot(y="Recency", x="customer_id", data=rfm_df.sort_values(by="Recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=15)
ax[0].set_title("By Recency (days)", loc="center", fontsize=20)
ax[0].tick_params(axis='y', labelsize=10)
ax[0].tick_params(axis='x', labelsize=10, rotation=80)

# By Frequency
sns.barplot(y="Frequency", x="customer_id", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=15)
ax[1].set_title("By Frequency", loc="center", fontsize=20)
ax[1].tick_params(axis='y', labelsize=10)
ax[1].tick_params(axis='x', labelsize=10, rotation=80)

# By Monetary
sns.barplot(y="Monetary", x="customer_id", data=rfm_df.sort_values(by="Monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=15)
ax[2].set_title("By Monetary", loc="center", fontsize=20)
ax[2].tick_params(axis='y', labelsize=10)
ax[2].tick_params(axis='x', labelsize=10, rotation=80)

st.pyplot(fig)

# Plot order count by month
monthly_orders = all_df.groupby('month')['order_id'].count().reset_index()
fig1 = px.bar(monthly_orders, x='month', y='order_id', title="Orders Count per Month")
st.plotly_chart(fig1)

# Product name category Analysis
st.subheader("Distribution Product Category Name")
plot_category_sales(all_df)

col1, col2 = st.columns(2)
with col1:
    # Tampilkan hasil distribusi customer per negara bagian
    st.subheader("Customer Distribution by State")
    st.dataframe(bystate_df)

with col2:
    # Tampilkan hasil distribusi customer per kota
    st.subheader("Customer Distribution by City")
    st.dataframe(bycity_df)
    
    
# Menghitung frekuensi pembelian untuk setiap produk
product_purchase = all_df.groupby(['product_id', 'customer_state', 'customer_city', 'payment_type']).agg({
    'order_item_id': 'count',
    'price': 'mean'
}).rename(columns={'order_item_id': 'purchase_count', 'price': 'average_price'}).reset_index()

# Mengelompokkan berdasarkan rentang harga (Binning)
bins_price = [0, 50, 100, 200, float('inf')]
labels_price = ['Murah', 'Sedang', 'Mahal', 'Sangat Mahal']
product_purchase['price_category'] = pd.cut(product_purchase['average_price'], bins=bins_price, labels=labels_price)

# Barang dengan Pembelian Terbanyak berdasarkan State
fig1, ax1 = plt.subplots(figsize=(12, 8))  
statewise = product_purchase.groupby('customer_state')['purchase_count'].sum().sort_values(ascending=False).head(10)
sns.barplot(x=statewise.values, y=statewise.index, palette='viridis', ax=ax1)
ax1.set_title('Top 10 Customer States with the Most Purchases')
ax1.set_xlabel('Purchase Amount')
ax1.set_ylabel('Customer State')

# Tampilkan plot di Streamlit
st.pyplot(fig1)

# Barang dengan Pembelian Terbanyak berdasarkan City
fig2, ax2 = plt.subplots(figsize=(12, 8))  
citywise = product_purchase.groupby('customer_city')['purchase_count'].sum().sort_values(ascending=False).head(10)
sns.barplot(x=citywise.values, y=citywise.index, palette='coolwarm', ax=ax2)
ax2.set_title('Top 10 Customer City with the Most Purchases')
ax2.set_xlabel('Purchase Amount')
ax2.set_ylabel('Customer City')

# Tampilkan plot di Streamlit
st.pyplot(fig2)

# Payment Type Distribution
st.subheader("Payment Type Distribution")
payment_type_counts = all_df['payment_type'].value_counts()
fig4 = px.pie(names=payment_type_counts.index, values=payment_type_counts.values)
st.plotly_chart(fig4)

# Plot review score distribution
st.subheader("Review Score Distribution")
review_score_counts = all_df['review_score'].value_counts().sort_index()
fig2 = px.bar(
    x=review_score_counts.index,
    y=review_score_counts.values,
    labels={'x': 'Review Score', 'y': 'Count'},
    title='Review Score Distribution',
    text=review_score_counts.values 
)
st.plotly_chart(fig2)

# Geospatial Visualization
st.subheader("Geospatial Analysis")

# Map of orders based on geolocation
fig3 = px.scatter_mapbox(all_df, lat="geolocation_lat", lon="geolocation_lng", 
                        hover_name="customer_city", hover_data=["order_id"],
                        color_discrete_sequence=["fuchsia"], zoom=3, height=500)
fig3.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig3)