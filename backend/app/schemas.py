from pydantic import BaseModel, Field
from typing import Optional, Any
class AccountIn(BaseModel):
    phone: str
    session_filename: str
    proxy_id: Optional[int] = None
class AccountOut(BaseModel):
    id: int
    phone: str
    username: Optional[str] = None
    premium: bool = False
    status: str
    next_allowed_at: Optional[str] = None
    proxy_id: Optional[int] = None
    last_error: Optional[str] = None
    class Config: from_attributes = True
class ProxyIn(BaseModel):
    kind: str
    host: str
    port: int
    login: Optional[str] = None
    password: Optional[str] = None
class ProxyOut(BaseModel):
    id: int
    kind: str
    host: str
    port: int
    login: Optional[str] = None
    class Config: from_attributes = True
class JobCreate(BaseModel):
    account_id: int
    kind: str = Field(description="inviter_optin|parser_owned|cloner_owned|warmup")
    payload_json: Any
class JobOut(BaseModel):
    id: int
    account_id: int
    kind: str
    state: str
    last_error: Optional[str] = None
    class Config: from_attributes = True
