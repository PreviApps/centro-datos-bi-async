import os
import redis
from rq import Worker


# Redis usado como backend de colas y contexto de ejecución del worker
redis_conn = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379
)

if __name__ == "__main__":
    worker = Worker(
        ["default"],
        connection=redis_conn
    )
    worker.work()