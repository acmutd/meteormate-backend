from typing import Optional

from pydantic import BaseModel



class UserReportCreate(BaseModel):
    reportee_uid: str
    description: str
    screenshots: Optional[list[str]] = None
