# Created by Atharva Mishra | 9/16/2026
# ACM MeteorMate | All Rights Reserved

from datetime import datetime

from pydantic import BaseModel


class Notifications(BaseModel):
    id: int
    created_at: datetime
    title: str
    description: str


class NotificationsGetResponse(BaseModel):
    data: list[Notifications]

    class Config:
        from_attributes = True


class NotificationsMarkSeenBody(BaseModel):
    notification_ids: list[int]
