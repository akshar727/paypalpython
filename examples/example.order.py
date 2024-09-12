import datetime
import paypalpython


api = paypalpython.PaypalApi(client_id="client_id_here",client_secret="client_secret_here",mode="sandbox")



"""
/
/   ORDER CREATION
/
"""

while True:

  order = paypalpython.Order(payload = 
                      {  "intent": "CAPTURE",
    "purchase_units": [
      {
          "items": [
          {
            "name": "T-Shirt",
            "description": "Green XL",
            "quantity": "1",
            "unit_amount": {
              "currency_code": "USD",
              "value": "10.00"
            }
          }
        ],
        "amount": {
          "currency_code": "USD",
          "value": "10.00",
          "breakdown": {
            "item_total": {
              "currency_code": "USD",
              "value": "10.00"
            }
          }
        }
      },
    ],
    "application_context": {
      "return_url": "https://example.com/return",
      "cancel_url": "https://example.com/cancel"
    }
  })

  order.create()
  print(f"Payment Approval Link: {order.approval_link()}")
  while True:
    input("Press Enter to continue when user has approved the order.")
    if order.is_approved(False):
        print("Order approved! Capturing order...")
        break
    else:
        print("Order not approved yet.")
  order.capture()
  print("Order captured!")
  refund = input("Refund? (y/n): ")
  if refund == "y":
    order.refund("Did not want to buy.")
    print("Order refunded!")
  else:
      print("Order was not refunded.")
  new_order = input("New order? (y/n): ")
  if new_order == "y":
      continue
  else:
    exit(0)
