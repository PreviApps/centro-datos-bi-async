from rq import Queue
from app.core.redis_client import redis_client

queue = Queue(connection=redis_client)