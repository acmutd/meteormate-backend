from pydantic import BaseModel, Field



class UserReportCreate(BaseModel):
    reportee_uid: str
    description: str
    screenshots: list[str] = Field(default_factory=list)
