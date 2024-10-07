import pytest  # noqa: F401
import base64
from app.services.signature_verification_service import SignatureVerificationService
import json
from datetime import datetime, timezone
from math import floor

class TestSignatureVerificationService:

    def test_init(self):
        secret_key = "whsec_" + base64.b64encode(b'secret').decode('utf-8')
        obj = SignatureVerificationService(secret_key)
        assert obj._secret_key == b'secret'

    def test_valid_signature_with_correct_headers_and_data(self):
        service = SignatureVerificationService('1234567890123456')
        msg_id = "test-msg-id"
        data = json.dumps({"key": "value"})
        timestamp = datetime.now(tz=timezone.utc)
        signature = service.sign(msg_id=msg_id, timestamp=timestamp, data=data)

        headers = {
            "svix-id": msg_id,
            "svix-signature": signature,
            "svix-timestamp": str(floor(timestamp.timestamp()))
        }

        result = service.verify(data, headers)
        assert result == json.loads(data)
