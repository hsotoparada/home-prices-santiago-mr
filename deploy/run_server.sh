#! /bin/bash

# start nginx
# service nginx start
/usr/sbin/nginx

# start gunicorn
# cd server/
# gunicorn --bind :8080 --workers 5 --timeout 1000 --preload server:app

# start flask server
python server/server.py