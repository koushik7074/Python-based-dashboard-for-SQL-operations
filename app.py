import pandas as pd
import streamlit as st
from db_functions import (
    connect_to_db,
    get_basic_info,
    get_additional_tables,
    add_new_manual_id,
    get_categories,
    get_suppliers
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
    if selected_task=='Add new product':
        st.header("Add New Product")
        categories = get_categories(cursor)
        suppliers = get_suppliers(cursor)
        supplier_ids = [s['supplier_id'] for s in suppliers]
        supplier_names = [s['supplier_name'] for s in suppliers]

        with st.form("Add Product Form"):
            product_name = st.text_input("Product Name")
            product_category = st.selectbox("Category", categories)
            product_price = st.number_input("Price", min_value=0.00)
            product_stock = st.number_input("Stock Quantity", min_value=0, step=1)
            product_level = st.number_input("Reorder Level", min_value=0, step=1)

            supplier_id = st.selectbox(
                "Supplier", 
                options = supplier_ids, 
                format_func = lambda x: supplier_names[supplier_ids.index(x)]
                )
            
            submitted = st.form_submit_button("Add Product")

            if submitted:
                if not product_name:
                    st.error("Please Enter the Product Name")
                else:
                    try:
                        add_new_manual_id(
                            cursor, 
                            db, 
                            product_name, 
                            product_category, 
                            product_price, 
                            product_stock, 
                            product_level, 
                            supplier_id
                            )
                        st.success(f"Product {product_name} added successfully!")
                    except Exception as e:
                        st.error(f"Error adding the product: {e}")


