
def calculate_paypal_invoice_fee(cost: float) -> float:
    return (cost * 0.0349) + 0.49

def percent_of(value:float, per:float):
    return (per/100) * value