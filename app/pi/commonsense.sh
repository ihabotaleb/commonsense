echo "Starting commonsense"
while true; do
    python3 compare_frame.py
    python3 msg.py
    echo "Scan complete and message sent at time $(date)"
    sleep 120
done