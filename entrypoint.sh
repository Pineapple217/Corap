#!/bin/bash
/usr/local/bin/python /app/main.py db_init

printenv | grep -v "no_proxy" >> /etc/environment

/bin/sh -c cron && tail -f /var/log/cron.log

/usr/local/bin/python -m streamlit run /app/frontend.py