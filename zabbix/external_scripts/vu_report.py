#!/usr/lib/zabbix/externalscripts/env/bin/python
import argparse
import pymysql

# Parsing text
parser = argparse.ArgumentParser(description="Validate and format a URL or domain name.")
parser.add_argument("name", help="Name is in valid formate.")

args = parser.parse_args()


### MAIN

# Database connection details
db_config = {
    'host': '48.217.107.255',
    'user': 'kartik',
    'password': 'Kartik@24082003',
    'database': 'zabbix'
}

# SQL query
sql_query = f"""
SELECT hist.value
FROM zabbix.history_uint AS hist
JOIN zabbix.items AS itm ON hist.itemid = itm.itemid
JOIN zabbix.hosts AS hosts ON itm.hostid = hosts.hostid
WHERE itm.key_ = 'status.id'
  AND hist.clock >= UNIX_TIMESTAMP(NOW() - INTERVAL 7 DAY)
  AND hosts.name = '{args.name}';
"""

def fetch_data():
    """Fetch data from the database."""
    connection = None
    values = []

    try:
        # Connect to the database
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchall()
            # Extract the values into a list
            values = [row[0] for row in result]
    except pymysql.MySQLError as e:
        print(f"Error fetching data from database: {e}")
    finally:
        if connection:
            connection.close()

    return values

def analyze_zero_sequences(values):
    """Analyze zero sequences and total count of zeros."""
    total_zeros = 0
    zero_sequences = []
    current_count = 0

    for value in values:
        if value == 0:
            total_zeros += 1
            current_count += 1
        else:
            if current_count > 0:
                zero_sequences.append(current_count)
                current_count = 0

    # Check for a sequence ending at the end of the list
    if current_count > 0:
        zero_sequences.append(current_count)

    return total_zeros, zero_sequences

def seconds_to_minutes(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return minutes, remaining_seconds

# Fetch the data
values = fetch_data()

# Analyze the zero sequences and total count of zeros
total_zeros, zero_sequences = analyze_zero_sequences(values)

# print(f"Total count of zeros: {total_zeros}")
# print(f"All sequences of zeros: {zero_sequences}")

# minuits = seconds_to_minutes(total_zeros * 15)
# minuits = str(minuits[0]) + "." + str(minuits[1])

# Downtime Count
d_count = []
for i in zero_sequences:
    if i >= 3:
        d_count.append(i)

# Downtime Minuits
d_minuits = 0
for i in d_count:
    d_minuits += (i * 15)
d_minuits = seconds_to_minutes(d_minuits)
d_minuits = str(d_minuits[0]) + "." + str(d_minuits[1])

abl = "{"
abr = "}"
print(f"""
"data": {{
    "downtime": {d_minuits},
    "downtimecount": {len(d_count)}
}}
""")
