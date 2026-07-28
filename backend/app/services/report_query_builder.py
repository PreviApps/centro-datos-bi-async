import re
from fastapi import HTTPException

class ReportQueryBuilder:

    PARAM_REGEX = r"@\((\w+):(string|date|number|boolean)\)"

    @staticmethod
    def compile(sql_template: str, values: dict):

        params = []

        def replacer(match):

            param_name = match.group(1)
            param_type = match.group(2)

            if param_name not in values:
                raise HTTPException(
                    status_code=400,
                    detail=f"Falta parámetro: {param_name}"
                )

            value = values[param_name]

            # Validaciones por tipo
            if param_type == "number":

                if not isinstance(value, (int, float)):
                    raise HTTPException(
                        status_code=400,
                        detail=f"{param_name} debe ser number"
                    )

            elif param_type == "boolean":

                if not isinstance(value, bool):
                    raise HTTPException(
                        status_code=400,
                        detail=f"{param_name} debe ser boolean"
                    )

            elif param_type in ["string", "date"]:

                if not isinstance(value, str):
                    raise HTTPException(
                        status_code=400,
                        detail=f"{param_name} debe ser string/date"
                    )

            params.append(value)

            return "?"

        compiled_query = re.sub(
            ReportQueryBuilder.PARAM_REGEX,
            replacer,
            sql_template
        )

        return {
            "query": compiled_query,
            "params": params
        }