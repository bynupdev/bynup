import requests
from django.conf import settings
from django.core.exceptions import ValidationError

class AgentaOSService:
    BASE_URL = "https://api.agentaos.ai/api/v1"

    def __init__(self):
        self.api_key = settings.AGENTAOS_API_KEY
        if not self.api_key:
            raise ValidationError("AgentaOS API key not configured")

    def _headers(self):
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def create_subscription_checkout(self, plan, user, billing_period, success_url, cancel_url, webhook_url):
        """
        Creates a checkout session for a subscription.
        AgentaOS requires a payment link (product) for subscriptions.
        """
        # Note: Ideally, you create the product/payment link once in the AgentaOS dashboard
        # and store its ID (linkId). For this example, we assume you create it on the fly
        # or have stored the linkId per plan.
        
        amount = plan.price_monthly if billing_period == 'monthly' else plan.price_yearly
        
        payload = {
            "amount": float(amount),
            "currency": "USD",  # AgentaOS supports EUR, USD, etc. [citation:13]
            "description": f"{plan.name} Plan - {billing_period}",
            "successUrl": success_url,
            "cancelUrl": cancel_url,
            "webhookUrl": webhook_url,
            "buyerEmail": user.email,
            # Metadata is crucial to link back to your Django user
            "metadata": {
                "user_id": user.id,
                "plan_tier": plan.tier,
                "billing_period": billing_period
            }
        }

        # If you have a pre-created payment link for subscriptions:
        # payload["linkId"] = "your_link_id"
        
        response = requests.post(
            f"{self.BASE_URL}/gateway/sessions",
            json=payload,
            headers=self._headers(),
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise ValidationError(f"AgentaOS error: {response.text}")