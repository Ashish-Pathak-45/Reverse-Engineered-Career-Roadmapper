from typing import List, Dict, Set, Tuple, Any
import networkx as nx
import re

def build_graph(nodes: List[Any], edges: List[Any]) -> nx.DiGraph:
    """Builds a NetworkX directed graph from nodes and edges."""
    G = nx.DiGraph()
    for n in nodes:
        node_id = n.get("node_id") if isinstance(n, dict) else getattr(n, "node_id", None)
        if node_id:
            G.add_node(node_id, data=n)
    for e in edges:
        s = e.get("source_node_id") if isinstance(e, dict) else getattr(e, "source_node_id", None)
        t = e.get("target_node_id") if isinstance(e, dict) else getattr(e, "target_node_id", None)
        if s and t and s != t:
            G.add_edge(s, t)
    return G

def check_cycles(G: nx.DiGraph) -> bool:
    """Returns True if there is a cycle in the graph."""
    return not nx.is_directed_acyclic_graph(G)

def validate_roadmap_graph(nodes: List[Any], edges: List[Any]) -> Tuple[bool, str]:
    """
    Validates that:
    1. Nodes are non-empty and have valid unique identifiers.
    2. Edge source and targets exist in nodes.
    3. No self-loops.
    4. The graph is strictly acyclic (no circular dependencies).
    """
    if not nodes:
        return False, "Roadmap contains no milestone nodes."

    node_ids = set()
    for n in nodes:
        nid = n.get("node_id") if isinstance(n, dict) else getattr(n, "node_id", None)
        if not nid:
            return False, "Encountered a node without a valid node_id."
        if nid in node_ids:
            return False, f"Duplicate node identifier detected: {nid}"
        node_ids.add(nid)

    for e in edges:
        s = e.get("source_node_id") if isinstance(e, dict) else getattr(e, "source_node_id", None)
        t = e.get("target_node_id") if isinstance(e, dict) else getattr(e, "target_node_id", None)
        if not s or not t:
            return False, "Edge contains missing source or target node ID."
        if s == t:
            return False, f"Self-referential loop detected on node: {s}"
        if s not in node_ids or t not in node_ids:
            return False, f"Edge connects to non-existent node: {s} -> {t}"

    G = build_graph(nodes, edges)
    if not nx.is_directed_acyclic_graph(G):
        try:
            cycle = nx.find_cycle(G, orientation="original")
            cycle_str = " -> ".join([f"{u}" for u, v, _ in cycle])
            return False, f"Circular prerequisite dependency detected: {cycle_str}"
        except Exception:
            return False, "Circular prerequisite dependency detected in graph."

    return True, "Valid DAG"

def extract_phase_index(phase_name: str) -> int:
    """
    Extracts numerical ordering index from various phase naming conventions:
    'Phase 1: Foundations', 'Phase 2', 'Stage 3', '1. Foundations', etc.
    """
    if not phase_name:
        return 99
    phase_lower = str(phase_name).lower()
    
    # Check for digit patterns
    match = re.search(r'(?:phase|stage|step|level|part)\s*(\d+)', phase_lower)
    if match:
        return int(match.group(1))
    
    prefix_match = re.match(r'^(\d+)[\.\:\-\s]', phase_lower)
    if prefix_match:
        return int(prefix_match.group(1))

    # Semantic keyword fallbacks
    semantic_order = [
        ("foundations", 1),
        ("core", 2),
        ("advanced", 3),
        ("specialization", 3),
        ("capstone", 4),
        ("portfolio", 4),
        ("interview", 5),
        ("production", 5),
        ("readiness", 5)
    ]
    for keyword, idx in semantic_order:
        if keyword in phase_lower:
            return idx

    return 99

def compute_node_layout(nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
    """
    Computes a clean layered horizontal/vertical DAG layout for nodes.
    Phases form columns (X-axis) and parallel skills form rows (Y-axis).
    """
    phases: Dict[str, List[str]] = {}
    
    # Map nodes to phase
    for n in nodes:
        nid = n.get("node_id") if isinstance(n, dict) else getattr(n, "node_id", "")
        ph = n.get("phase", "Phase 1: Foundations") if isinstance(n, dict) else getattr(n, "phase", "Phase 1: Foundations")
        if ph not in phases:
            phases[ph] = []
        phases[ph].append(nid)

    # Sort phase keys according to extract_phase_index, then lexicographically
    sorted_phase_names = sorted(phases.keys(), key=lambda p: (
        extract_phase_index(p),
        p
    ))

    positions: Dict[str, Tuple[float, float]] = {}
    col_width = 370
    row_height = 190
    start_x = 60
    start_y = 60

    for col_idx, p_name in enumerate(sorted_phase_names):
        n_list = phases[p_name]
        col_x = start_x + (col_idx * col_width)
        for row_idx, nid in enumerate(n_list):
            row_y = start_y + (row_idx * row_height)
            positions[nid] = (float(col_x), float(row_y))

    # Apply to nodes
    for n in nodes:
        nid = n.get("node_id") if isinstance(n, dict) else getattr(n, "node_id", "")
        if nid in positions:
            x, y = positions[nid]
            if isinstance(n, dict):
                n["position_x"] = x
                n["position_y"] = y
            else:
                n.position_x = x
                n.position_y = y

    return nodes

def can_complete_node(target_node_id: str, nodes: List[Dict], edges: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validates prerequisite dependency rules.
    A node cannot be marked 'completed' or 'in_progress' unless all its
    direct prerequisite ancestor nodes are 'completed'.
    """
    node_map = { (n["node_id"] if isinstance(n, dict) else getattr(n, "node_id", "")): n for n in nodes }
    
    # Direct prerequisites: edges where target == target_node_id
    prereq_ids = [
        (e["source_node_id"] if isinstance(e, dict) else getattr(e, "source_node_id", ""))
        for e in edges
        if (e["target_node_id"] if isinstance(e, dict) else getattr(e, "target_node_id", "")) == target_node_id
    ]

    unmet_prereqs = []
    for pid in prereq_ids:
        p_node = node_map.get(pid)
        if not p_node:
            continue
        p_status = p_node.get("status") if isinstance(p_node, dict) else getattr(p_node, "status", "")
        if p_status != "completed":
            p_title = p_node.get("title") if isinstance(p_node, dict) else getattr(p_node, "title", pid)
            unmet_prereqs.append(p_title)

    return (len(unmet_prereqs) == 0, unmet_prereqs)

def update_graph_states_on_change(nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
    """
    When milestone statuses change, recalculate 'locked' vs 'available' states.
    - Completed nodes remain completed.
    - Needs revision nodes remain needs_revision.
    - In progress nodes remain in_progress if prerequisites are satisfied, else flagged.
    - If all prerequisites of a locked node are 'completed', it unlocks to 'available'.
    - If prerequisites become incomplete, available nodes revert to locked.
    """
    node_map = { (n["node_id"] if isinstance(n, dict) else getattr(n, "node_id", "")): n for n in nodes }
    
    # Map each target to its prerequisites
    target_to_sources: Dict[str, List[str]] = {}
    for e in edges:
        s = e["source_node_id"] if isinstance(e, dict) else getattr(e, "source_node_id", "")
        t = e["target_node_id"] if isinstance(e, dict) else getattr(e, "target_node_id", "")
        if t not in target_to_sources:
            target_to_sources[t] = []
        target_to_sources[t].append(s)

    for nid, node in node_map.items():
        status = node.get("status") if isinstance(node, dict) else getattr(node, "status", "locked")
        # Keep completed or needs_revision as-is
        if status in ["completed", "needs_revision"]:
            continue

        prereqs = target_to_sources.get(nid, [])
        if not prereqs:
            # Root node with no prerequisites
            new_status = "available" if status == "locked" else status
        else:
            all_done = True
            for pid in prereqs:
                p_node = node_map.get(pid)
                if not p_node:
                    continue
                p_status = p_node.get("status") if isinstance(p_node, dict) else getattr(p_node, "status", "")
                if p_status != "completed":
                    all_done = False
                    break
            
            if status == "in_progress":
                new_status = "in_progress" if all_done else "locked"
            else:
                new_status = "available" if all_done else "locked"

        if isinstance(node, dict):
            node["status"] = new_status
        else:
            node.status = new_status

    return nodes

def calculate_progress(nodes: List[Dict]) -> Tuple[float, str]:
    """
    Computes roadmap completion percentage and current active phase.
    """
    if not nodes:
        return 0.0, "Phase 1: Foundations"
    
    total = len(nodes)
    completed = 0
    current_phase = "Phase 1: Foundations"

    for n in nodes:
        status = n.get("status") if isinstance(n, dict) else getattr(n, "status", "")
        phase = n.get("phase", "Phase 1: Foundations") if isinstance(n, dict) else getattr(n, "phase", "Phase 1: Foundations")
        if status == "completed":
            completed += 1
        elif status in ["in_progress", "available"]:
            current_phase = phase

    pct = round((completed / total) * 100.0, 1)
    if completed == total:
        current_phase = "Completed - Career Ready"

    return pct, current_phase

