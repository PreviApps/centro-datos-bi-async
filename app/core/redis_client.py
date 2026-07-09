import os
import redis


# Cliente Redis reutilizable, solo para la conexión (FastAPI, servicios, repositorios)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379))
)