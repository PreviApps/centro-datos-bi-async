from app.core.minio_client import BUCKET
from fastapi import HTTPException
import re
import json
import numpy as np
import pandas as pd
import polars as pl
from app.core.duckdb_client import con

class DuckDBService:

    @staticmethod
    def validate_query(query: str):
        forbidden = [
            "DROP",
            "DELETE",
            "UPDATE",
            "INSERT",
            "ALTER",
            "COPY",
            "INSTALL",
            "LOAD"
        ]

        upper_query = query.upper()

        for word in forbidden:
            if word in upper_query:
                raise HTTPException(
                    status_code=400,
                    detail=f"Operación no permitida: {word}"
                )
            
    @staticmethod
    def get_parquet_metadata(path: str):
        try:

            s3_path = f"s3://{BUCKET}/{path}"

            describe_query = f"""
                DESCRIBE
                SELECT *
                FROM read_parquet('{s3_path}')
            """

            count_query = f"""
                SELECT COUNT(*) as total
                FROM read_parquet('{s3_path}')
            """

            schema = con.execute(
                describe_query
            ).fetchdf()

            total_rows = con.execute(
                count_query
            ).fetchone()[0]

            print("SCHEMA", schema)
            print("#################")
            print("ROWS", total_rows)

            return {

                "table_name": path.split("/")[-1],

                "path": path,

                "total_rows": total_rows,

                "total_columns": len(schema),

                "schema": schema.to_dict(
                    orient="records"
                )
            }
        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
            
    @staticmethod
    def apply_limit(query: str, limit: int = 10):

        # Si ya tiene LIMIT no lo tocamos
        if re.search(r"\bLIMIT\b", query, re.IGNORECASE):
            return query

        query = query.strip().rstrip(";")

        return f"{query} LIMIT {limit}"

    @staticmethod
    def build_columns(df):
        return [
            {
                "name": col,
                "dtype": str(df[col].dtype)
            }
            for col in df.columns
        ]
    
    @staticmethod
    def replace_parquet_paths(query: str):

        pattern = r"read_parquet\(['\"](.*?)['\"]\)"

        def replacer(match):

            parquet_path = match.group(1)

            # Si ya viene con s3:// no tocar
            if parquet_path.startswith("s3://"):
                return match.group(0)

            s3_path = f"s3://{BUCKET}/{parquet_path}"

            return f'read_parquet("{s3_path}")'

        return re.sub(
            pattern,
            replacer,
            query,
            flags=re.IGNORECASE
        )

    @staticmethod
    def execute_query(query: str, params: list = None, limit: int = 20):

        DuckDBService.validate_query(query)

        query = DuckDBService.replace_parquet_paths(query)

        query = DuckDBService.force_limit(query, limit)

        try:

            result = con.execute(
                query,
                params or []
            ).fetchdf()

            clean_rows = DuckDBService._serializable_dataframe(result)

            return {
                "metadata": {
                    "table_name": "query_result"
            },
                "columns": DuckDBService.build_columns(result),
                #"rows": result.to_dict(orient="records"),
                "rows": clean_rows,
                "row_count": len(result),
                "query_executed": query
            }

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
        
    @staticmethod
    def preview_parquet(path: str, limit: int = 10):
        try:

            # Seguridad básica
            if ".." in path:

                raise HTTPException(
                    status_code=400,
                    detail="Ruta inválida"
                )

            if not path.endswith(".parquet"):

                raise HTTPException(
                    status_code=400,
                    detail="El archivo debe ser parquet"
                )

            s3_path = f"s3://{BUCKET}/{path}"

            query = f"""
                SELECT *
                FROM read_parquet('{s3_path}')
                LIMIT {limit}
            """

            #metadata = DuckDBService.get_parquet_metadata(path)
            metadata = 1

            print("QUERY:", query)

            result = con.execute(query).fetchdf()

            clean_rows = DuckDBService._serializable_dataframe(result)

            return {
                "metadata": metadata,
                "query_executed": query,
                "columns": DuckDBService.build_columns(result),
                "row_count": len(result),
                #"rows": result.to_dict(orient="records")
                "rows": clean_rows
            }

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
        
    @staticmethod
    def force_limit(query: str, limit: int = 20):

        query = query.strip().rstrip(";")

        # eliminar LIMIT existente (opcional pero recomendado)
        query = re.sub(r"\bLIMIT\s+\d+\b", "", query, flags=re.IGNORECASE)

        return f"{query} LIMIT {limit}"
    
    @staticmethod
    def export_query_to_excel(
        query: str,
        params: dict,
        output_path: str
    ):
        from app.core.duckdb_client import con

        DuckDBService.validate_query(query)

        query = DuckDBService.replace_parquet_paths(query)

        print("QUERY OME", query)

        result = con.execute(
            query,
            params
        )

        arrow_table = result.arrow()

        df = pl.from_arrow(arrow_table)

        df.write_excel(output_path)

        return {
            "rows": df.height,
            "columns": df.width,
            "path": output_path
        }

    @staticmethod
    def _serializable_dataframe(df: pd.DataFrame) -> list:
        """
        Método interno para limpiar tipos extraños de Pandas (como Timestamps, NaN, Inf)
        y convertirlos a tipos nativos primitivos de Python que PostgreSQL entienda 100%.
        """
        # 1. Convertir columnas de fecha/tiempo a string ISO antes de tocar nulos
        for col in df.select_dtypes(include=['datetime', 'datetimetz']).columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

        # 2. Reemplazar NaN, Infinitos y nulos usando la API nativa de Pandas
        df = df.replace([np.nan, np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)

        # 3. Forzar serialización a JSON para destruir Timestamps ocultos y retornar la lista de registros
        return json.loads(df.to_json(orient="records", date_format="iso"))