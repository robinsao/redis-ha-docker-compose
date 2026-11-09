#!/bin/bash
IMG="redis:8.8.0-alpine3.23"

for port in {7001..7006}; do 
    PORT=${port} IP="$IP" envsubst < ./redis-cluster.tmpl > ./${port}-conf; 
done

docker pull "$IMG"
docker compose up -d

sleep 2

docker exec -it redis-1 redis-cli \
 --cluster create \
 $IP:7001 \
 $IP:7002 \
 $IP:7003 \
 $IP:7004 \
 $IP:7005 \
 $IP:7006 \
 --cluster-replicas 1 \
 --cluster-yes
