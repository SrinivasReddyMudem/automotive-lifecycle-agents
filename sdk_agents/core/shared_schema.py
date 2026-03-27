"""
Shared Pydantic sub-models reused across multiple agents.
Import from here to keep schemas consistent and avoid duplication.
"""

from pydantic import BaseModel, Field
from typing import Literal


class ProbableCause(BaseModel):
    rank: Literal["HIGH", "MEDIUM", "LOW"]
    description: str = Field(description="What is causing the fault and why")
    test: str = Field(description="Specific measurement to perform — tool, signal, value")
    pass_criteria: str = Field(description="Exact value/condition that rules this cause out")
    fail_criteria: str = Field(description="Exact value/condition that confirms this cause")


class NarrowingQuestion(BaseModel):
    question: str
    yes_consequence: str = Field(description="What yes means for the diagnosis")
    no_consequence: str = Field(description="What no means for the diagnosis")


class SelfEvaluationLine(BaseModel):
    item: str = Field(description="What was checked")
    result: Literal["PASS", "FAIL"]
    evidence: str = Field(description="Specific text from this response that proves the result")


class DebugStep(BaseModel):
    step_number: int
    tool: str
    action: str = Field(description="Exactly what to do with the tool")
    expected_output: str = Field(description="What you see in the tool if this is the cause")
