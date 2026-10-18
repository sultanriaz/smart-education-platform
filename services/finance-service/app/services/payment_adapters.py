from __future__ import annotations

import hashlib
import hmac
import secrets
import time
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.core.config import settings
from app.core.errors import FinanceDomainError
from app.domain.models import PaymentIntent


class BasePaymentAdapter(ABC):
    @abstractmethod
    def generate_checkout_payload(self, intent: PaymentIntent) -> dict[str, Any]:
        """Generate checkout / simulator metadata for frontend and callback simulation."""
        pass

    @abstractmethod
    def verify_callback(self, payload: dict[str, Any], signature: str, timestamp: float) -> bool:
        """Verify callback authenticity, timing freshness, and payload signature."""
        pass


class JazzCashAdapter(BasePaymentAdapter):
    PROVIDER_NAME = "JAZZ_CASH"

    def __init__(self, secret_key: str | None = None):
        self.secret_key = secret_key or settings.PAYMENT_WEBHOOK_SECRET

    def _sign_payload(self, data: dict[str, Any]) -> str:
        # Build canonical query string of sorted keys excluding signature
        sorted_keys = sorted(k for k in data.keys() if k != "signature")
        canonical = "&".join(f"{k}={data[k]}" for k in sorted_keys)
        return hmac.new(
            self.secret_key.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def generate_checkout_payload(self, intent: PaymentIntent) -> dict[str, Any]:
        ts = int(time.time())
        ref_id = f"JC-{intent.id.hex[:10].upper()}"
        payload = {
            "pp_TxnRefNo": ref_id,
            "pp_Amount": str(intent.amount),
            "pp_TxnCurrency": intent.currency,
            "pp_TxnDateTime": str(ts),
            "pp_BillReference": str(intent.invoice_id),
            "pp_MerchantID": "SMARTEDU_JC_DEMO",
            "provider": self.PROVIDER_NAME,
        }
        payload["signature"] = self._sign_payload(payload)
        return payload

    def verify_callback(self, payload: dict[str, Any], signature: str, timestamp: float) -> bool:
        # 1. Freshness check: reject callbacks older than 300 seconds
        now = time.time()
        if abs(now - timestamp) > 300:
            return False

        # 2. Strict HMAC verification
        expected = self._sign_payload(payload)
        return secrets.compare_digest(expected, signature)


class EasypaisaAdapter(BasePaymentAdapter):
    PROVIDER_NAME = "EASYPAISA"

    def __init__(self, secret_key: str | None = None):
        self.secret_key = secret_key or settings.PAYMENT_WEBHOOK_SECRET

    def _sign_payload(self, data: dict[str, Any]) -> str:
        sorted_keys = sorted(k for k in data.keys() if k != "signature")
        canonical = "&".join(f"{k}={data[k]}" for k in sorted_keys)
        return hmac.new(
            self.secret_key.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def generate_checkout_payload(self, intent: PaymentIntent) -> dict[str, Any]:
        ts = int(time.time())
        ref_id = f"EP-{intent.id.hex[:10].upper()}"
        payload = {
            "orderId": ref_id,
            "storeId": "SMARTEDU_EP_DEMO",
            "transactionAmount": str(intent.amount),
            "transactionCurrency": intent.currency,
            "timestamp": str(ts),
            "provider": self.PROVIDER_NAME,
        }
        payload["signature"] = self._sign_payload(payload)
        return payload

    def verify_callback(self, payload: dict[str, Any], signature: str, timestamp: float) -> bool:
        now = time.time()
        if abs(now - timestamp) > 300:
            return False
        expected = self._sign_payload(payload)
        return secrets.compare_digest(expected, signature)


class BankTransferAdapter(BasePaymentAdapter):
    PROVIDER_NAME = "BANK_TRANSFER"

    def generate_checkout_payload(self, intent: PaymentIntent) -> dict[str, Any]:
        # Generate 16-digit 1Bill / Kuickpay consumer number
        consumer_number = f"9988{intent.id.int % 10**12:012d}"
        return {
            "consumer_number": consumer_number,
            "bank_name": "Habib Bank Limited / 1Bill",
            "account_title": "SmartEdu Demo University Collection A/C",
            "account_iban": "PK36HABB0001234567890123",
            "amount": str(intent.amount),
            "currency": intent.currency,
            "provider": self.PROVIDER_NAME,
            "voucher_expires_at": intent.expires_at.isoformat(),
        }

    def verify_callback(self, payload: dict[str, Any], signature: str, timestamp: float) -> bool:
        # Bank transfer simulator uses bearer internal authorization
        return True


class CashAdapter(BasePaymentAdapter):
    PROVIDER_NAME = "CASH"

    def generate_checkout_payload(self, intent: PaymentIntent) -> dict[str, Any]:
        return {
            "payment_code": f"CASH-{intent.id.hex[:8].upper()}",
            "campus_counter": "Finance Office Window 1",
            "amount": str(intent.amount),
            "currency": intent.currency,
            "provider": self.PROVIDER_NAME,
        }

    def verify_callback(self, payload: dict[str, Any], signature: str, timestamp: float) -> bool:
        return True


ADAPTERS: dict[str, BasePaymentAdapter] = {
    "JAZZ_CASH": JazzCashAdapter(),
    "EASYPAISA": EasypaisaAdapter(),
    "BANK_TRANSFER": BankTransferAdapter(),
    "CASH": CashAdapter(),
}


def get_adapter(provider: str) -> BasePaymentAdapter:
    normalized = provider.upper()
    if normalized not in ADAPTERS:
        raise FinanceDomainError(f"Unsupported payment provider: {provider}")
    return ADAPTERS[normalized]

