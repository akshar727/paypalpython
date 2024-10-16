Paypalpython
--------
An API Wrapper for the Paypal API written in Python


Key Features
--------
- Sandbox and live Paypal support
- Multiple configurations for any order or invoice
- Light syntax; most work done on the backend

Installing
--------
**Python 3.6 or higher is required**
Since this project is not on PyPI, you need to download the repository to your local computer, and from there you can use it within projects using:

.. code:: py

    # top-level import example
    import paypalpython



Quick Example
~~~~~~~~~~~~~

.. code:: py

  import paypalpython
  api = paypalpython.PaypalApi(client_id="client_id_here",client_secret="client_secret_here",mode="live")
  order = paypalpython.Order(payload = 
                    {  "intent": "CAPTURE",
  "purchase_units": [
    {
        "items": [
        {
          "name": "Basketball",
          "description": "Blue and White",
          "quantity": "1",
          "unit_amount": {
            "currency_code": "USD",
            "value": "3.50"
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
  print("Link for user: " + order.approval_link())
  # Wait for user to continue forward
  input()
  order.capture()
  print("Payment Successful!")



You can find more examples in the `examples directory <https://github.com/akshar727/paypalpython/blob/master/examples/>`_.

**NOTE:** It is not advised to leave your token directly in your code, as it allows anyone with it to create orders under your name. If you intend to make your code public you should store it securely using a .env file
