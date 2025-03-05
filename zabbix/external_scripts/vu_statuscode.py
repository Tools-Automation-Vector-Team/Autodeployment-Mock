#!/usr/lib/zabbix/externalscripts/env/bin/python

import argparse
import requests
from requests.exceptions import Timeout, ConnectionError
from urllib.parse import urlparse

def get_status_code(url, timeout=15):        # WAITING FOR RESPONCE FROM SERVER TILL 6O SECONDS
    try:
        response = requests.get(url, timeout=timeout)
        status_code = response.status_code
        status_code = int(status_code)
    except Timeout:                                 # HANDLING STATUSCODE ON TIMEOUT
        status_code = 408
    except ConnectionError as e:
        status_code = 503                           # ISSUE ON SERVER
    except Exception as e:
        status_code = 500                           # ANY OTHER ISSUE OCCURED

    # MANAGING STATUS CODE
    status_code = int(status_code) # converting statuscode to integer
    if status_code < 400 or status_code > 600:
        status_code = 200
    elif status_code in [403]:
        status_code = 200

    if status_code == 200:
        s_id = 1
    else:
        s_id = 0

#    return {"status code": status_code, "status" : s_id}
    return ("{" + f'"code": {status_code}, "status": {s_id}' + "}")

def validate_and_format_url(url_or_domain):
    """Validates and formats a URL or domain name."""
    parsed = urlparse(url_or_domain)
    if not parsed.scheme:  # No scheme, assume it's a domain
        url_or_domain = "http://" + url_or_domain

    # Re-parse after adding the scheme (if needed)
    parsed = urlparse(url_or_domain)

    # Additional validation checks:
    if not all([parsed.scheme, parsed.netloc]):
        raise argparse.ArgumentTypeError("Invalid URL or domain name format")

    return parsed.geturl()

def main():
    parser = argparse.ArgumentParser(description="Validate and format a URL or domain name.")
    parser.add_argument("url_or_domain", type=validate_and_format_url, help="URL or domain name to validate and format.")

    args = parser.parse_args()
    print(get_status_code(args.url_or_domain))

if __name__ == "__main__":
    main()
