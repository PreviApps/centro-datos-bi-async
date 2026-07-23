import os
from minio import Minio
from minio.lifecycleconfig import LifecycleConfig
from minio.commonconfig import Filter
from minio.replicationconfig import Status
import urllib3

timeout_config = urllib3.Timeout(connect=5.0, read=15.0)
http_client = urllib3.PoolManager(
    timeout= timeout_config,
    retries=False,
    cert_reqs="CERT_NONE"
)

client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)

#BUCKET = os.getenv("MINIO_BUCKET", "exports")
BUCKET = os.getenv("MINIO_BUCKET", "silver")

if not client.bucket_exists(BUCKET):
    client.make_bucket(BUCKET)

lifecycle_config = LifecycleConfig([
        LifecycleConfig.Rule(
            status=Status.ENABLED,
            rule_filter=Filter(prefix="temp/"),
            rule_id="delete-temp-files",
            expiration=LifecycleConfig.Expiration(days=1),
        )
    ])

try:
    client.set_bucket_lifecycle(BUCKET, lifecycle_config)
    print(f"Regla LifeCycle 'temp/' aplicada correctamente al bucket '{BUCKET}'")
except Exception as e:
    print(f'Error al configurar el Lifecycle en MinIO: {e}')