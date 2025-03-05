#!/bin/bash

# Website URL
WEBSITE_URL="$1"

# Measure page load time
start_time=$(date +%s.%N)
curl -s -o /dev/null -w "%{time_total}" $WEBSITE_URL
end_time=$(date +%s.%N)

# Calculate page load time in seconds
page_load_time=$(echo "$end_time - $start_time" | bc | cut -d'.' -f1)

# Print page load time in seconds
echo "$page_load_time"
