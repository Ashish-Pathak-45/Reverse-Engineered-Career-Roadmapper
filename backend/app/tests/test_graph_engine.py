import pytest
from app.services.graph_engine import (
    validate_roadmap_graph,
    extract_phase_index,
    compute_node_layout,
    can_complete_node,
    update_graph_states_on_change,
    calculate_progress
)

def test_validate_roadmap_graph_valid_dag():
    nodes = [
        {"node_id": "n1", "title": "Foundations", "phase": "Phase 1: Foundations", "status": "available"},
        {"node_id": "n2", "title": "Core Engineering", "phase": "Phase 2: Core Engineering", "status": "locked"},
        {"node_id": "n3", "title": "Advanced Topics", "phase": "Phase 3: Advanced Specialization", "status": "locked"}
    ]
    edges = [
        {"source_node_id": "n1", "target_node_id": "n2"},
        {"source_node_id": "n2", "target_node_id": "n3"}
    ]
    is_valid, msg = validate_roadmap_graph(nodes, edges)
    assert is_valid is True
    assert msg == "Valid DAG"

def test_validate_roadmap_graph_cycle_detection():
    # Construct a cycle: n1 -> n2 -> n3 -> n1
    nodes = [
        {"node_id": "n1", "title": "Step 1"},
        {"node_id": "n2", "title": "Step 2"},
        {"node_id": "n3", "title": "Step 3"}
    ]
    edges = [
        {"source_node_id": "n1", "target_node_id": "n2"},
        {"source_node_id": "n2", "target_node_id": "n3"},
        {"source_node_id": "n3", "target_node_id": "n1"}
    ]
    is_valid, msg = validate_roadmap_graph(nodes, edges)
    assert is_valid is False
    assert "Circular prerequisite dependency" in msg

def test_validate_roadmap_graph_self_loop():
    nodes = [{"node_id": "n1", "title": "Step 1"}]
    edges = [{"source_node_id": "n1", "target_node_id": "n1"}]
    is_valid, msg = validate_roadmap_graph(nodes, edges)
    assert is_valid is False
    assert "Self-referential loop" in msg

def test_validate_roadmap_graph_nonexistent_node():
    nodes = [{"node_id": "n1", "title": "Step 1"}]
    edges = [{"source_node_id": "n1", "target_node_id": "n99"}]
    is_valid, msg = validate_roadmap_graph(nodes, edges)
    assert is_valid is False
    assert "non-existent node" in msg

def test_validate_roadmap_graph_duplicate_id():
    nodes = [
        {"node_id": "n1", "title": "Step 1"},
        {"node_id": "n1", "title": "Duplicate"}
    ]
    edges = []
    is_valid, msg = validate_roadmap_graph(nodes, edges)
    assert is_valid is False
    assert "Duplicate node identifier" in msg

def test_extract_phase_index():
    assert extract_phase_index("Phase 1: Foundations") == 1
    assert extract_phase_index("Phase 2 - Core Systems") == 2
    assert extract_phase_index("Stage 3: Advanced") == 3
    assert extract_phase_index("4. Capstone Project") == 4
    assert extract_phase_index("Phase 5: Interview Prep") == 5
    assert extract_phase_index("Production Readiness") == 5
    assert extract_phase_index("Unknown Phase") == 99

def test_can_complete_node_and_unlock():
    nodes = [
        {"node_id": "n1", "title": "Step 1", "status": "available"},
        {"node_id": "n2", "title": "Step 2", "status": "locked"}
    ]
    edges = [{"source_node_id": "n1", "target_node_id": "n2"}]

    # n2 cannot be completed while n1 is not completed
    can_complete, unmet = can_complete_node("n2", nodes, edges)
    assert can_complete is False
    assert "Step 1" in unmet

    # Complete n1
    nodes[0]["status"] = "completed"
    can_complete_after, unmet_after = can_complete_node("n2", nodes, edges)
    assert can_complete_after is True
    assert len(unmet_after) == 0

    # update_graph_states_on_change should unlock n2 to available
    updated = update_graph_states_on_change(nodes, edges)
    assert updated[1]["status"] == "available"

def test_state_reversion_to_needs_revision():
    nodes = [
        {"node_id": "n1", "title": "Step 1", "status": "completed"},
        {"node_id": "n2", "title": "Step 2", "status": "available"}
    ]
    edges = [{"source_node_id": "n1", "target_node_id": "n2"}]

    # User or assessment flags n1 for revision
    nodes[0]["status"] = "needs_revision"
    updated = update_graph_states_on_change(nodes, edges)
    
    # n2 must now revert to locked because n1 is not completed
    assert updated[0]["status"] == "needs_revision"
    assert updated[1]["status"] == "locked"

def test_calculate_progress():
    nodes = [
        {"node_id": "n1", "status": "completed", "phase": "Phase 1: Foundations"},
        {"node_id": "n2", "status": "completed", "phase": "Phase 1: Foundations"},
        {"node_id": "n3", "status": "available", "phase": "Phase 2: Core Engineering"},
        {"node_id": "n4", "status": "locked", "phase": "Phase 3: Advanced"}
    ]
    pct, current_phase = calculate_progress(nodes)
    assert pct == 50.0
    assert current_phase == "Phase 2: Core Engineering"
