import requests
import json
from . import get_default
from .exceptions import *
import time

class Order:
    def __init__(self,payload):
        self.creation_payload = payload
        self._created = False
        self.request_id = get_default().create_request_id()
        pass
    def __repr__(self) -> str:
        if not self.created:
            return f"<Order created={self.created}>"
        return f"<Order id={self.id} intent={self.intent} purchase_units={self.purchase_units} links={self.links} json={self.json} req_id={self.req_id}>"
    
    def create(self):
        if self._created:
            raise OrderAlreadyCreated("The order has already been created.")
        url =f"{get_default().base_endpoint()}/v2/checkout/orders"
        headers = {
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
        'PayPal-Request-Id': self.request_id,
        'Authorization': f"Bearer {get_default().bearer_token.token}"
        }
        response = requests.request("POST", url, headers=headers, data=json.dumps(self.creation_payload))
        handled = get_default().handle_response(response, self.creation_payload)
        resp = handled
        self.id = resp["id"]
        self.intent = resp["intent"]
        self.purchase_units = resp["purchase_units"]
        self.links = resp["links"]
        self.json = resp
        self.order_data = {}



    def approval_link(self) -> str:
        for link in self.links:
            if link["rel"] == "approve":
                return link["href"]
        return None
    def get_paypal_request_id(self) -> str:
        return self.request_id
    
    
    def is_approved(self,cached_data=True) -> bool:
        if cached_data:
            return self.order_data["status"] == "APPROVED"
        else:
            return self.get_data()["status"] == "APPROVED"
    
    def is_completed(self,cached_data=True) -> bool:
        if cached_data:
            return self.order_data["status"] == "COMPLETED"
        else:
            return self.get_data()["status"] == "COMPLETED"
    


    def get_data(self) -> dict:
        
        payload = {}
        headers = {
        'Authorization': f"Bearer {get_default().bearer_token.token}"
        }
        url = f"{get_default().base_endpoint()}/v2/checkout/orders/{self.id}"
        response = requests.request("GET", url, headers=headers, data=payload)
        handled = get_default().handle_response(response,payload)
        self.order_data = handled
        return handled
    def get_total_cost(self) -> float:
        d = self.get_data()
        total = 0
        for unit in d["purchase_units"]:
            total += float(unit["amount"]["value"])
        return total
    
    def refund(self,note):
        if not self.is_completed():
            raise OrderNotCompleted("Order has not been completed.")
        url = f"{get_default().base_endpoint()}/v2/payments/captures/{self.get_data()['purchase_units'][0]['payments']['captures'][0]['id']}/refund"

        payload = json.dumps({
        "amount": {
            "value": self.get_total_cost(),
            "currency_code": "USD"
        },
        "invoice_id": str(int(time.time())),
        "note_to_payer": note
        })
        headers = {
            'Content-Type': 'application/json',
            'PayPal-Request-Id': self.get_paypal_request_id(),
            'Prefer': 'return=representation',
            'Authorization': f'Bearer {get_default().bearer_token.token}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        handled = get_default().handle_response(response,payload)
        return handled
    
    def is_refunded(self) -> bool:
        d = self.get_data()
        return d.get("purchase_units")[0].get("payments").get("refunds") != None

    
    def capture(self) -> None:
        data  = self.get_data()
        if data.get("status") == "COMPLETED":
            raise OrderAlreadyCompleted("Order has already been completed.")
            return
        url = f"{get_default().base_endpoint()}/v2/checkout/orders/{self.id}/capture"

        payload = ""
        headers = {
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
        'PayPal-Request-Id': self.get_paypal_request_id(),
        'Authorization': f'Bearer {get_default().bearer_token.token}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        get_default().handle_response(response,payload)
        return response.json()
    



    def __str__(self) -> str:
        return f"Order(id={self.id}, intent={self.intent}, purchase_units={self.purchase_units}, links={self.links}, req_id={self.req_id}"
    





