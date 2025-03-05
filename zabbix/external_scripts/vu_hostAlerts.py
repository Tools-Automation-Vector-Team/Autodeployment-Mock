#!/usr/lib/zabbix/externalscripts/env/bin/python

import argparse
import requests

ZABBIX_TOKEN = "f27d2d5053a798137734fbe4e26431189d194257a6c71b1b9c569c23cc2d0bc8"
ZABBIX_HOST = "http://140.238.230.93/zabbix"


parser = argparse.ArgumentParser(description="Provide Host Name")
parser.add_argument("host", help="Host Name.")

args = parser.parse_args()


TARGET_HOST = args.host

url = f"{ZABBIX_HOST}/api_jsonrpc.php"
headers = {
    "Authorization": f"Bearer {ZABBIX_TOKEN}",
    "Content-Type": "application/json-rpc"
}

def problems():
    """Fetch active problems from Zabbix."""
    data = {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "output": ["triggerid", "description", "priority", "value", "lastchange"],
            "selectTags": "extend",  # Fetch tags for each item
            "filter": {
                "value": 1  # 1 means the trigger is in problem state
            },
            "selectHosts": ["hostid", "name"],
            "selectLastEvent": ["eventid", "acknowledged"],
            "expandDescription": True,
            "expandComment": True,
            "expandExpression": True,
            "only_true": True,  # Only show active triggers
            "maintenance": False,  # Exclude triggers under maintenance
            "withLastEventUnacknowledged": True  # Only show unacknowledged events
        },
        "id": 1
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result.get("result", None)
    except requests.RequestException as e:
        print(f"Error fetching problems: {e}")
        return None
    
def filter_events_by_host(data, target_host):
    """
    Filters events based on the host name and returns eventid and priority.

    Args:
        data (list): List of dictionaries containing event data.
        target_host (str): The target host name to filter by.

    Returns:
        list: A list of dictionaries with eventid and priority for the matching host.
    """
    return [
        {
            'eventid': item['lastEvent']['eventid'],
            'priority': item['priority']
        }
        for item in data
        if any(host['name'] == target_host for host in item['hosts'])
    ]

# Example usage
try:
    filtered_data = filter_events_by_host(problems(), TARGET_HOST)
except Exception as e:
    filtered_data = None
    print(e)


result = 1
if filtered_data:
    for data in filtered_data:
        if int(data['priority']) == 0: # PRIORITY 0
            continue
        elif int(data['priority']) < 3 and result < 2: # PRIORITY 1, 2
            result = 2
        elif int(data['priority']) < 5 and result < 3: # PRIORITY 3, 4
            result = 3
        elif int(data['priority']) < 6 and result < 4: # PRIORITY 5
            result = 4


print(result)