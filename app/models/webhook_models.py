from pydantic import BaseModel, Field
from typing import Optional

class ResendEvent(BaseModel):
    type: str
    description: Optional[str] = "No description"
    data: dict
    created_at: str

    class Config:
        schema_extra = {
            "example": {
                "type": "email.sent",
                "data": {"from": "example@example.com", "subject": "Sent Email"},
                "created_at": "2024-10-01T12:34:56Z"
            }
        }

class PrefectEvent(BaseModel):
    flow_id: str = Field(..., alias="id")
    state: dict
    timestamp: str

    class Config:
        schema_extra = {
            "example": {
                "id": "flow_abcdef123456",
                "state": {
                    "message": "Flow run completed successfully",
                    "state_name": "Completed"
                },
                "timestamp": "2024-10-02T15:20:30Z"
            }
        }
