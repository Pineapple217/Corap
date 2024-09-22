#!/bin/bash
set -e

/usr/local/bin/python /app/main.py db_init

exec /usr/local/bin/python /app/main.py scheduler
