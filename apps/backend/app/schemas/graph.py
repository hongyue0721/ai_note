from pydantic import BaseModel


class GraphNode(BaseModel):
    name: str
    weight: float


class GraphOverviewData(BaseModel):
    nodes: list[GraphNode]
    total_problems: int
    total_notes: int


class WeakTagItem(BaseModel):
    name: str
    score: float
