python3 crapi-gen-users.py $1 $2 $3
sleep 3;
# locust -f crapi-locust.py  --headless -r 0.1 -u $3 -t 1m -H $1
