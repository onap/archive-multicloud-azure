#!/bin/bash
# Copyright (c) 2018 Amdocs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Configure MSB IP address
MSB_IP=`echo $MSB_ADDR | cut -d: -f 1`
MSB_PORT=`echo $MSB_PORT | cut -d: -f 2`
sed -i "s|MSB_SERVICE_IP.*|MSB_SERVICE_IP = '$MSB_IP'|" azure/azure/pub/config/config.py
sed -i "s|MSB_SERVICE_PORT.*|MSB_SERVICE_PORT = '$MSB_PORT'|" azure/azure/pub/config/config.py
sed -i "s|DB_NAME.*|DB_NAME = 'inventory'|" azure/azure/pub/config/config.py
sed -i "s|DB_USER.*|DB_USER = 'inventory'|" azure/azure/pub/config/config.py
sed -i "s|DB_PASSWD.*|DB_PASSWD = 'inventory'|" azure/azure/pub/config/config.py
sed -i "s|\"ip\": \".*\"|\"ip\": \"$SERVICE_IP\"|" azure/azure/pub/config/config.py

# Configure MYSQL
if [ -z "$MYSQL_ADDR" ]; then
    export MYSQL_IP=`hostname -i`
    export MYSQL_PORT=3306
    export MYSQL_ADDR=$MYSQL_IP:$MYSQL_PORT
else
    MYSQL_IP=`echo $MYSQL_ADDR | cut -d: -f 1`
    MYSQL_PORT=`echo $MYSQL_ADDR | cut -d: -f 2`
fi
echo "MYSQL_ADDR=$MYSQL_ADDR"
sed -i "s|DB_IP.*|DB_IP = '$MYSQL_IP'|" azure/azure/pub/config/config.py
sed -i "s|DB_PORT.*|DB_PORT = $MYSQL_PORT|" azure/azure/pub/config/config.py

cat azure/azure/pub/config/config.py

sed -i "s/sip=.*/sip=$SERVICE_IP/g" azure/run.sh
sed -i "s/sip=.*/sip=$SERVICE_IP/g" azure/stop.sh

# Create log directory
logDir="/var/log/onap/multicloud/azure"
if [ ! -x  $logDir  ]; then
       mkdir -p $logDir
fi
