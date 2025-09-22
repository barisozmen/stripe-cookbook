import webbrowser
import stripe
from decouple import config
stripe.api_key = config("STRIPE_SECRET_KEY_TEST")

CUSTOMER_ID = "cus_T5rm1AweQushbC"

customer_session = stripe.CustomerSession.create(
  customer=CUSTOMER_ID,
  components={"pricing_table": {"enabled": True}},
)

pricing_table_html = f"""
<html>
<head>
</head>
<body>
    <h1>Pricing Table</h1>
    
    <script async src="https://js.stripe.com/v3/pricing-table.js"></script>
    <stripe-pricing-table 
        pricing-table-id="prctbl_1S9mHcAMz8gMMU0rzQqJyWaD" 
        publishable-key="pk_test_51S9fnqAMz8gMMU0rWFhWbHBN7mcbnjXZIUKf8ftkbamVBlRgj2BgkcpihORBeOCG4XgNRRRmwHpHf2ZwVcd4YdAC003EIgjDaK"
        customer-session-client-secret="{customer_session.client_secret}"
    >
    </stripe-pricing-table>
</body>
</html>
"""
PRICING_TABLE_HTML_PATH = "pricing_table.html"

# save html to file
with open(PRICING_TABLE_HTML_PATH, "w") as f:
    f.write(pricing_table_html)

# Open in browser
webbrowser.open(PRICING_TABLE_HTML_PATH)