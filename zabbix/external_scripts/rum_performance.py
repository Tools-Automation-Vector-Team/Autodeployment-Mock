#!/usr/lib/zabbix/externalscripts/env/bin/python

"RUM PERFORMANCE"
import requests
import argparse
import json

MATOMO_BASE_URL = "https://analytics.cl.telemetrics.tech/index.php"
TOKEN_AUTH = "a39ccd9e9c8eac098dd5200539177864"


def get_sites():
    url = f"{MATOMO_BASE_URL}?module=API&method=SitesManager.getSitesWithAdminAccess&format=JSON&token_auth={TOKEN_AUTH}"
    response = requests.get(url)
 
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching sites: {response.status_code}")
        return []
 
def fetch_page_performance(id_site):
    payload = {
        "module": "API",
        "method": "PagePerformance.get",
        "format": "json",
        "token_auth": TOKEN_AUTH,
        "idSite": id_site,
        "period": "day",
        "date": "today"
    }
    
    try:
        response = requests.post(MATOMO_BASE_URL, data=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()  # Return the JSON response
    except requests.RequestException as e:
        return f"Error: {e}"
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Matomo data for a specific website.")
    parser.add_argument("site_name", help="The name of the website (e.g., 'BOLT').")

    args = parser.parse_args()

    idSite = None
    for sites in get_sites():
        if args.site_name == sites['name'] :
            idSite = sites['idsite']
            break

    print(json.dumps(fetch_page_performance(idSite)))
