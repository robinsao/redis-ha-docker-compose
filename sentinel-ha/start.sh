#!/bin/bash
IMG="redis:8.8.0-alpine3.23"
REDIS_PWD="redis_pwd"

for port in {26379..26381}; do 
    sentinelid=$((port-26378))
    filenameconf="./sentinel$sentinelid/sentinel.conf"
    mkdir -p "sentinel$sentinelid"
    if [[ -f "$filenameconf" ]]; then
        sudo chown $(id -u):$(id -g) "$filenameconf"  
    fi
    PORT=${port} IP="$IP" REDIS_PORT=6379 REDIS_PWD=${REDIS_PWD} envsubst < ./sentinel-conf.tmpl > "$filenameconf"
done

docker pull "$IMG"
docker compose up -d

sleep 2

# Verify replication
for i in {2..3}; do
    echo "Replication status for redis-$i: "
    docker exec -ti "redis-$i" redis-cli -a ${REDIS_PWD} -p 6379 INFO replication
done

echo -e "\n\n\nStarting sentinel processes"

# Start the sentinel instances
for i in {1..3}; do
    docker exec "redis-$i" touch /var/log/sentinel.log
    docker exec "redis-$i" redis-sentinel /usr/local/etc/redis/sentinel.conf --daemonize yes
done

sleep 3

echo -e "\n\n\n"

# Verify sentinel cluster is healthy
for i in {1..3}; do
    echo -e "\nVerify sentinel on redis-$i:"
    docker exec "redis-$i" redis-cli -p 26379 SENTINEL MASTERS | grep -A 5 'num-slaves'
done
