#!/bin/bash
# Start NovaPay web application with unbuffered python output
cd /home/ubuntu/novapay
nohup python3 -u app.py > /home/ubuntu/novapay.log 2>&1 &
