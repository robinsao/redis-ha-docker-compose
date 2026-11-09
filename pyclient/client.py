
import random
import time
from typing import Literal

from redis.cluster import ClusterNode, RedisCluster
from redis import Sentinel

REDIS_MODE : Literal["sentinel", "cluster"] = "cluster"
TARGET_RPS = 10000

KEY_PREFIX = "benchmark:"

REDIS_PWD = "redis_pwd"
TIMEOUT_SECONDS = 6.5

# Redis Cluster configuration
def get_redis_cluster():
    rc = RedisCluster(
        startup_nodes=[
            ClusterNode("127.0.0.1", 7001),
            ClusterNode("127.0.0.1", 7002),
            ClusterNode("127.0.0.1", 7003),
        ],
        decode_responses=True,
    )
    return rc


def get_sentinel():
    s = Sentinel([
        ("127.0.0.1", 26379),
        ("127.0.0.1", 26380),
        ("127.0.0.1", 26381),
    ],
    password=REDIS_PWD,
    socket_timeout=TIMEOUT_SECONDS)
    return s.master_for("mymaster")


def main():
    if REDIS_MODE == "cluster":
        r = get_redis_cluster()
    else:
        r = get_sentinel()

    req_interval = 1 / TARGET_RPS

    # Optional: prepopulate some keys
    for i in range(1000):
        r.set(f"{KEY_PREFIX}{i}", f"value-{i}")

    print(f"Starting Redis benchmark at {TARGET_RPS} RPS...")

    prev_total_ops = 0
    total_ops = 0
    total_errors = 0

    time_curr_run = time.perf_counter()
    time_next_run = time.perf_counter()

    try:
        while True:
            now = time.perf_counter()

            if now < time_next_run:
                time.sleep(time_next_run - now)

            key = f"{KEY_PREFIX}{random.randint(0, 999)}"

            try:
                # Randomly select SET or GET
                if random.random() < 0.5:
                    r.set(key, f"value-{random.randint(0, 999999)}")
                else:
                    r.get(key)
            except KeyboardInterrupt:
                return
            except:
                total_errors += 1

            total_ops += 1

            time_next_run += req_interval

            # Report throughput every second
            now = time.perf_counter()
            if now - time_curr_run >= 1:
                print(
                    f"Total operations: {total_ops} |"
                    f"Delta operations: +{total_ops - prev_total_ops} |"
                    f"Total errors: {total_errors}"
                )
                time_curr_run = now
                prev_total_ops = total_ops

    except KeyboardInterrupt:
        print(f"\nStopped. Total operations: {total_ops}")

    finally:
        r.close()


main()
