import stripe
from decouple import config

stripe.api_key = config("STRIPE_SECRET_KEY_TEST")

EMAIL = "customer2@example.com"

# check if customer already exists
maybe_customer = stripe.Customer.list(email=EMAIL)
if maybe_customer.data:
    print("Customer already exists:")
    print(maybe_customer.data[0].id)
    exit()

# create customer
new_customer = stripe.Customer.create(email=EMAIL)
print("Created new customer:")
print(new_customer.id)