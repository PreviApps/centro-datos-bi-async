from fastapi import HTTPException
from datetime import timedelta

from app.core.minio_client import client, BUCKET
#from minio.select import (SelectRequest, ParquetInputSerialization, CSVInputSerialization, CSVOutputSerialization)

class MinioRepository:

    async def list_buckets(self):
        try:
            return client.list_buckets()
        except:
            raise HTTPException(404, "No se encontaron buckets")
        
    
    async def list_objects(self, path: str = ""):
        try:
            objects = client.list_objects(bucket_name=BUCKET, prefix=path, recursive=False)
            return [
                {
                    "object_name": obj.object_name,
                    "is_dir": obj.is_dir,
                    "size": obj.size
                }
                for obj in objects
            ]

        except Exception as e:
            raise HTTPException(500, str(e)) 
         
        
    """async def get_object(self, path: str):
        result = None
        try:
            print("PATH", path)
            #result = client.get_object(bucket_name=BUCKET, object_name="DGH EXAMPLE/part-00000-5ab75775-d33d-48b9-8bd1-7338b613e34c-c000.snappy.parquet")
            result = client.get_object(bucket_name=BUCKET, object_name=path)

            #data = result.read()

            #df = pl.read_parquet(io.BytesIO(data))

            #return df.head(10).to_dicts()

            with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:

                for chunk in result.stream(32 * 1024):
                    tmp.write(chunk)

                tmp.flush()

                df = (
                    pl.scan_parquet(tmp.name)
                    .head(10)
                    .collect()
                )

                return df.to_dicts()
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if result:
                result.close()
                result.release_conn()
        """

    '''async def execute_query_parquet(self):
        try:
            result = client.select_object_content(bucket_name=BUCKET, 
                                                  object_name="DGH EXAMPLE/part-00000-5ab75775-d33d-48b9-8bd1-7338b613e34c-c000.snappy.parquet",
                                                  request=SelectRequest("SELECT * FROM S3Object s LIMIT 10",
                                                                CSVInputSerialization(),
                                                                CSVOutputSerialization(),
                                                                request_progress=True),)
            print(result)
            with result as response:
                return response
        except:
            raise HTTPException(500, "Hubo un error")
     '''   

    '''@staticmethod
    def upload_file(file_path: str, object_name: str):
        try:
            client.fput_object(
                BUCKET,
                object_name,
                file_path
            )
            #return object_name
            return {
                "object_name": object_name,
                "url": client.presigned_get_object(BUCKET, object_name)
            }

        except Exception as e:
            raise HTTPException(500, str(e))'''
    
    def upload_file(self, file_path: str, object_name: str):
        try:
            print("🔥 UPLOADING TO MINIO:")
            print("BUCKET:", BUCKET)
            print("OBJECT:", object_name)
            print("FILE:", file_path)

            client.fput_object(
                BUCKET,
                object_name,
                file_path
            )

            print("✅ UPLOAD DONE")

            return {
                "object_name": object_name,
                #"url": client.presigned_get_object(BUCKET, object_name, expires=timedelta(minutes=5))
            }

        except Exception as e:
            print("❌ MINIO ERROR:", str(e))
            raise HTTPException(500, str(e))

    @staticmethod
    def get_url(object_name: str):
        try:
            return client.presigned_get_object(
                BUCKET,
                object_name,
                expires=timedelta(minutes=5)
            )
        except Exception as e:
            raise HTTPException(500, str(e))