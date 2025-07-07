import msal
import requests
import json
import os
from dotenv import load_dotenv
import time

class GPT_Model:
    def __init__(self):
        load_dotenv(override=True)
        self.username = os.getenv('Username')
        self.password = os.getenv('Password')
        self.client_id = os.getenv('client_id')
        self.tenant_id = os.getenv('tenant_id')
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ['api://id/API.Read']

    def authenticate_user(self):
        # Create a confidential client application
        app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
        )
        
        # Acquire token using username and password
        result = app.acquire_token_by_username_password(
            username=self.username,
            password=self.password,
            scopes=self.scope
        )
        
        if "access_token" in result:
            return result["access_token"]
        else:
            print("Failed to authenticate.")
            print(result.get("error"))
            print(result.get("error_description"))

    def chat(self,chat_msg):
        """
        Args:
            chat_msg: it is list [{"role": "system", "content": system_prompt},{"role": "user", "content": user_prompt}]
        """
        try:
            user_token = self.authenticate_user()
            print(user_token)
            url = "token_url"

            payload = json.dumps(chat_msg)
            headers = {
            'Content-Type': 'application/json-patch+json',
            'Authorization': f'Bearer {user_token}',
            'accept': 'text/plain'
            }
            response = requests.request("POST", url, headers=headers, data=payload,verify=False)
            return response
        except Exception as ex:
            raise
