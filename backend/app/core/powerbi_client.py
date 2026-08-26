import os
import msal
import requests
from fastapi import HTTPException

class PowerBIClient:
    def __init__(self):
        self.client_id = os.getenv("POWERBI_CLIENT_ID")
        self.client_secret = os.getenv("POWERBI_CLIENT_SECRET")
        self.tenant_id = os.getenv("POWERBI_TENANT_ID")
        
        # Obteniendo URLs y parámetros desde el entorno
        authority_base = os.getenv("POWERBI_AUTHORITY", "https://login.microsoftonline.com")
        self.authority = f"{authority_base}/{self.tenant_id}"
        
        # MSAL espera los scopes como una lista de strings
        scope_env = os.getenv("POWERBI_SCOPE", "https://analysis.windows.net/powerbi/api/.default")
        self.scope = [scope_env] if isinstance(scope_env, str) else scope_env
        
        self.api_url = os.getenv("POWERBI_API_URL", "https://api.powerbi.com/v1.0/myorg")

    def get_workspaces(self) -> list:
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{self.api_url}/groups", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error al obtener workspaces de Power BI")
        return response.json().get("value", [])

    def get_reports_by_workspace(self, workspace_id: str) -> list:
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{self.api_url}/groups/{workspace_id}/reports", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error al obtener reportes de Power BI")
        return response.json().get("value", [])

    def get_access_token(self) -> str:
        if not self.client_id or not self.client_secret or not self.tenant_id:
            raise HTTPException(
                status_code=500,
                detail="Faltan credenciales de Power BI en las variables de entorno (.env)"
            )

        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        result = app.acquire_token_for_client(scopes=self.scope)
        
        if "access_token" in result:
            return result["access_token"]
        
        raise HTTPException(
            status_code=500,
            detail=f"Error al autenticar con Power BI: {result.get('error_description', 'Desconocido')}"
        )

    def get_embed_token(self, workspace_id: str, report_id: str) -> dict:
        access_token = self.get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Construcción de la URL utilizando la variable de entorno POWERBI_API_URL
        url = f"{self.api_url}/groups/{workspace_id}/reports/{report_id}/GenerateToken"
        payload = {"accessLevel": "View"}

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al generar Embed Token de Power BI: {response.text}"
            )
            
        return response.json()