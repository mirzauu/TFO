from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests

class QueryNvidiaNimInput(BaseModel):
    """Input schema for the NVIDIA NIM Tool."""
    endpoint: str = Field(..., description="The API endpoint to query (e.g., '/devices').")
    method: str = Field("GET", description="HTTP method to use (e.g., 'GET' or 'POST').")
    data: dict = Field(None, description="Payload for POST/PUT requests.")
    headers: dict = Field(None, description="Additional HTTP headers.")

class QueryNvidiaNimTool(BaseTool):
    name: str = "query_nvidia_nim"
    description: str = (
        "Tool to query NVIDIA NIM API for network management tasks. "
        "Use it to interact with NVIDIA infrastructure and retrieve relevant information."
    )
    args_schema: Type[BaseModel] = QueryNvidiaNimInput

    def _run(self, endpoint: str, method: str = "GET", data: dict = None, headers: dict = None) -> str:
        """
        Query the NVIDIA NIM API.
        """
        base_url = "https://integrate.api.nvidia.com/v1"  # Replace with the actual base URL
        url = f"{base_url}{endpoint}"

        default_headers = {
            "Authorization": "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",
            "Content-Type": "application/json",
        }
        if headers:
            default_headers.update(headers)

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers)
            else:
                return f"HTTP method {method} not supported."
            
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error querying NVIDIA NIM API: {str(e)}"
