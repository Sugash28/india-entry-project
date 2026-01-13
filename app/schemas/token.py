from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class GoogleToken(BaseModel):
    token: str

class MicrosoftToken(BaseModel):
    token: str
