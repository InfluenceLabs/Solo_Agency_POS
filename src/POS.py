import stripe
import boto3
import os
stripe.api_key = os.environ['STRIPE_SECRET_KEY']


class POS:
    def __init__(self, payload):
        self.stripe = stripe.StripeClient(stripe.api_key)
        self.till = boto3.client('dynamodb')
        self.payload = payload

    def create_checkout(self):
        return self.stripe.checkout.Session.create(
            customer_email= self.payload.customerEmail,
            success_url="",
            line_items = self.payload.products,
            mode = self.payload.mode,
            metadata = self.payload.metadata
        )

    def create_partner_checkout(self):
        return self.stripe.checkout.Session.create(
            customer_email= self.payload.customerEmail,
            success_url="",
            line_items = self.payload.products,
            mode = self.payload.mode,
            metadata = self.payload.metadata,
            on_behalf_of = self.payload.partnerId,
            transfer_data = {
                'destination': self.payload.partnerId
            }
        )

    def create_refund(self):
       return self.stripe.Refund.create(charge=self.payload.chargeId)

    def get_session(self):
        return self.stripe.checkout.Session.retrieve(self.payload.sessionId)