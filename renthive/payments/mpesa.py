import requests  # Import the requests library for making HTTP requests
import base64    # Import base64 for encoding credentials and passwords
import os        # Import os for interacting with the operating system (not used here)
from django.utils import timezone  # Import timezone utilities from Django
from django.conf import settings   # Import Django settings to access configuration variables

# Set the base URL for MPESA API depending on the environment (sandbox or production)
MPESA_BASE_URL = "https://sandbox.safaricom.co.ke" if settings.MPESA_ENV == "sandbox" else "https://api.safaricom.co.ke"

def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY  # Get the MPESA consumer key from settings
    consumer_secret = settings.MPESA_CONSUMER_SECRET  # Get the MPESA consumer secret from settings
    # Encode the consumer key and secret in base64 as required by MPESA API
    auth = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}  # Prepare the authorization header
    # Set the URL for requesting the access token
    url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, headers=headers)  # Make the GET request to obtain the token
    response.raise_for_status()  # Raise an error if the request failed
    return response.json()["access_token"]  # Return the access token from the response

def stk_push(phone_number, amount, account_reference, transaction_desc, callback_url):
    access_token = get_access_token()  # Get the access token for authorization
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")  # Generate the current timestamp in required format
    # Encode the password using shortcode, passkey, and timestamp as per MPESA requirements
    password = base64.b64encode(f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()).decode()
    headers = {
        "Authorization": f"Bearer {access_token}",  # Bearer token for authorization
        "Content-Type": "application/json"          # Specify content type as JSON
    }
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,  # Business shortcode from settings
        "Password": password,                           # Encoded password
        "Timestamp": timestamp,                         # Current timestamp
        "TransactionType": "CustomerPayBillOnline",     # Type of transaction
        "Amount": int(amount),                          # Amount to be transacted (as integer)
        "PartyA": phone_number,                         # Phone number sending the money
        "PartyB": settings.MPESA_SHORTCODE,             # Business shortcode receiving the money
        "PhoneNumber": phone_number,                    # Phone number of the customer
        "CallBackURL": callback_url,                    # URL to receive payment notifications
        "AccountReference": account_reference,          # Reference for the account/payment
        "TransactionDesc": transaction_desc,            # Description of the transaction
    }
    # Set the URL for the STK push request
    url = f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    # Make the POST request to initiate the STK push
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an error if the request failed
    return response.json()       # Return the JSON response from MPESA
