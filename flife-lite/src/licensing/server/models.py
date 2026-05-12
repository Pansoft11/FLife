from typing import Literal

from pydantic import BaseModel, EmailStr, Field


LicenseType = Literal["trial", "monthly", "yearly", "perpetual", "enterprise"]


class ActivationRequest(BaseModel):
    email: EmailStr
    license_key: str = Field(min_length=8)
    machine_hash: str = Field(min_length=32)


class ValidationRequest(BaseModel):
    token: str
    machine_hash: str = Field(min_length=32)


class DeactivationRequest(BaseModel):
    token: str
    machine_hash: str = Field(min_length=32)


class RevocationRequest(BaseModel):
    license_key: str = Field(min_length=8)
    reason: str = "Admin revocation"


class MachineTransferRequest(BaseModel):
    license_key: str = Field(min_length=8)
    from_machine_hash: str = Field(min_length=32)
    to_machine_hash: str = Field(min_length=32)


class LicenseResponse(BaseModel):
    state: Literal["active", "trial", "offline", "expired", "unactivated", "deactivated"]
    type: LicenseType
    email: str
    token: str | None = None
    days_remaining: int
    offline_until: str
    max_activations: int = 1
