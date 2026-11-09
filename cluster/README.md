# Overview

This setup consists of a 3-node redis cluster along with 3 replicas, one for each primary node.

# Setup

Starting the cluster

```sh
# Replace with your computer's IP
IP=YOUR_LAN_IP ./start.sh
```

To pause or stop:

```sh
# Pause
docker compose stop

# Delete
docker compose down
```

# Play around

## Verify the Cluster

```sh
docker exec -it redis-1 redis-cli -p 7001 cluster info
docker exec -it redis-1 redis-cli -p 7001 cluster nodes
```

## Resharding

```sh
# This will launch an interactive set of prompts
docker exec -it redis-1 redis-cli --cluster reshard 127.0.0.1:7000
```

## Failover

There are 2 types of failover: planned and unplanned.

Unplanned Failover simulation: simulate a node encountering an error by deliberately causing segfault

```sh
export FAIL_NODE="redis-2"
export PORT_FAIL_NODE=7002
export UP_NODE="redis-3"
export PORT_UP_NODE=7003

# Take note of the slave of the node you're planning to segfault. You want to make sure that this slave becomes the new master
docker exec -it "$UP_NODE" redis-cli -p $PORT_UP_NODE cluster nodes

# Deliberately fail that node
docker exec -it "$FAIL_NODE" redis-cli -p $PORT_FAIL_NODE debug segfault

# Check that the slave is promoted
watch -n 1 'docker exec -it "$UP_NODE" redis-cli -p $PORT_UP_NODE cluster nodes'

# Bring up the old master node again. It should rejoin as a replica.
docker restart "$FAIL_NODE" && watch -n 1 'docker exec -it "$UP_NODE" redis-cli -p $PORT_UP_NODE cluster nodes'
```

Planned Failover simulation: i.e., for routine maintenance on a node

```sh
# Find the container name of the replica of the master you want to simulate failing
# Make sure to change the container name and port
docker exec -it redis-4 redis-cli -p 7004 CLUSTER FAILOVER

# Note that Redis clients should be able to send requests as usual

# Check that the slave is promoted
docker exec -it redis-1 redis-cli -p 7001 cluster nodes
```

Benchmarking

```sh
# Don't forget --cluster flag!
docker exec -it redis-1 redis-benchmark -q -p 7001 --cluster \
 -n 100000 \
 -c 50 \
 -d 8

# Specifiy the type of test:
#  -t HSET,SADD,LPUSH
#
#  Use pipelining:
#  -P 10
#
#  Use random key:
# -r
```
