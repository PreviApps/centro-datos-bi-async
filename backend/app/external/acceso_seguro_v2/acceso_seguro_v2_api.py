import os
import requests
from fastapi import HTTPException, status

class AccesoSeguroService:
    def __init__(self):
        self.base_url = os.getenv("ACCESO_SEGURO_BACKEND_URL", "https://api-acceso-seguro-v2.previsalud.com.co")
        self.api_key = os.getenv("INTER_SERVICE_API_KEY", "")

    def get_all_users(self) -> list:
        try:
            url = f"{self.base_url}/users/searchUsersAccesoSeguroApi"
            headers = {
                "x-api-key": self.api_key
            }

            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Error al comunicarse con Acceso Seguro (SSO)."
                )

            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error de red consumiendo Acceso Seguro: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo conectar con el servicio de Acceso Seguro."
            )