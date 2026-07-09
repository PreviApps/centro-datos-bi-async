import duckdb
import os

con = duckdb.connect()


def initialize_duckdb():

    print("Inicializando DuckDB")

    con.execute("""
        INSTALL httpfs;
        LOAD httpfs;
    """)

    #con.execute(f"""
    #   SET s3_endpoint='minio:9000';
    #  SET s3_access_key_id='{os.getenv("MINIO_ACCESS_KEY")}';
    # SET s3_secret_access_key='{os.getenv("MINIO_SECRET_KEY")}';
        #SET s3_use_ssl=false;
        #SET s3_url_style='path';
    #""")

    con.execute(f"""
        SET s3_endpoint='10.10.119.104:9000';
        SET s3_access_key_id='{os.getenv("MINIO_ACCESS_KEY")}';
        SET s3_secret_access_key='{os.getenv("MINIO_SECRET_KEY")}';
        SET s3_use_ssl=false;
        SET s3_url_style='path';
    """)

    con.execute("""
        SET http_timeout=60000;
        SET http_retries=5;
        SET max_memory='4GB'
    """)

    con.execute("SET threads = 2;")
    con.execute("SET max_memory = '4GB';")

    print("DuckDB listo para usar")