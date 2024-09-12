import requests
import json
from paypalpython.api import get_default
from paypalpython.exceptions import *




class Invoice:
    def __init__(self, payload) -> None:
        self.creation_payload = payload
        self.invoice_data = None
        self.paypal_request_id = get_default().create_request_id()
        self.id = ""
        self._deleted = False
        self._created = False
        self.payment_ids = []
        self.refund_ids = []
    

    def create(self):
        if self._created:
            raise InvoiceAlreadyCreated("The invoice has already been created.")
        url =f"{get_default().base_endpoint()}/v2/invoicing/invoices"

        payload = json.dumps(self.creation_payload or {})
        headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': self.paypal_request_id,
        "Prefer":"return=representation",
        'Authorization': f'Bearer {get_default().bearer_token.token}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        handled = get_default().handle_response(response,payload)
        self.invoice_data = handled
        self.id = handled["id"]
        self._created = True
        return handled
    def get_send_link(self,load):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has been deleted.")
        url = f"{get_default().base_endpoint()}/v2/invoicing/invoices/{self.id}/send"

        payload = json.dumps(load or {})
        headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': self.paypal_request_id,
        'Authorization': f'Bearer {get_default().bearer_token.token}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        handled = get_default().handle_response(response, payload)
        return handled["href"]
    def get_data(self):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has been deleted.")
        url = f"{get_default().base_endpoint()}/v2/invoicing/invoices/{self.id}"

        payload  = {}
        headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': self.paypal_request_id,
        'Authorization': f'Bearer {get_default().bearer_token.token}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        handled = get_default().handle_response(response, payload)
        self.invoice_data = handled
        return handled
    def is_paid(self,cached_data=True):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has been deleted.")
        if cached_data:
            return self.invoice_data["status"] == "PAID" or self.invoice_data["status"] == "MARKED_AS_PAID" or self.invoice_data["status"] == "PARTIALLY_PAID"
        else:
            d = self.get_data()
            return d["status"] == "PAID" or d["status"] == "MARKED_AS_PAID" or d["status"] == "PARTIALLY_PAID"
    def is_refunded(self,cached_data=True):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has been deleted.")
        if cached_data:
            return self.invoice_data["status"] == "REFUNDED" or self.invoice_data["status"] == "PARTIALLY_REFUNDED"
        else:
            return self.get_data()["status"] == "REFUNDED" or self.get_data()["status"] == "PARTIALLY_REFUNDED"
    def is_deleted(self):
        return self._deleted
    def delete(self):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has already been deleted.")
        self.get_data()
        if self.invoice_data["status"] != "DRAFT":
            raise InvoiceNotDraft("The invoice is not a draft. Use invoice.cancel() to cancel a sent invoice.")
        url = f"{get_default().base_endpoint()}/v2/invoicing/invoices/{self.id}"

        payload  = {}
        headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': self.paypal_request_id,
        'Authorization': f'Bearer {get_default().bearer_token.token}'
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)
        handled = get_default().handle_response(response, payload)
        if handled["deletion"] == True:
            self._deleted = True
        self.invoice_data = handled
        return handled
    def cancel(self,load):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has been deleted.")
        url = f"{get_default().base_endpoint()}/v2/invoicing/invoices/{self.id}/cancel"

        payload  = json.dumps(load)
        headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': self.paypal_request_id,
        'Authorization': f'Bearer {get_default().bearer_token.token}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        handled = get_default().handle_response(response, payload)
        self.invoice_data = handled
        return handled
    
    def get_total_invoice_cost(self):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has been deleted.")
        d = self.get_data()
        return d['amount']['value']
    
    def record_external_payment(self,load):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has been deleted.")
        url = f"{get_default().base_endpoint()}/v2/invoicing/invoices/{self.id}/payments"
        payload = json.dumps(load or {})
        headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': self.paypal_request_id,
        'Authorization': f'Bearer {get_default().bearer_token.token}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        handled = get_default().handle_response(response,payload)
        self.payment_ids.append(handled['payment_id'])
        return handled['payment_id']
    

    def record_external_refund(self,load):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has been deleted.")
        if not self.is_paid(False):
            raise InvoiceNotPaid("The invoice has not been paid yet")
        url = f"{get_default().base_endpoint()}/v2/invoicing/invoices/{self.id}/refunds"
        payload = json.dumps(load or {})
        headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': self.paypal_request_id,
        'Authorization': f'Bearer {get_default().bearer_token.token}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        handled = get_default().handle_response(response, payload)
        self.refund_ids.append(handled['refund_id'])
        return handled
    def delete_external_payment(self,payment_id):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has been deleted.")
        if payment_id not in self.payment_ids:
            raise KeyError("Given payment id does not exist or is not part of this invoice")
        url = f"{get_default().base_endpoint()}/v2/invoicing/invoices/{self.id}/payments/{payment_id}"

        payload = {}
        headers = {
        'PayPal-Request-Id': self.paypal_request_id,
        'Authorization': f'Bearer {get_default().bearer_token.token}'
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)
        handled = get_default().handle_response(response,{})
        self.payment_ids.remove(payment_id)
        return handled
    def delete_external_refund(self,refund_id):
        if self.is_deleted():
            raise InvoiceDeleted("The invoice has been deleted.")
        if refund_id not in self.refund_ids:
            raise KeyError("Given refund id does not exist or is not part of this invoice")
        url = f"{get_default().base_endpoint()}/v2/invoicing/invoices/{self.id}/refunds/{refund_id}"

        payload = {}
        headers = {
        'PayPal-Request-Id': self.paypal_request_id,
        'Authorization': f'Bearer {get_default().bearer_token.token}'
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)
        handled = get_default().handle_response(response,{})
        self.refund_ids.remove(refund_id)
        return handled