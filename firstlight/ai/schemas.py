from pydantic import BaseModel


class BriefItem(BaseModel):
    ref: str
    headline: str
    why: str


class BriefSummary(BaseModel):
    title: str
    quiet_day: bool
    items: list[BriefItem]
