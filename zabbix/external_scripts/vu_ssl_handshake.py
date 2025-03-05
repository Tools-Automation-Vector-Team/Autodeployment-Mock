#!/usr/lib/zabbix/externalscripts/env/bin/python
# ssl handshake time

import argparse
import ssl
import socket
from urllib.parse import urlparse
import time

def get_ssl_handshake_time(self):
    error_start = time.time()
    try:
        context = ssl.create_default_context()
        with socket.create_connection((self.hostname, 443)) as sock:
            start_time = time.time()
            with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                result = time.time() - start_time
    except Exception:
        result = time.time() - error_start

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
    print(get_ssl_handshake_time(args.url_or_domain))

if __name__ == "__main__":
    main()
