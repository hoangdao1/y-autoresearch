from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ExecutionStrategy(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    TOPOLOGICAL = "topological"


class AgentSpec(BaseModel):
    id: str
    name: str
    role: str
    system_prompt: str
    model: str = "claude-opus-4-7"
    tool_ids: List[str] = Field(default_factory=list)
    context_ids: List[str] = Field(default_factory=list)


class ToolSpec(BaseModel):
    id: str
    name: str
    description: str
    parameters_schema: dict = Field(default_factory=dict)
    # Stub body is the body of the Python function (single expression or return stmt)
    stub_body: str = "return f'[stub] called with: {kwargs}'"


class ContextSpec(BaseModel):
    id: str
    name: str
    content: str
    weight: float = 1.0


class ConnectionSpec(BaseModel):
    from_id: str
    to_id: str
    condition: Optional[str] = None


class AppBlueprint(BaseModel):
    name: str
    description: str
    entry_agent_id: str
    agents: List[AgentSpec]
    tools: List[ToolSpec] = Field(default_factory=list)
    context: List[ContextSpec] = Field(default_factory=list)
    connections: List[ConnectionSpec] = Field(default_factory=list)
    execution_strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
    sample_query: str = "Hello, please help me."


class ValidationResult(BaseModel):
    score: float  # 0.0 – 1.0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.score >= 1.0


class IterationRecord(BaseModel):
    iteration: int
    score: float
    delta: float
    status: Literal["baseline", "keep", "discard", "no-op", "crash"]
    description: str
