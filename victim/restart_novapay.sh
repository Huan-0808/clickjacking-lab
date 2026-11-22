#!/bin/bash
# Restart NovaPay service
pkill -f "python3 -u app.py" || pkill -f "app.py" || true
sleep 1
cd /home/ubuntu/novapay
nohup python3 -u app.py > /home/ubuntu/novapay.log 2>&1 &
echo "NovaPay has been restarted."
