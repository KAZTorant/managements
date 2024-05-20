import sqlite3
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

# SQLite database path
sqlite_db = f'{BASE_DIR}/db.sqlite3'
output_sql_file = 'output_postgres.sql'

# Connect to SQLite database
sqlite_conn = sqlite3.connect(sqlite_db)
sqlite_cursor = sqlite_conn.cursor()

# Function to convert SQLite schema to PostgreSQL


def convert_schema(sqlite_schema):
    # Replace SQLite specific types with PostgreSQL types
    pg_schema = sqlite_schema.replace('AUTOINCREMENT', 'SERIAL')
    pg_schema = pg_schema.replace('INTEGER', 'INT')
    pg_schema = pg_schema.replace('TEXT', 'VARCHAR')
    pg_schema = pg_schema.replace('BOOLEAN', 'BOOL')
    return pg_schema


with open(output_sql_file, 'w') as f:
    # Retrieve tables from SQLite database
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = sqlite_cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]

        # Get the schema of the table from SQLite
        sqlite_cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        create_table_sql = sqlite_cursor.fetchone()[0]

        # Convert schema to PostgreSQL
        create_table_sql = convert_schema(create_table_sql)

        # Write the create table statement to the file
        f.write("{};\n".format(create_table_sql))

        # Retrieve data from SQLite table
        sqlite_cursor.execute("SELECT * FROM {}".format(table_name))
        rows = sqlite_cursor.fetchall()

        # Write insert statements to the file
        for row in rows:
            values = []
            for value in row:
                if isinstance(value, str):
                    values.append("'{}'".format(value.replace("'", "''")))
                elif value is None:
                    values.append('NULL')
                else:
                    values.append(str(value))
            insert_sql = "INSERT INTO {} VALUES ({});".format(
                table_name, ', '.join(values))
            f.write("{}\n".format(insert_sql))

# Close the connections
sqlite_cursor.close()
sqlite_conn.close()

print("SQL dump for PostgreSQL created successfully: {}".format(output_sql_file))
