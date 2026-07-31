from src.graph import route_after_grade

def test_writes_when_evidence_is_sufficient():
    state = {"sufficient": True, "search_rounds": 1, "max_search_rounds": 2}
    assert route_after_grade(state) == "write_report"

def test_researches_again_when_evidence_is_weak():
    state = {
        "sufficient": False,
        "search_rounds": 1,
        "max_search_rounds": 2,
        "active_queries": ["improved query"],
    }
    assert route_after_grade(state) == "research"

def test_stops_at_search_limit():
    state = {
        "sufficient": False,
        "search_rounds": 2,
        "max_search_rounds": 2,
        "active_queries": ["another query"],
    }
    assert route_after_grade(state) == "write_report"
