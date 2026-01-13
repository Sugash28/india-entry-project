from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
from pydantic import validator, MySQLDsn

class Settings(BaseSettings):
    PROJECT_NAME: str = "India Entry Project"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "changethis"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "280124"
    MYSQL_DB: str = "Main"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_TENANT_ID: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return str(MySQLDsn.build(
            scheme="mysql+pymysql",
            username=values.get("MYSQL_USER"),
            password=values.get("MYSQL_PASSWORD"),
            host=values.get("MYSQL_SERVER"),
            path=f"/{values.get('MYSQL_DB') or ''}",
        ))

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
