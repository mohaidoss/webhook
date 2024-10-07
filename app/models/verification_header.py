from pydantic import BaseModel


class VerificationHeader(BaseModel):
    svix_id: str
    svix_timestamp: int
    svix_signature: str
