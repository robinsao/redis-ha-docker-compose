# Overview

This runs 3 redis instances in a single-primary-double-standby setup.

Sentinel is run as a cluster with 3 nodes, each running along side is corresponding redis instance.

# Setup

```sh
# Replace with your computer's IP
IP=YOUR_LAN_IP ./start.sh
```

# Play around

Export your redis password first:

```sh
export REDIS_PWD="redis_pwd"
```

While python client is running, you can simulate master hanging/failing:

```sh
export FAIL_NODE="redis-2"
export UP_NODE="redis-1"
export PORT_UP_NODE=6379

docker exec -i "$FAIL_NODE" \
    redis-cli -p 6379 \
    -a $REDIS_PWD \
    DEBUG sleep 30 &

# You should see it switch from port 6379 to another port after 5 seconds
watch -n 1 'docker exec "$UP_NODE" redis-cli -p "2$PORT_UP_NODE" SENTINEL get-master-addr-by-name mymaster'

# Verify that the old master is setup as replica. If yes, 'num-salves' should be 2
docker exec "$UP_NODE" redis-cli -p "2$PORT_UP_NODE" SENTINEL MASTERS | grep -A 5 'num-slaves'

# You can view the logs too. Look for +sdown event
docker exec -ti $UP_NODE cat /var/log/sentinel.log

# You can also view the sentinel.conf file. It should update to reflect the current state of the cluster.
```
