import pandas
import numpy
import os
from dotenv import load_dotenv
import mysql.connector

# Load variables from .env
load_dotenv()

def connect_to_db():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return conn

def get_basic_info(cursor):
    queries = {
    "Total Suppliers": "select count(*) as total_suppliers from suppliers;",

    "Total Products": "select count(*) as total_products from products;",

    "Total Categories Dealing": "select count(distinct category) as total_categories from products;",

    "Total Sale Value (last 9 months)": """ 
        select round(sum(abs(se.change_quantity) * p.price), 2) as total_sales_value_in_last_9_months
        from stock_entries as se
        join products as p 
        on p.product_id = se.product_id
        where se.change_type='Sale' and se.entry_date >= (select date_sub(max(entry_date), interval 9 month) from stock_entries);
        """,

    "Total Restock Value (last 9 months)": """ 
        select round(sum(abs(se.change_quantity) * p.price), 2) as total_restock_value_in_last_9_months
        from stock_entries as se
        join products as p 
        on p.product_id = se.product_id
        where se.change_type='Restock' and se.entry_date >= (select date_sub(max(entry_date), interval 9 month) from stock_entries);
        """,

    "Below Reorders and No Pending Reorders": """ 
        select count(*) from products as p where p.stock_quantity < p.reorder_level
        and product_id not in (
        select distinct product_id from reorders where status='Pending'
        )
        """
    }

    result={}

    for label, query in queries.items():
        cursor.execute(query)
        row = cursor.fetchone()
        result[label] = list(row.values())[0]
    
    return result

def get_additional_tables(cursor):
    queries = {
    "Suppliers contact details": "select supplier_name, contact_name, email, phone from suppliers;",

    "Product with suppliers and stock": """
    select p.product_name, s.supplier_name, p.stock_quantity, p.reorder_level
    from products as p
    join suppliers as s
    on p.supplier_id = s.supplier_id
    order by p.product_name;
    """,

    "Product needing reorder":""" 
    select product_id, product_name, stock_quantity, reorder_level
    from products 
    where stock_quantity < reorder_level
    """
    }
    
    tables={}

    for label, query in queries.items():
        cursor.execute(query)
        tables[label] = cursor.fetchall()

    return tables

def add_new_manual_id(cursor, db, p_name, p_category, p_price, p_stock, p_reorder, p_supplier):
    proc_call = "call AddNewProductManualID(%s, %s, %s, %s, %s, %s)"
    params = (p_name, p_category, p_price, p_stock, p_reorder, p_supplier)
    cursor.execute(proc_call, params)
    db.commit()

def get_categories(cursor):
    cursor.execute("select distinct category from products order by category asc")
    rows = cursor.fetchall()
    return [row['category'] for row in rows]

def get_suppliers(cursor):
    cursor.execute("select supplier_id, supplier_name from suppliers order by supplier_name asc")
    return cursor.fetchall()

def get_all_products(cursor):
    cursor.execute("select product_id, product_name from products order by product_name")
    return cursor.fetchall()

def get_product_history(cursor, product_id):
    query = """select * 
                from product_inventory_history 
                where product_id=%s
                order by record_date desc """
    cursor.execute(query, (product_id, ))
    return cursor.fetchall()
    