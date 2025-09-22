import stripe
import time
from decouple import config

stripe.api_key = config("STRIPE_SECRET_KEY_TEST")

EMAIL = "customer2@example.com"

def YEARLY_PRICE_WITH_DISCOUNT(monthly_price, discount=0.3): return monthly_price * 12 * (1 - discount)

PRODUCT = {
    "name": "MyService",
    "description": "Subscription service with exclusive tiers: Basic / Pro / Ultimate",
    "currency": "usd",

    "tiers": [
        {
            "name": "basic",
            "price": {
                "monthly": 10.00,
                "yearly": YEARLY_PRICE_WITH_DISCOUNT(10.00),
            }
        },
        {
            "name": "pro",
            "price": {
                "monthly": 20.00,       
                "yearly": YEARLY_PRICE_WITH_DISCOUNT(20.00),
            }
        },
        {
            "name": "ultimate",
            "price": {
                "monthly": 100.00,
                "yearly": YEARLY_PRICE_WITH_DISCOUNT(100.00),
            }
        }
    ]
}

def create_product_if_not_exists(name, description):
    # check if product already exists
    maybe_product = stripe.Product.list(active=True)
    for product in maybe_product.data:
        if product.name == name:
            print("Product already exists:")
            print(product.id)
            return product

    # create product with all details
    new_product = stripe.Product.create(
        name=name,
        description=description,
        type='service',
    )
    print("Created new product:")
    print(new_product.id)
    return new_product


def create_price_if_not_exists(product_id, amount=10, currency='usd',interval='month', nickname=None):
    # check if price already exists
    maybe_price = stripe.Price.list(product=product_id, recurring={'interval': interval})
    for price in maybe_price.data:
        if price.unit_amount == int(amount * 100):
            print("Price already exists:")
            print(price.id)
            return price
    
    new_price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100), # Stripe requires the amount in cents
        currency='usd',
        recurring={'interval': interval}, # can be 'month' or 'year',
        nickname=nickname,
    )
    
    print("Created new price:")
    print(new_price.id)
    return new_price


def create_customer_if_not_exists(email):
    # check if customer already exists
    resp = stripe.Customer.list(email=email)
    maybe_customers = resp.data
    if maybe_customers:
        
        if len(maybe_customers) > 1:
            print(f"WARNING! Multiple customers exists for email: {email}")
            print(f"Customer IDs: {[customer.id for customer in maybe_customers]}")
            print("\nReturning the first customer:")
            return maybe_customers[0]
        
        print("Customer already exists:")
        print(maybe_customers[0].id)
        return maybe_customers[0]

    # create customer
    new_customer = stripe.Customer.create(email=email)
    print("Created new customer:")
    print(new_customer.id)
    return new_customer


def start_checkout_session(customer_id, price_id):
    session = stripe.checkout.Session.create(
        customer=customer_id,
        line_items=[{'price': price_id, 'quantity': 1}],
        mode='subscription',
        success_url='https://example.com/success',
        cancel_url='https://example.com/cancel',
        metadata={
            'user_id': '123',
            'created_via': 'url' 
        },
    )
    print("Created new checkout session:")
    print(session.url)
    return session

def determine_customer_subscription(customer_id):
    all_subs = stripe.Subscription.list(customer=customer_id).data
    now = int(time.time())
    valid_subs = [s for s in all_subs if s.status == 'active' or (s.status == 'canceled' and s.current_period_end > now)]
    
    if not valid_subs:
        print("No valid subscription found")
        return None
    
    if len(valid_subs) > 1:
        print(f"WARNING! Multiple valid subscriptions found for customer: {customer_id}")
        print(f"Subscription IDs: {[sub.id for sub in valid_subs]}")
        print("\nReturning the first subscription")
        
    return valid_subs[0]


if __name__ == "__main__":
    prefix = '\n' + "-"*50 + '\n'
    
    input(prefix+"Press Enter to create product and prices")
    product = create_product_if_not_exists(
        PRODUCT['name'], 
        PRODUCT['description'], 
    )
    for tier in PRODUCT['tiers']:
        price_monthly = create_price_if_not_exists(
            product.id, 
            tier['price']['monthly'],
            PRODUCT['currency'], 
            'month',
            nickname=f"{tier['name']} monthly",
        )
        price_yearly = create_price_if_not_exists(
            product.id, 
            tier['price']['yearly'],
            PRODUCT['currency'],
            'year',
            nickname=f"{tier['name']} yearly",
        )
    
    input(prefix+"Press Enter to create customer")
    customer = create_customer_if_not_exists(EMAIL)
    
    input(prefix+"Press Enter to create checkout or portal session")
    if customer_has_subscription(customer.id):
        session = start_portal_session(customer.id)
    else:
        session = start_checkout_session(customer.id, price_monthly.id)
    
    input(prefix+"Press Enter to check customer subscription")
    subscription = determine_customer_subscription(customer.id)
    print(subscription)