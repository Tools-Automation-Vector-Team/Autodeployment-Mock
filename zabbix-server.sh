#!/bin/bash

# Prompt the user for input
read -p "Enter the Zabbix database name: " ZABBIX_DB
read -p "Enter the Zabbix database user: " ZABBIX_USER
read -sp "Enter the Zabbix database password: " ZABBIX_PASSWORD
echo
read -sp "Enter the MySQL root password: " MYSQL_ROOT_PASSWORD
echo
read -p "Enter the Zabbix server name: " ZABBIX_SERVER_NAME

# Get the Ubuntu version
UBUNTU_VERSION=$(lsb_release -sr)_all

# Step 1: Download and install Zabbix repository
wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_7.0-1+ubuntu${UBUNTU_VERSION}.deb
dpkg -i zabbix-release_7.0-1+ubuntu${UBUNTU_VERSION}.deb

# Step 2: Update package index and install Zabbix packages
apt update
apt install -y mysql-server zabbix-server-mysql zabbix-frontend-php zabbix-nginx-conf zabbix-sql-scripts zabbix-agent2

# Step 3: Set up MySQL database for Zabbix
mysql -uroot -p${MYSQL_ROOT_PASSWORD} <<MYSQL_SCRIPT
CREATE DATABASE ${ZABBIX_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
CREATE USER '${ZABBIX_USER}'@'localhost' IDENTIFIED BY '${ZABBIX_PASSWORD}';
GRANT ALL PRIVILEGES ON ${ZABBIX_DB}.* TO '${ZABBIX_USER}'@'localhost';
SET GLOBAL log_bin_trust_function_creators = 1;
FLUSH PRIVILEGES;
MYSQL_SCRIPT

# Step 4: Import initial schema and data for Zabbix server
zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -u${ZABBIX_USER} -p${ZABBIX_PASSWORD} ${ZABBIX_DB}

# Step 5: Revert log_bin_trust_function_creators setting
mysql -uroot -p${MYSQL_ROOT_PASSWORD} <<MYSQL_SCRIPT
SET GLOBAL log_bin_trust_function_creators = 0;
MYSQL_SCRIPT

# Step 6: Update Zabbix server configuration
sed -i "s/^# DBPassword=.*/DBPassword=${ZABBIX_PASSWORD}/" /etc/zabbix/zabbix_server.conf

# Custom Zabbix server settings
sed -i "s/^StartPollers=.*/StartPollers=80/" /etc/zabbix/zabbix_server.conf
sed -i "s/^StartPingers=.*/StartPingers=10/" /etc/zabbix/zabbix_server.conf
sed -i "s/^StartPollersUnreachable=.*/StartPollersUnreachable=80/" /etc/zabbix/zabbix_server.conf
sed -i "s/^StartIPMIPollers=.*/StartIPMIPollers=10/" /etc/zabbix/zabbix_server.conf
sed -i "s/^StartTrappers=.*/StartTrappers=20/" /etc/zabbix/zabbix_server.conf
sed -i "s/^StartDBSyncers=.*/StartDBSyncers=6/" /etc/zabbix/zabbix_server.conf
sed -i "s/^# CacheSize=.*/CacheSize=256M/" /etc/zabbix/zabbix_server.conf
sed -i "s/^# HistoryCacheSize=.*/HistoryCacheSize=32M/" /etc/zabbix/zabbix_server.conf
sed -i "s/^# TrendCacheSize=.*/TrendCacheSize=16M/" /etc/zabbix/zabbix_server.conf
sed -i "s/^# StartPollers=.*/StartPollers=10/" /etc/zabbix/zabbix_server.conf
sed -i "s/^# StartPingers=.*/StartPingers=5/" /etc/zabbix/zabbix_server.conf
sed -i "s/^# HousekeepingFrequency=.*/HousekeepingFrequency=1/" /etc/zabbix/zabbix_server.conf
sed -i -e 's/^# ExternalScripts=\/usr\/lib\/zabbix\/externalscripts/ExternalScripts=\/usr\/lib\/zabbix\/externalscripts/' -e 's/^Timeout=4$/Timeout=30/' /etc/zabbix/zabbix_server.conf
sed -i 's/^# Timeout=3$/Timeout=30/' /etc/zabbix/zabbix_agent2.conf
sed -i 's/^# PluginTimeout=.*/PluginTimeout=30/' /etc/zabbix/zabbix_agent2.conf





# Step 7: Update Nginx configuration
sed -i "s/^#\s*listen\s.*/listen 5121;/" /etc/zabbix/nginx.conf
sed -i "s/^#\s*server_name\s.*/server_name ${ZABBIX_SERVER_NAME};/" /etc/zabbix/nginx.conf

# Step 8: Restart and enable services
systemctl restart zabbix-server zabbix-agent2 nginx php8.1-fpm
systemctl enable zabbix-server zabbix-agent2 nginx php8.1-fpm

# Step 9: Remove Instalation Script 
rm zabbix-server.sh
echo "Zabbix installation and configuration complete."
