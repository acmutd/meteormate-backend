# Created by Atharva Mishra | 9/16/2026
# ACM MeteorMate | All Rights Reserved

from typing import TypedDict

from pydantic import BaseModel


class Notifications(TypedDict):
    id: int
    created_at: str
    title: str
    description: str


class NotificationsGetResponse(BaseModel):
    data: list[Notifications]

    class Config:
        from_attributes = True

class NotificationsMarkSeenBody(BaseModel):
    notification_ids: list[int]

    class Config:
        from_attributes = True