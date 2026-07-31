import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from .schemas import ResearchPlan, EvidenceGrade
# Import the tools and AI helpers from tools.py
from .tools import search_web, llm, planner, grader

class ResearchState(TypedDict, total=False):
    question: str
    depth: str
    plan: dict
    active_queries: list[str]
    sources: list[dict]
    evidence_score: int
    sufficient: bool
    missing_information: list[str]
    search_rounds: int
    max_search_rounds: int
    report: str

def create_plan(state: ResearchState) -> dict:
    print("\n[1] 🧠 LLM is creating the research plan...")
    prompt = f"""Create a focused research plan.
Question: {state['question']}
Depth: {state['depth']}
Return distinct search queries and a sensible report outline.
Do not answer the question yet."""
    plan = planner.invoke(prompt)
    return {
        "plan": plan.model_dump(),
        "active_queries": plan.search_queries,
        "search_rounds": 0,
        "sources": [],
    }

def research(state: ResearchState) -> dict:
    print(f"\n[2] 🌐 Searching the web for information (Round {state.get('search_rounds', 0) + 1})...")
    
    # Safe check in case search_web returns None
    new_sources = search_web(state["active_queries"]) or []
    
    # Safe list comprehension
    existing = {item["url"]: item for item in state.get("sources", []) if isinstance(item, dict) and "url" in item}
    
    existing.update({
        item["url"]: item 
        for item in new_sources 
        if isinstance(item, dict) and "url" in item
    })
    
    return {
        "sources": list(existing.values()),
        "search_rounds": state.get("search_rounds", 0) + 1,
    }

def grade_evidence(state: ResearchState) -> dict:
    print("\n[3] ⚖️ LLM is grading the search results...")
    evidence = "\n\n".join(
        f"SOURCE {i+1}: {s['title']}\nURL: {s['url']}\n{s['content']}"
        for i, s in enumerate(state["sources"])
    )
    grade = grader.invoke(f"""Judge whether this evidence can answer the question.
Question: {state['question']}
Evidence:\n{evidence}
Require relevant evidence from more than one source. If weak, provide improved queries.""")
    return {
        "sufficient": grade.sufficient,
        "evidence_score": grade.score,
        "missing_information": grade.missing_information,
        "active_queries": grade.refined_queries,
    }

def route_after_grade(state: ResearchState) -> str:
    # THIS IS THE CONDITION ROUTER
    current_rounds = state.get("search_rounds", 0)
    max_rounds = state.get("max_search_rounds", 2)

    if state.get("sufficient"):
        print("\n✅ Evidence is sufficient. Moving to report generation...")
        return "write_report"
        
    if current_rounds >= max_rounds:
        print(f"\n🛑 Reached maximum search rounds ({current_rounds}/{max_rounds}). Forcing report generation...")
        return "write_report"
        
    if not state.get("active_queries"):
        print("\n⚠️ No more queries to search. Forcing report generation...")
        return "write_report"
        
    print(f"\n🔄 Evidence is still weak. Looping back for search round {current_rounds + 1}...")
    return "research"

def write_report(state: ResearchState) -> dict:
    print("\n[4] 📝 LLM is writing the final report...")
    evidence = "\n\n".join(
        f"[{i+1}] {s['title']}\n{s['content']}\nURL: {s['url']}"
        for i, s in enumerate(state["sources"])
    )
    report = llm.invoke(f"""Write a {state['depth']} research report.
Question: {state['question']}
Planned sections: {state['plan']['report_sections']}
Evidence:\n{evidence}

Rules:
- Use only the supplied evidence.
- Cite claims using [1], [2], etc.
- Clearly state uncertainty or missing evidence.
- End with a short conclusion.
- Never create a citation number that is absent from the evidence.""")
    
    print("\n🎉 Report complete!")
    return {"report": report.content}

# Flowchart Setup
builder = StateGraph(ResearchState)
builder.add_node("create_plan", create_plan)
builder.add_node("research", research)
builder.add_node("grade_evidence", grade_evidence)
builder.add_node("write_report", write_report)

builder.add_edge(START, "create_plan")
builder.add_edge("create_plan", "research")
builder.add_edge("research", "grade_evidence")
builder.add_conditional_edges("grade_evidence", route_after_grade, {
    "research": "research",
    "write_report": "write_report",
})
builder.add_edge("write_report", END)

research_graph = builder.compile()
