import sqlite3
import argparse
import sys

DB_FILE = "coinglass_data.db"

def list_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    return tables

def print_table(conn, table, limit):
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM {table} LIMIT ?", (limit,))
        rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]
        print("| ", " | ".join(col_names), "|")
        print("|" + "---|" * len(col_names))
        for row in rows:
            print("| ", " | ".join(str(x) for x in row), "|")
    except sqlite3.Error as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="View data from coinglass_data.db.")
    parser.add_argument("table", nargs="?", help="Table name to view. If omitted, lists all tables.")
    parser.add_argument("--limit", type=int, default=10, help="Number of rows to display (default: 10)")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_FILE)
    if not args.table:
        print("Available tables:")
        for t in list_tables(conn):
            print(" -", t)
    else:
        print_table(conn, args.table, args.limit)
    conn.close()

if __name__ == "__main__":
    main()
