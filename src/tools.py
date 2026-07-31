import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from .schemas import ResearchPlan, EvidenceGrade

load_dotenv(override=True)

# 1. Aggressively strip away any hidden Windows characters or spaces
raw_key = os.getenv("OPENROUTER_API_KEY", "")
clean_key = raw_key.strip().replace("\r", "").replace("\n", "")

if clean_key:
    print(f"\n✅ SUCCESS: Clean Key loaded! Starts with: {clean_key[:10]}...\n")
else:
    print("\n❌ ERROR: Key is missing!\n")

# 2. Use the stable ChatOpenAI wrapper with OpenRouter's required headers
llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL_ID"),
    api_key=clean_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
    request_timeout=30.0,
    max_retries=2,
    default_headers={
        "HTTP-Referer": "http://localhost:8000", # OpenRouter requires this
        "X-Title": "AI Research Assistant",      # OpenRouter requires this
    }
)

# Structured output helpers
planner = llm.with_structured_output(ResearchPlan)
grader = llm.with_structured_output(EvidenceGrade)

# Tavily search tool instance
search_tool = TavilySearch(
    max_results=5,
    topic="general",
    include_raw_content=False,
)

def search_web(queries: list[str]) -> list[dict]:
    collected: dict[str, dict] = {}
    for query in queries:
        result = search_tool.invoke({"query": query})
        items = result.get("results", result) if isinstance(result, dict) else result
        for item in items:
            url = item.get("url")
            if url:
                collected[url] = {
                    "title": item.get("title", "Untitled source"),
                    "url": url,
                    "content": item.get("content", ""),
                }
    return list(collected.values())