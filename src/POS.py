import stripe
import boto3
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class POSPayload:
    customerEmail: Optional[str] = None
    products: List[Dict[str, Any]] = field(default_factory=list)
    mode: str = "payment"
    metadata: Dict[str, Any] = field(default_factory=dict)
    partnerId: Optional[str] = None
    chargeId: Optional[str] = None
    sessionId: Optional[str] = None
    tillId: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

class StripeService:
    def __init__(self, api_key: str):
        self.client = stripe.StripeClient(api_key)

    def create_checkout_session(self, payload: POSPayload, partner_id: Optional[str] = None):
        params = {
            "customer_email": payload.customerEmail,
            "success_url": "",
            "line_items": payload.products,
            "mode": payload.mode,
            "metadata": payload.metadata,
        }
        if partner_id:
            params.update({
                "on_behalf_of": partner_id,
                "transfer_data": {"destination": partner_id}
            })
        return self.client.checkout.Session.create(**params)

    def create_refund(self, charge_id: str):
        return self.client.refunds.create(charge=charge_id)

    def get_session(self, session_id: str):
        return self.client.checkout.Session.retrieve(session_id)

class TillService:
    def __init__(self, table_name: str = 'TillBalance'):
        self.client = boto3.client('dynamodb')
        self.table_name = table_name

    def get_balance(self, till_id: str):
        return self.client.get_item(
            TableName=self.table_name,
            Key={'tillId': {'S': till_id}}
        )

class NotificationService:
    def __init__(self, topic_arn: str):
        self.client = boto3.client('sns')
        self.topic_arn = topic_arn

    def notify_success(self, customer_email: str):
        return self.client.publish(
            TopicArn=self.topic_arn,
            Message=f"Successful payment for {customer_email}",
            Subject="POS Sales"
        )

class POS:
    def __init__(self, payload: Any):
        # Handle both dict and object for backward compatibility or flexibility
        if isinstance(payload, dict):
            self.payload = POSPayload.from_dict(payload)
        else:
            self.payload = payload

        self.stripe_service = StripeService(os.environ.get('STRIPE_SECRET_KEY'))
        self.till_service = TillService()
        self.notification_service = NotificationService(os.environ.get('SNS_TOPIC_ARN'))

    def create_checkout(self):
        return self.stripe_service.create_checkout_session(self.payload)

    def create_partner_checkout(self):
        return self.stripe_service.create_checkout_session(self.payload, partner_id=self.payload.partnerId)

    def create_refund(self):
        return self.stripe_service.create_refund(self.payload.chargeId)

    def get_session(self):
        return self.stripe_service.get_session(self.payload.sessionId)

    def get_till_balance(self):
        return self.till_service.get_balance(self.payload.tillId)

    def successful_payment(self):
        return self.notification_service.notify_success(self.payload.customerEmail)