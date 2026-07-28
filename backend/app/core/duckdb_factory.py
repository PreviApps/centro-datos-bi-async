import duckdb
import os

def create_connection():
    
    con = duckdb.connect()

    con.execute("""
        INSTALL httpfs;
        LOAD httpfs;
    """)

    con.execute(f"""
        SET s3_endpoint='10.10.119.104:9000';
        SET s3_access_key_id='{os.getenv("MINIO_ACCESS_KEY")}';
        SET s3_secret_access_key='{os.getenv("MINIO_SECRET_KEY")}';
        SET s3_use_ssl=false;
        SET s3_url_style='path';
    """)

    con.execute("""
        SET http_timeout=600000;
        SET http_retries=10;
        SET threads=2;
        SET max_memory='4GB';
        SET temp_directory='/tmp/duckdb_spill';
        SET enable_object_cache=false;
    """)

    return con