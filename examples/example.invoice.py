import datetime
import paypalpython


api = paypalpython.PaypalApi(client_id="client_id_here",client_secret="client_secret_here",mode="sandbox")




"""
/
/    INVOICE CREATION
/
"""

invoice = paypalpython.Invoice({
        "detail": {
            "invoice_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "payment_term": {
            "term_type": "DUE_ON_DATE_SPECIFIED",
            "due_date": datetime.datetime.now().strftime("%Y-%m-%d")
            },
            "currency_code": "USD",
            "reference": "<The reference data. Includes a post office (PO) number.>",
            "note": "This invoice must be completed today to recieve the merchandise.",
            "terms_and_conditions": "<The general terms of the invoice. Can include return or cancellation policy and other terms and conditions.>",
            "memo": "<A private bookkeeping note for merchant.>"
        },
        "invoicer": {
            "business_name":"Nitrostorm Games",
            "name": {
            "given_name": "Atharv",
            "surname": "Konkala"
            },
            "address": {
            "address_line_1": "1035 University Avenue",
            "admin_area_2": "San Diego",
            "admin_area_1": "CA",
            "postal_code": "92103",
            "country_code": "US"
            },
            "website": "www.example.com",
            "tax_id": "XX-XXXXXXX",
            "logo_url": "https://example.com/logo.png",
            "additional_notes": "<Any additional information. Includes business hours.>"
        },
        "primary_recipients": [
            {
            "billing_info": {
                "name": {
                "given_name": "Akshar",
                "surname": "Desai"
                },
                "email_address": "denniscool1@gmail.com",
                "additional_info_value": "add-info"
            },
            }
        ],
        "items": [
            {
            "name": "Turtle Clicker",
            "description": "Idle Turtle Clicking Game",
            "quantity": "1",
            "unit_amount": {
                "currency_code": "USD",
                "value": "7.99"
            },
            "tax": {
                "name": "Sales Tax",
                "percent": "7.25"
            },
            "unit_of_measure": "QUANTITY"
            },
            {
            "name": "Turret Overload",
            "quantity": "1",
            "unit_amount": {
                "currency_code": "USD",
                "value": "9.99"
            },
            "tax": {
                "name": "Sales Tax",
                "percent": "7.25"
            },
            "unit_of_measure": "QUANTITY"
            }
        ],
        "configuration": {
            "allow_tip": False,
            "tax_calculated_after_discount": True,
            "tax_inclusive": False
        },
        "amount": {
            "breakdown": {
              "discount": {
                "invoice_discount": {
                "percent":"10"
                }
            },
            "custom": {
                "label": "Paypal Fees",
                "amount":{
                    "currency_code":"USD",
                    "value": paypalpython.util.calculate_paypal_invoice_fee(7.99+9.99)
                }
            }
            }
        }
        })

invoice.create()
# invoice.delete()
link = invoice.get_send_link(load={
        "subject": "<The subject of the email that is sent as a notification to the recipient.>",
        "note": "<Note to the payer.>",
        "send_to_recipient": False,
        "send_to_invoicer": False
        })
# invoice.cancel({
#     "subject": "<The subject of the email that is sent as a notification to the recipient.>",
#     "note": "<A note to the payer.>",
#     "send_to_invoicer": True,
#     "send_to_recipient": True,
#     "additional_recipients": [
#         "user_in_cc@example.com"
#     ]
# })
print(invoice.get_total_invoice_cost())
print(f"Invoice Link: {link}")
pay = None
record_external = input("Mark invoice as paid in full? y/n: ").lower()
if record_external == 'y':
    pay = invoice.record_external_payment({
            "method": "CASH",
            "payment_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "amount": {
                "currency_code": "USD",
                "value": str(invoice.get_total_invoice_cost())
            },
            "type": "EXTERNAL",
            "transaction_type": "CAPTURE",
            "note": "<A note associated with an external cash or check payment.>",
            })
else:
    print("Did not mark as paid.")
# invoice.delete_external_payment(pay)

while True:
    input("Press enter when invoice is paid.")
    if invoice.is_paid(False):
        break
    else:
        print("Invoice not paid yet")
        continue

refund = input("Refund payment? y/n: ").lower()
if refund == 'y':
    invoice.record_external_refund(
        {
        "method": "PAYPAL",
        "refund_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "amount": {
            "currency_code": "USD",
            "value": str(invoice.get_total_invoice_cost())
        }
    }
    )
    print("Refunded invoice in full.")
else:
    print("Did not refund.")
