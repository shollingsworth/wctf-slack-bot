#!/usr/bin/env bash
./env_setup/get_env.py dev
echo "alias envmysql='mysql -h\${SQL_ENDPOINT} -u\${SQL_USER} -p\${SQL_PASS} -P\${SQL_PORT}'"
