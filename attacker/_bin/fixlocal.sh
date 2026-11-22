#!/bin/bash
# Start Python HTTP server in background under user ubuntu
# Serving /home/ubuntu/www on port 8000
mkdir -p /home/ubuntu/www
cd /home/ubuntu/www
nohup python3 -m http.server 8000 > /home/ubuntu/http_server.log 2>&1 &
