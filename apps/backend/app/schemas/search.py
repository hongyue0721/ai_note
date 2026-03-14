from pydantic import BaseModel


class SearchItem(BaseModel):
    type: str
    id: str
    title: str
    snippet: str
    subject: str
    category: str
    parse_status: str
