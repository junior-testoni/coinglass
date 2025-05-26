import streamlit as st
import sqlite3
import pandas as pd

DB_FILE = "coinglass_data.db"

def get_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cur.fetchall()]

def load_table(conn, table, symbol=None, limit=500):
    query = f"SELECT * FROM {table}"
    params = []
    if symbol and 'symbol' in [d[0] for d in conn.execute(f'PRAGMA table_info({table})')]:
        query += " WHERE symbol = ?"
        params.append(symbol)
    query += " ORDER BY time DESC LIMIT ?"
    params.append(limit)
    return pd.read_sql_query(query, conn, params=params)

def external_link(label, url):
    st.markdown(f'<a href="{url}" target="_blank">{label}</a>', unsafe_allow_html=True)

def main():
    st.title("Coinglass Data Dashboard")
    st.write("For more info, visit ")
    external_link("Coinglass Documentation", "https://docs.coinglass.com/")
    conn = sqlite3.connect(DB_FILE)
    tables = get_tables(conn)
    table = st.sidebar.selectbox("Select table", tables)
    # Symbol filter if available
    columns = [d[1] for d in conn.execute(f'PRAGMA table_info({table})')]
    symbol = None
    if 'symbol' in columns:
        symbols = [row[0] for row in conn.execute(f'SELECT DISTINCT symbol FROM {table}')]
        symbol = st.sidebar.selectbox("Symbol", symbols)
    df = load_table(conn, table, symbol)
    st.write(f"Showing {len(df)} rows from {table}")
    st.dataframe(df)
    # Plot if time and a numeric column exist
    if 'time' in df.columns:
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        plot_col = st.selectbox("Plot column", [c for c in numeric_cols if c != 'time'], key='plot_col')
        if plot_col:
            df_sorted = df.sort_values('time')
            st.line_chart(df_sorted.set_index('time')[plot_col])
    conn.close()

if __name__ == "__main__":
    main()
