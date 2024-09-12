import os
from . import exceptions
from .bearer import BearerToken
from .config import __api_endpoints__
import requests
import base64
import uuid

__api__ = None

class PaypalApi:
    def __init__(self,client_id,client_secret,mode="sandbox") -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.mode = mode
        self.bearer_token = None
        global __api__
        __api__ = self
        self.create_bearer_token()

    def __repr__(self) -> str:
        return f"<PaypalApi client_id={self.client_id} mode={self.mode}>"
    
    def base_endpoint(self):
        return __api_endpoints__.get(self.mode,"https://api-m.sandbox.paypal.com")
    
    def get_encoded_credentials(self):
        return (base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("utf-8"))).decode("utf-8")

    def create_bearer_token(self) -> BearerToken:
        url = f"{self.base_endpoint()}/v1/oauth2/token"
        payload = 'grant_type=client_credentials&ignoreCache=true&return_authn_schemes=true&return_client_metadata=true&return_unconsented_scopes=true'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
        headers["Authorization"] = f"Basic {self.get_encoded_credentials()}"
        response = requests.request("POST", url, headers=headers, data=payload)
        d = self.handle_response(response,payload)
        t = BearerToken(d["access_token"],d["expires_in"])
        self.bearer_token = t
        return t
    def create_request_id(self):
        return str(uuid.uuid4())
    
    def handle_response(self, response,payload):
        """Validate HTTP response
        """
        r = response
        # for deletion of invoices
        if r.text == "" and r.status_code == 204:
            return {"deletion":True}
        if response.json().get("error") == "invalid_token":
            new_token = self.create_bearer_token().token
            new_headers = response.headers
            new_headers["Authorization"] = f"Bearer {new_token}"
            r = requests.request(response.request.method, response.url, headers=new_headers, data=payload)

        if r.json().get("error") != None or r.json().get("name"):
            raise exceptions.MalformedPayload(r.json()["message"])
        status = response.status_code
        if status in (301, 302, 303, 307):
            raise exceptions.Redirection(response, response.content.decode("utf-8"))
        elif 200 <= status <= 299:
            return response.json()
        elif status == 400:
            raise exceptions.BadRequest(response, response.content.decode("utf-8"))
        elif status == 401:
            raise exceptions.UnauthorizedAccess(response, response.content.decode("utf-8"))
        elif status == 403:
            raise exceptions.ForbiddenAccess(response, response.content.decode("utf-8"))
        elif status == 404:
            raise exceptions.ResourceNotFound(response, response.content.decode("utf-8"))
        elif status == 405:
            raise exceptions.MethodNotAllowed(response, response.content.decode("utf-8"))
        elif status == 409:
            raise exceptions.ResourceConflict(response, response.content.decode("utf-8"))
        elif status == 410:
            raise exceptions.ResourceGone(response, response.content.decode("utf-8"))
        elif status == 422:
            raise exceptions.ResourceInvalid(response, response.content.decode("utf-8"))
        elif 401 <= status <= 499:
            raise exceptions.ClientError(response, response.content.decode("utf-8"))
        elif 500 <= status <= 599:
            raise exceptions.ServerError(response, response.content.decode("utf-8"))
        else:
            raise exceptions.ConnectionError(
                response, response.content.decode("utf-8"), "Unknown response code: #{response.code}")


    


def get_default():
    global __api__
    if __api__ is None:
        try:
            client_id = os.environ["PAYPAL_CLIENT_ID"]
            client_secret = os.environ["PAYPAL_CLIENT_SECRET"]
        except KeyError:
            raise exceptions.MissingConfig("Required PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET if not creating a PaypalApi manually. Use os.environ to set them.")
        __api__ = PaypalApi(client_id=client_id,client_secret=client_secret,mode=os.environ.get("PAYPAL_MODE","sandbox"))
    return __api__