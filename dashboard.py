from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


def format_number(value):
    return f"{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    return pd.read_parquet('data/output/AB_NYC_2019.parquet')

df = load_data()

st.title("🏙️ Dashboard ETL NYC Airbnb")

st.markdown("---")

st.sidebar.title("🔎 Filtros")
st.sidebar.markdown("---")

neigh_group = st.sidebar.multiselect(
    "Neighbourhood Group",
    options=df['neighbourhood_group'].unique(),
    default=df["neighbourhood_group"].unique()
)

room_type = st.sidebar.multiselect(
    "Room Type",
    options=df['room_type'].unique(),
    default=df["room_type"].unique()
)

df_filtered = df[
    (df['neighbourhood_group'].isin(neigh_group)) &
    (df["room_type"].isin(room_type))
]

col1, col2, col3 = st.columns(3)

col1.metric("Preço Médio", f"${df_filtered['price'].mean():.2f}")
col2.metric("Total de listings", format_number(df_filtered.shape[0]))

col3.metric(
    "Reviews Totais",
    format_number(df_filtered['number_of_reviews'].sum())
)

price_by_group = df_filtered.groupby('neighbourhood_group')['price'].mean()

st.markdown("---")

st.subheader("Preço médio por região")
fig = px.bar(
    price_by_group,
    labels={'value': 'Preço médio', 'neighbourhood_group': 'Região'}
)
fig.update_layout(
    yaxis_tickprefix="$ ",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

room_analysis = df_filtered.groupby('room_type').agg({
    'price': 'mean',
    'availability_365': 'mean',
    'number_of_reviews': 'sum'
})

room_analysis = room_analysis.rename(columns={
    'price': 'Preço Médio',
    'availability_365': 'Disponibilidade Média',
    'number_of_reviews': 'Total de Reviews'
})

room_analysis['Preço Médio'] = room_analysis['Preço Médio'].apply(
    lambda x: f"$ {x:,.2f}"
)

room_analysis['Disponibilidade Média'] = room_analysis['Disponibilidade Média'].apply(
    lambda x: f"{x:.0f} dias"
)

room_analysis['Total de Reviews'] = room_analysis['Total de Reviews'].apply(
    lambda x: f"{int(x):,}".replace(",", ".")
)

st.markdown("### Análise por tipo de acomodação")
st.caption("Comparação entre tipos de imóveis com base em preço, disponibilidade e demanda")

st.dataframe(room_analysis, use_container_width=True)

st.markdown("---")

revenue = df_filtered.groupby('neighbourhood_group')['estimated_revenue'].sum()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Preço por região")
    fig = px.bar(
    price_by_group,
    labels={'value': 'Preço', 'neighbourhood_group': 'Região'}
    )
    fig.update_layout(
        yaxis_tickprefix="$ ",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Receita por região")
    fig = px.bar(
    revenue,
    labels={'value': 'Receita', 'neighbourhood_group': 'Região'}
    )
    fig.update_layout(
        yaxis_tickprefix="$ ",
    )
    st.plotly_chart(fig, use_container_width=True)


st.markdown("---")

st.subheader("Mapa de listings")
st.map(df_filtered[['latitude', 'longitude']].sample(1000))

most_expensive = price_by_group.idxmax()

st.info(f"""
    **Observação:**
A região mais cara atualmente é **{most_expensive}**.
""")

