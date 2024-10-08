import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from math import floor
from typing import Any, Dict, Union


class SignatureVerificationService:  # TODO: abstract this so we have 2 final services (one for webhooks that use svix signature validation, and another that only validates a Header API KEY)
    def __init__(self, secret_key: str):
        try:
            if isinstance(secret_key, str):
                if secret_key.startswith("whsec_"):
                    secret_key = secret_key[len("whsec_") :]
                self._secret_key = base64.b64decode(secret_key)
        except Exception as e:
            raise ValueError(f"Error decoding the value {secret_key},\nException: {e}")

        if isinstance(secret_key, bytes):
            self._secret_key = secret_key

        if not self._secret_key:
            raise ValueError("Cannot initialize with an invalid secret_key")

    def verify(self, data: Union[bytes, str], headers: Dict[str, str]) -> Any:
        data = data if isinstance(data, str) else data.decode()
        headers = {k.lower(): v for (k, v) in headers.items()}
        msg_id = headers.get("svix-id")
        msg_signature = headers.get("svix-signature")
        msg_timestamp = headers.get("svix-timestamp")
        if not (msg_id and msg_timestamp and msg_signature):
            msg_id = headers.get("webhook-id")
            msg_signature = headers.get("webhook-signature")
            msg_timestamp = headers.get("webhook-timestamp")
            if not (msg_id and msg_timestamp and msg_signature):
                raise ValueError("Missing required headers")

        timestamp = self.__verify_timestamp(msg_timestamp)

        expected_sig = base64.b64decode(
            self.sign(msg_id=msg_id, timestamp=timestamp, data=data).split(",")[1]
        )
        passed_sigs = msg_signature.split(" ")
        for versioned_sig in passed_sigs:
            (version, signature) = versioned_sig.split(",")
            if version != "v1":
                continue
            sig_bytes = base64.b64decode(signature)
            if hmac.compare_digest(expected_sig, sig_bytes):
                return json.loads(data)

        raise ValueError("No matching signature found")

    def sign(self, msg_id: str, timestamp: datetime, data: str) -> str:
        timestamp_str = str(floor(timestamp.replace(tzinfo=timezone.utc).timestamp()))
        to_sign = f"{msg_id}.{timestamp_str}.{data}".encode()
        signature = self.hmac_data(self._secret_key, to_sign)
        return f"v1,{base64.b64encode(signature).decode('utf-8')}"

    def __verify_timestamp(self, timestamp_header: str) -> datetime:
        webhook_tolerance = timedelta(minutes=5)
        now = datetime.now(tz=timezone.utc)
        try:
            timestamp = datetime.fromtimestamp(float(timestamp_header), tz=timezone.utc)
        except Exception:
            raise ValueError("Invalid Signature Headers")

        if timestamp < (now - webhook_tolerance):
            raise ValueError("Message timestamp too old")
        if timestamp > (now + webhook_tolerance):
            raise ValueError("Message timestamp too new")
        return timestamp

    def hmac_data(self, key: bytes, data: bytes) -> bytes:
        return hmac.new(key, data, hashlib.sha256).digest()
