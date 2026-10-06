from typing import Literal
from pydantic import BaseModel, Field, model_validator

class SupportResponse(BaseModel):
    reply: str = Field(min_length=1, max_length=1200)
    action: str = Field(min_length=1, max_length=300)
    escalation_needed: bool

class JudgeResult(BaseModel):
    correctness: int = Field(ge=0, le=2)
    completeness: int = Field(ge=0, le=2)
    tone: int = Field(ge=0, le=2)
    non_fabrication: int = Field(ge=0, le=2)
    overall_score: int = Field(ge=0, le=8)
    passed: bool
    reason: str = Field(min_length=1, max_length=500)

    @model_validator(mode='after')
    def check_consistency(self):
        total = self.correctness + self.completeness + self.tone + self.non_fabrication
        expected_pass = total >= 6 and self.correctness >= 1 and self.non_fabrication >= 1
        if self.overall_score != total:
            raise ValueError(f'overall_score must equal dimension sum ({total})')
        if self.passed != expected_pass:
            raise ValueError('passed is inconsistent with rubric')
        return self

class PairwiseResult(BaseModel):
    winner: Literal['A','B','tie']
    reason: str = Field(min_length=1, max_length=300)
