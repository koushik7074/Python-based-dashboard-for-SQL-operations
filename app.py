import pandas as pd
import streamlit as st
from db_functions import (
    connect_to_db,
    get_basic_info,
    get_additional_tables,
    add_new_manual_id,
    get_categories,
    get_suppliers,
    get_all_products,
    get_product_history,
    place_reorder,
    get_pending_reorders,
    mark_reorder_as_received
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

    #-----------------------------------Add New Product-------------------------------------------------------
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

    #----------------------------------Product History--------------------------------------------------------
    elif selected_task == "Product history":
        st.header("Product Inventory History")

        # get product list
        products = get_all_products(cursor)
        product_names = [p['product_name'] for p in products] 
        product_ids = [p['product_id'] for p in products]

        selected_product_name = st.selectbox("Select a Product", options=product_names)

        if selected_product_name:
            selected_product_id = product_ids[product_names.index(selected_product_name)]

            history_data = get_product_history(cursor, selected_product_id)

            if history_data:
                df = pd.DataFrame(history_data)
                st.dataframe(df)
            else:
                st.info("No history found for the product selected!")

    #----------------------------------Place Reorder ---------------------------------------------------------
    elif selected_task == "Place Reorder":
        st.header("Place a Reorder")

        # get product list
        products = get_all_products(cursor)
        product_names = [p['product_name'] for p in products] 
        product_ids = [p['product_id'] for p in products]

        # user input
        selected_product_name = st.selectbox("Select a Product", options=product_names)
        reorder_quantity = st.number_input("Reorder Quantity", min_value=1, step=1)

        if st.button("Place Reorder"):
            if not selected_product_name:
                st.error("Please select a product ")
            elif reorder_quantity<=0:
                st.error("Reorder quantity must be greater than 0")
            else:
                selected_product_id = product_ids[product_names.index(selected_product_name)]
                try:
                    place_reorder(cursor, db, selected_product_id, reorder_quantity)
                    st.success(f"Order placed for {selected_product_name} with quantity: {reorder_quantity}")
                except Exception as e:
                    st.error(f"Error placing reorder: {e}")

    #---------------------------------Receive Reorder --------------------------------------------------------
    elif selected_task == "Receive Reorder":
        st.header("Mark Reorder as Received")
        # fetch orders in "ordered" stage
        pending_reorders = get_pending_reorders(cursor)
        if not pending_reorders:
            st.info("No pending orders to be received")
        else:
            reorder_ids = [r['reorder_id'] for r in pending_reorders]
            reorder_labels = [f"ID {r['reorder_id']} - {r['product_name']}" for r in pending_reorders]

            selected_label = st.selectbox("Select Reorder to mark as Received", options=reorder_labels)

            if selected_label:
                selected_reorder_id = reorder_ids[reorder_labels.index(selected_label)]
                
                if st.button("Mark as 'Received'"):
                    try:
                        mark_reorder_as_received(cursor, db, selected_reorder_id)
                        st.success(f"Reorder ID {selected_reorder_id} marked as Received!")
                    except Exception as e:
                        st.error(f"Error: {e}")
