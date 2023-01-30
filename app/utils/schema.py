from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class NodeBase(BaseModel):
    node_id: int
    labels: list


class ProjectNode(NodeBase):
    properties: Optional[dict] = None


class ProjectNodeList(BaseModel):
    nodes: List[ProjectNode]


class ProjectNodeProperties(BaseModel):
    name: str
    description: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
