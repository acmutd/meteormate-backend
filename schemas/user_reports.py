# Created by Atharva Mishra | <unknown>
# ACM MeteorMate | All Rights Reserved

from pydantic import BaseModel


class UserReportCreate(BaseModel):
    reportee_uid: str
    description: str
    screenshots: list[str] | None = None
