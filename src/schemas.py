from pydantic import BaseModel, Field, HttpUrl

class ResearchRequest(BaseModel):
    question: str = Field(min_length=10, max_length=1000)
    depth: str = Field(default="brief", pattern="^(brief|standard|deep)$")

class ResearchPlan(BaseModel):
    objective: str
    search_queries: list[str] = Field(min_length=2, max_length=5)
    report_sections: list[str] = Field(min_length=2, max_length=6)

class EvidenceGrade(BaseModel):
    sufficient: bool
    score: int = Field(ge=0, le=100)
    missing_information: list[str] = []
    refined_queries: list[str] = []

class Source(BaseModel):
    title: str
    url: HttpUrl
    content: str

class ResearchResponse(BaseModel):
    question: str
    report: str
    sources: list[Source]
    search_rounds: int
    evidence_score: int
