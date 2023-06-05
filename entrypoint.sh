#!/bin/bash
/usr/local/bin/python /app/main.py db_init

/usr/local/bin/python /app/main.py scheduler &

/usr/local/bin/python -m streamlit run /app/frontend.py &