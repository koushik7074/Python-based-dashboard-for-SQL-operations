import pandas as pd
import streamlit as st
from db_functions import (
    connect_to_db,
    get_basic_info,
    get_additional_tables
)

st.sidebar.title("Inventory Management Dashboard")
option = st.sidebar.radio("Select Option:", ['Basic Information', 'Operational Tasks'])

st.title("Inventory and Supply Chain Dashboard")
db = connect_to_db()
cursor = db.cursor(dictionary=True)

#-------------------------------------Basic info page--------------------------------------------------------
if option=='Basic Information':
    st.header('Basic Metrics')

    basic_info = get_basic_info(cursor) # basic info as dictionary

    cols = st.columns(3)
    keys=list(basic_info.keys())
    for i in range(3):
        cols[i].metric(label=keys[i], value=basic_info[keys[i]])

    cols = st.columns(3)
    for i in range(3, 6):
        cols[i-3].metric(label=keys[i], value=basic_info[keys[i]])

    st.divider()

    # fetch and display detailed tables
    tables = get_additional_tables(cursor)
    for label, data in tables.items():
        st.header(label)
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.divider()

elif option == 'Operational Tasks':
    st.header("Operational Tasks")
    selected_task = st.selectbox("choose a task:", ['Add new product', "Product history", "Place Reorder", "Receive Reorder"])
    