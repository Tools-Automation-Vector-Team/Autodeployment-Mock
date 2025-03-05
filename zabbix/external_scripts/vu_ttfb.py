#!/usr/lib/zabbix/externalscripts/env/bin/python

import argparse
import requests
from requests.exceptions import Timeout, ConnectionError
from urllib.parse import urlparse
import time

def get_ttfb(url):
    start_time = time.time()
    try:
        response = requests.get(url, stream=True)
        first_byte_time = time.time()
        for chunk in response.iter_content(chunk_size=1):
            if chunk:
                break
        result = first_byte_time - start_time
    except Exception as e:
        result = time.time() - start_time

    return round(result, 5)

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
    print(get_ttfb(args.url_or_domain))

if __name__ == "__main__":
    main()
