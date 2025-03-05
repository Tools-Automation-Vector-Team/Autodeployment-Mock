#!/usr/lib/zabbix/externalscripts/env/bin/python
import mysql.connector
import json
import argparse
from datetime import datetime
from decimal import Decimal

class QueryFetcher:
    def __init__(self, dsn, user, password, database):
        self.config = self._parse_dsn(dsn, user, password, database)
        self.connection = None
        self.cursor = None

    def _parse_dsn(self, dsn, user, password, database):
        # Parse DSN in the format: tcp://host:port
        try:
            protocol, rest = dsn.split("//")
            if protocol != "tcp:":
                raise ValueError("Unsupported DSN protocol")

            host_port = rest
            host, port = host_port.split(":")

            return {
                'user': user,
                'password': password,
                'host': host,
                'port': int(port),
                'database': database
            }
        except Exception as e:
            raise ValueError(f"Invalid DSN format: {e}")

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def fetch_query_data(self, query, params=None):
        try:
            self.connect()
            if not self.cursor:
                return

            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            results = self.cursor.fetchall()

            # Convert Decimal to float for JSON serialization
            for row in results:
                for key, value in row.items():
                    if isinstance(value, Decimal):
                        # Convert Decimal to float for JSON serialization
                        row[key] = float(value)
                    elif isinstance(value, datetime):
                        # Convert datetime to ISO format string
                        row[key] = value.isoformat()
                    elif value is None:
                        # Convert None (NULL in SQL) to None in JSON (which will be serialized as null)
                        row[key] = None
                    elif isinstance(value, bytes):
                        # Handle binary data (e.g., BLOB) - convert to base64 string
                        row[key] = value.decode('utf-8', errors='ignore')  # Decoding bytes to string, or you can use base64 encoding
                # You can add more custom handling for other types as needed
            formatted_data = {"data": results}
            return formatted_data

        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            self.disconnect()

def get_query_by_name(fetcher, query_name, params=None):
    queries = {
        "High-Impact SQL Queries": """
        SELECT
            DIGEST AS `Fingerprint`,
            SCHEMA_NAME,
            DIGEST_TEXT AS `Query`, 
            COUNT_STAR AS `Requests`, 
            ROUND(AVG_TIMER_WAIT / 1000000000, 2) AS `Avg Latency (ms)`, 
            ROUND(SUM_TIMER_WAIT / 1000000000, 2) AS `Total Time (ms)`, 
            ROUND((SUM_TIMER_WAIT / (SELECT SUM(SUM_TIMER_WAIT) FROM performance_schema.events_statements_summary_by_digest)) * 100, 2) AS `Percent Time`, 
            ROUND(SUM_ROWS_SENT / COUNT_STAR, 2) AS `Rows/Query`,
            SUM_CPU_TIME / 1000000000 AS `Total CPU Time (ms)`,
            LAST_SEEN AS `Last Execution Time`
        FROM 
            performance_schema.events_statements_summary_by_digest
        WHERE 
            LAST_SEEN >= NOW() - INTERVAL 7 DAY 
            AND SCHEMA_NAME IS NOT NULL
            AND SCHEMA_NAME != 'PERFORMANCE_SCHEMA'
        ORDER BY 
            AVG_TIMER_WAIT DESC
        LIMIT %s;
        """,
        "Statements with Runtimes in 95th Percentile": """
        SELECT * FROM sys.statements_with_runtimes_in_95th_percentile
        """
        # Add other queries here
    }

    query = queries.get(query_name)
    if not query:
        print(f"Query '{query_name}' not found.")
        return None

    return fetcher.fetch_query_data(query, params)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch SQL query data.")
    parser.add_argument('--dsn', required=True, help="Database DSN in the format tcp://host:port")
    parser.add_argument('--user', required=True, help="Database user")
    parser.add_argument('--password', required=True, help="Database password")
    parser.add_argument('--database', required=True, help="Database name")
    parser.add_argument('--query_name', required=True, help="Query name to execute")
    parser.add_argument('--limit', type=int, default=None, help="Limit parameter for the query")

    args = parser.parse_args()

    fetcher = QueryFetcher(args.dsn, args.user, args.password, args.database)

    params = (args.limit,) if args.limit is not None else None
    data = get_query_by_name(fetcher, args.query_name, params)

    if data:
        print(json.dumps(data, indent=4))
