import stripe
from decouple import config

stripe.api_key = config("STRIPE_SECRET_KEY_TEST")

customer = stripe.Customer.create(email="customer@example.com")
print(customer.id)