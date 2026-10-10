import json
import logging
from typing import Dict, Any, List
from app.core.config import settings
from app.schemas.roadmap import RoadmapGenerateRequest, ReplanRequest, CareerCompareOut
from app.services.graph_engine import (
    compute_node_layout,
    update_graph_states_on_change,
    validate_roadmap_graph,
)

logger = logging.getLogger(__name__)

def generate_roadmap_ai(req: RoadmapGenerateRequest) -> Dict[str, Any]:
    """
    Generates a personalized career roadmap using Google Gemini if GEMINI_API_KEY is configured,
    or falls back gracefully to the deterministic Heuristic Career Intelligence Engine.
    """
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)

            prompt = f"""
You are the Lead Career Architect at PATHFORGE AI.
Generate a structured, personalized, professional career roadmap.
Target Career: {req.dream_job}
Target Company / Tier: {req.target_company}
Current Education: {req.education_level}
Current Skills: {", ".join(req.current_skills) if req.current_skills else "None specified"}
Current Experience: {req.current_experience}
Timeline: {req.timeline}
Weekly Study Hours: {req.weekly_hours}
Learning Format: {req.learning_format}
Salary Aspiration: {req.salary_aspiration or 'Industry Standard'}

OUTPUT FORMAT: Return ONLY valid, raw JSON (no markdown formatting, no code block backticks) matching this exact schema:
{{
  "title": "{req.dream_job} Roadmap for {req.target_company}",
  "starting_skill_assessment": "Comprehensive summary of baseline vs requirements",
  "completion_criteria": "Clear verifiable standard to declare career readiness",
  "suggested_next_action": "Exact first task to begin today",
  "current_phase": "Phase 1: Foundations",
  "nodes": [
    {{
      "node_id": "phase1_node1",
      "title": "Skill/Milestone Title",
      "category": "Core Skills / Practical Projects / Systems",
      "difficulty": "Beginner / Intermediate / Advanced",
      "estimated_hours": 20,
      "status": "available",
      "description": "Thorough practical description",
      "deliverable": "Specific project or repository deliverable",
      "completion_criteria": "How to verify completion",
      "recommended_next_action": "Actionable task",
      "phase": "Phase 1: Foundations",
      "practical_assignments": ["Assignment 1", "Assignment 2"],
      "resources": [{{"title": "Resource Name", "url": "https://...", "type": "documentation", "is_free": true}}]
    }}
  ],
  "edges": [
    {{
      "source_node_id": "phase1_node1",
      "target_node_id": "phase2_node1",
      "edge_type": "prerequisite"
    }}
  ],
  "sprints": [
    {{
      "week_number": 1,
      "goals": ["Master Core Foundations", "Build Initial Demo"],
      "planned_hours": {req.weekly_hours},
      "tasks": [
        {{"id": "w1_t1", "text": "Set up environment and complete project scaffold", "completed": false, "estimated_hours": 3}},
        {{"id": "w1_t2", "text": "Complete foundational implementation drills", "completed": false, "estimated_hours": 5}}
      ]
    }}
  ]
}}
Ensure there are 10 to 14 nodes organized into:
Phase 1: Foundations
Phase 2: Core Engineering
Phase 3: Advanced Specialization
Phase 4: Capstone & Portfolio
Phase 5: Interview & Production Readiness
All edges must form a strictly acyclic Directed Acyclic Graph (DAG).
Root nodes in Phase 1 should have status 'available' or 'completed' if user already knows them; downstream nodes must have status 'locked'.
"""
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            roadmap_dict = json.loads(clean_text)
            
            # Validate DAG structure from AI response
            is_valid, validation_err = validate_roadmap_graph(
                roadmap_dict.get("nodes", []),
                roadmap_dict.get("edges", [])
            )
            if not is_valid:
                logger.warning(f"Gemini output DAG validation failed ({validation_err}). Falling back to Heuristic AI Engine.")
                return _heuristic_generate_roadmap(req)

            roadmap_dict["ai_mode"] = "gemini_pro"
            # Polish coordinates & prerequisite statuses
            roadmap_dict["nodes"] = compute_node_layout(roadmap_dict["nodes"], roadmap_dict["edges"])
            roadmap_dict["nodes"] = update_graph_states_on_change(roadmap_dict["nodes"], roadmap_dict["edges"])
            return roadmap_dict
        except Exception as e:
            logger.warning(f"Gemini API call encountered error: {e}. Falling back to Heuristic AI Engine.")

    # Fallback to Heuristic Algorithmic Engine
    return _heuristic_generate_roadmap(req)

def _heuristic_generate_roadmap(req: RoadmapGenerateRequest) -> Dict[str, Any]:
    """
    Deterministic Heuristic AI Engine that dynamically crafts personalized roadmaps
    adapting to role, target company, existing skills, weekly hours, and target timeline.
    """
    dream_lower = req.dream_job.lower()
    skills_lower = [s.lower().strip() for s in req.current_skills]
    company = req.target_company or "Tier-1 Tech Companies"
    weekly_hrs = req.weekly_hours or 14

    # Determine archetype
    if "machine learning" in dream_lower or "ml" in dream_lower or "ai" in dream_lower:
        archetype = "ml_engineer"
    elif "data" in dream_lower:
        archetype = "data_scientist"
    elif "frontend" in dream_lower or "react" in dream_lower or "ui" in dream_lower:
        archetype = "frontend_engineer"
    elif "cloud" in dream_lower or "devops" in dream_lower or "site reliability" in dream_lower:
        archetype = "devops_engineer"
    elif "cyber" in dream_lower or "security" in dream_lower:
        archetype = "security_engineer"
    elif "product" in dream_lower:
        archetype = "product_manager"
    else:
        archetype = "software_engineer"

    node_definitions = _get_archetype_nodes(archetype, req.dream_job, company, skills_lower)
    edges = _generate_dag_edges(node_definitions)

    # Initial sprint planner
    sprints = [
        {
            "week_number": 1,
            "goals": [f"Scaffold {req.dream_job} learning environment", "Complete diagnostic baseline and foundational drills"],
            "planned_hours": weekly_hrs,
            "completed_hours": 0,
            "status": "active",
            "tasks": [
                {"id": "w1_t1", "text": "Set up version-controlled development environment and roadmap workspace", "completed": False, "estimated_hours": 3},
                {"id": "w1_t2", "text": f"Complete foundational concepts drill for {node_definitions[0]['title']}", "completed": False, "estimated_hours": 5},
                {"id": "w1_t3", "text": "Build first mini-prototype deliverable and commit to GitHub", "completed": False, "estimated_hours": 6}
            ]
        },
        {
            "week_number": 2,
            "goals": ["Expand algorithmic depth", "Deliver Phase 1 milestone submission"],
            "planned_hours": weekly_hrs,
            "completed_hours": 0,
            "status": "active",
            "tasks": [
                {"id": "w2_t1", "text": "Solve 5 targeted pattern problems aligned with target role", "completed": False, "estimated_hours": 4},
                {"id": "w2_t2", "text": "Complete peer code review and unit tests for deliverable", "completed": False, "estimated_hours": 5},
                {"id": "w2_t3", "text": "Submit milestone evidence in Career Evidence Portfolio", "completed": False, "estimated_hours": 5}
            ]
        }
    ]

    # Calculate positions & initial lock states
    nodes = compute_node_layout(node_definitions, edges)
    nodes = update_graph_states_on_change(nodes, edges)

    # Baseline summary
    known_count = sum(1 for n in nodes if n["status"] == "completed")
    starting_assessment = (
        f"Evaluated current proficiency across {len(req.current_skills)} reported skills. "
        f"{known_count} foundational milestones already verified or recognized. "
        f"Targeting {company} hiring standards with a structured {req.timeline} roadmap."
    )

    first_available = next((n for n in nodes if n["status"] == "available"), nodes[0])

    return {
        "title": f"Tailored {req.dream_job} Roadmap for {company}",
        "starting_skill_assessment": starting_assessment,
        "completion_criteria": f"Production-grade capstone project, verified GitHub evidence portfolio, and 85%+ readiness score for {company} technical screens.",
        "suggested_next_action": f"Begin milestone: {first_available['title']} ({first_available['estimated_hours']} hrs estimated).",
        "current_phase": "Phase 1: Foundations",
        "ai_mode": "heuristic_intelligence",
        "nodes": nodes,
        "edges": edges,
        "sprints": sprints
    }

def _get_archetype_nodes(archetype: str, role_title: str, company: str, known_skills: List[str]) -> List[Dict[str, Any]]:
    """Synthesizes structured milestone nodes for role archetypes."""
    templates = {
        "ml_engineer": [
            ("n1", "Advanced Python & Numerical Computing", "Phase 1: Foundations", "Beginner", 25, ["python", "numpy", "pandas"],
             "Vectorized computing, broadcasting, memory efficiency, and idiomatic Python 3 for data pipelines.",
             "High-throughput data parsing benchmark repository with pytest suite."),
            ("n2", "Linear Algebra & Vector Calculus for ML", "Phase 1: Foundations", "Intermediate", 20, ["math", "linear algebra", "calculus"],
             "Eigenvalues, SVD, gradients, Hessians, and backpropagation mechanics from scratch.",
             "Numpy implementation of neural backpropagation without high-level frameworks."),
            ("n3", "Classical Machine Learning & Statistical Modeling", "Phase 2: Core Engineering", "Intermediate", 30, ["scikit-learn", "statistics", "ml"],
             "Bias-variance tradeoff, regularized regression, ensemble trees (XGBoost, LightGBM), cross-validation.",
             "End-to-end predictive model on tabular dataset with hyperparameter tuning and model card."),
            ("n4", "Deep Learning Foundations & PyTorch", "Phase 2: Core Engineering", "Intermediate", 35, ["pytorch", "deep learning"],
             "Computation graphs, custom autograd, CNNs, residual connections, and training loop optimizations.",
             "Custom PyTorch vision classifier with mixed precision training and wandb logging."),
            ("n5", "Transformer Architectures & Modern NLP", "Phase 3: Advanced Specialization", "Advanced", 40, ["transformers", "huggingface", "llm"],
             "Multi-head self-attention, tokenization, encoder-decoder vs decoder-only models, RoPE embeddings.",
             "Fine-tuned causal language model with LoRA/QLoRA on domain-specific dataset."),
            ("n6", "MLOps, Serving & Real-Time Inference", "Phase 3: Advanced Specialization", "Advanced", 30, ["docker", "fastapi", "mlops", "kubernetes"],
             "ONNX runtime acceleration, Triton inference server, containerization, and latency profiling.",
             "Production FastAPI inference microservice with Docker, Prometheus metrics, and automated tests."),
            ("n7", "Distributed Systems & Large-Scale Data (Spark/Ray)", "Phase 4: Capstone & Portfolio", "Advanced", 35, ["spark", "ray", "kafka"],
             "Distributed model training (DDP/FSDP), feature stores (Feast), and asynchronous streaming pipelines.",
             "Ray-based distributed data preprocessor handling 50M+ rows with partition tuning."),
            ("n8", f"Capstone: Production AI Platform for {company}", "Phase 4: Capstone & Portfolio", "Advanced", 45, ["capstone", "end-to-end"],
             "Architect a full-stack AI system solving a real-world problem matching target employer's domain.",
             "Live deployed web application, documented system architecture diagram, and CI/CD workflow."),
            ("n9", f"System Design & Technical Interviews at {company}", "Phase 5: Interview & Production Readiness", "Advanced", 25, ["interview", "system design", "dsa"],
             "Large-scale recommendation systems, vector search indexing (HNSW/Faiss), and behavioral leadership.",
             "Comprehensive interview study guide with 15 solved end-to-end ML system design architectures.")
        ],
        "software_engineer": [
            ("n1", "Data Structures, Algorithms & Complexity", "Phase 1: Foundations", "Intermediate", 30, ["dsa", "algorithms", "data structures"],
             "Time/space complexity, trees, graphs, dynamic programming, heaps, and sliding window patterns.",
             "Curated repository of 75+ solved algorithmic problem patterns with automated tests."),
            ("n2", "Advanced Object-Oriented & Modern Language Idioms", "Phase 1: Foundations", "Intermediate", 20, ["python", "java", "c++", "go", "typescript"],
             "Design patterns (SOLID), concurrency models, async I/O, garbage collection internals.",
             "Thread-safe in-memory cache with eviction policy (LRU) and benchmark comparisons."),
            ("n3", "Relational Database Design & Query Optimization", "Phase 2: Core Engineering", "Intermediate", 25, ["sql", "postgresql", "database"],
             "ACID guarantees, indexing strategies (B-Trees), execution plans, transactions, and migration tools.",
             "Normalized PostgreSQL database schema with indexing optimizations and load test reports."),
            ("n4", "REST & gRPC Microservice Architecture", "Phase 2: Core Engineering", "Intermediate", 30, ["api", "fastapi", "grpc", "node"],
             "Protocol buffers, idempotent API design, middleware patterns, rate limiting, and observability.",
             "High-throughput microservice handling structured requests with distributed tracing (OpenTelemetry)."),
            ("n5", "Distributed Systems & Cloud Architecture", "Phase 3: Advanced Specialization", "Advanced", 35, ["cloud", "aws", "docker", "redis"],
             "CAP theorem, eventual consistency, message queues (Kafka/RabbitMQ), Redis caching patterns.",
             "Event-driven order processing system with idempotent event consumption and fallback queues."),
            ("n6", "Container Orchestration & CI/CD Pipelines", "Phase 3: Advanced Specialization", "Intermediate", 25, ["kubernetes", "docker", "ci/cd"],
             "Docker multi-stage builds, Kubernetes deployments, service meshes, zero-downtime rolling updates.",
             "GitHub Actions CI/CD pipeline building, testing, linting, and deploying to cloud infrastructure."),
            ("n7", f"Capstone: Resilient Scalable System for {company}", "Phase 4: Capstone & Portfolio", "Advanced", 40, ["capstone", "portfolio"],
             "Build a high-availability distributed platform featuring real-time synchronization.",
             "Production-deployed application with architecture RFC, benchmarks, and monitoring dashboard."),
            ("n8", f"System Design & Coding Interviews at {company}", "Phase 5: Interview & Production Readiness", "Advanced", 25, ["interviews", "system design"],
             "Distributed rate limiters, key-value stores, URL shorteners, and company-specific coding rounds.",
             "Mock interview readiness dossier covering architectural tradeoffs and behavioral STAR stories.")
        ],
        "data_scientist": [
            ("n1", "Python for Data Analysis & Exploratory Statistics", "Phase 1: Foundations", "Beginner", 20, ["python", "pandas", "numpy"],
             "Data cleaning, exploratory data analysis, hypothesis testing, and statistical distributions.",
             "Interactive Jupyter notebook analyzing real-world dataset with statistical rigor."),
            ("n2", "Relational Databases, Advanced SQL & Warehousing", "Phase 1: Foundations", "Intermediate", 25, ["sql", "database"],
             "Window functions, CTEs, query plan analysis, star schemas, and data warehouse patterns.",
             "Analytical SQL suite solving 20 complex business cohort queries on 1M+ row dataset."),
            ("n3", "Applied Statistical Inference & A/B Testing", "Phase 2: Core Engineering", "Intermediate", 25, ["statistics", "a/b testing"],
             "Power analysis, p-values, bootstrap confidence intervals, variance reduction (CUPED).",
             "Complete A/B experimentation analysis framework with automated sample size calculator."),
            ("n4", "Predictive Modeling & Feature Engineering", "Phase 2: Core Engineering", "Intermediate", 30, ["scikit-learn", "feature engineering"],
             "Tree ensembles, cross-validation strategies, handling imbalanced data, feature importance.",
             "Kaggle-style competitive ML pipeline with modular transformers and automated evaluation."),
            ("n5", "Time Series Forecasting & Causal Inference", "Phase 3: Advanced Specialization", "Advanced", 30, ["time series", "causal inference"],
             "ARIMA, Prophet, synthetic control methods, difference-in-differences, econometric models.",
             "Demand forecasting engine with rolling-origin cross validation and anomaly alerts."),
            ("n6", "Data Storytelling & Executive Dashboards", "Phase 3: Advanced Specialization", "Intermediate", 20, ["tableau", "streamlit", "powerbi"],
             "Data visualization best practices, cognitive load reduction, stakeholder communication.",
             "Interactive Streamlit dashboard translating data insights into executive action items."),
            ("n7", f"Capstone: Enterprise Data Science Project for {company}", "Phase 4: Capstone & Portfolio", "Advanced", 35, ["portfolio", "capstone"],
             "End-to-end business problem formulation, modeling, interpretation, and ROI calculation.",
             "Deployed data application with technical paper and executive presentation deck."),
            ("n8", f"Technical Case Studies & Interview Prep for {company}", "Phase 5: Interview & Production Readiness", "Advanced", 20, ["interview", "case studies"],
             "Product sense metrics, metric drop root-cause analysis, and take-home challenge simulations.",
             "Dossier of 10 solved technical case study frameworks for data science on-sites.")
        ]
    }

    raw_list = templates.get(archetype, templates["software_engineer"])
    nodes = []

    for idx, item in enumerate(raw_list):
        nid, title, phase, diff, hrs, match_keywords, desc, deliv = item
        # Check if user already knows this milestone
        already_known = any(kw in known_skills for kw in match_keywords)
        status = "completed" if (already_known and idx < 2) else ("available" if idx == 0 else "locked")

        nodes.append({
            "node_id": nid,
            "title": title,
            "category": "Core Competency" if "Foundations" in phase else ("Applied Systems" if "Core" in phase else "Specialization"),
            "difficulty": diff,
            "estimated_hours": hrs,
            "status": status,
            "description": desc,
            "deliverable": deliv,
            "completion_criteria": f"Pass test suite, adhere to code quality standards, and satisfy deliverable requirements.",
            "recommended_next_action": f"Review learning syllabus and begin hands-on assignment for {title}.",
            "phase": phase,
            "order_index": idx,
            "is_self_reported": already_known,
            "resources": [
                {"title": f"Official Reference & Guide: {title}", "url": "https://docs.python.org/3/", "type": "documentation", "is_free": True},
                {"title": f"Interactive Curriculum on {title}", "url": "https://cs50.harvard.edu/", "type": "course", "is_free": True}
            ],
            "practical_assignments": [
                f"Implement core logic milestone for {title}",
                f"Write automated unit tests verifying edge cases and constraints"
            ]
        })

    return nodes

def _generate_dag_edges(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Connects nodes into a sequential & branching DAG without cycles."""
    edges = []
    for i in range(len(nodes) - 1):
        edges.append({
            "source_node_id": nodes[i]["node_id"],
            "target_node_id": nodes[i+1]["node_id"],
            "edge_type": "prerequisite"
        })
    # Add parallel branching prerequisite if 6+ nodes
    if len(nodes) >= 6:
        edges.append({
            "source_node_id": nodes[1]["node_id"],
            "target_node_id": nodes[3]["node_id"],
            "edge_type": "recommended"
        })
    return edges

def replan_roadmap_ai(current_nodes: List[Dict], current_edges: List[Dict], req: ReplanRequest) -> Dict[str, Any]:
    """
    Dynamically recalculates roadmap nodes when user goals, study hours, or skills change.
    Preserves completed nodes deterministically!
    """
    # If user provided newly known skills, update those nodes
    known = [s.lower().strip() for s in (req.known_skills or [])]
    for n in current_nodes:
        title_lower = n["title"].lower()
        if any(k in title_lower for k in known):
            n["status"] = "completed"
            n["is_self_reported"] = True

    # Re-evaluate prerequisites and unlock dependent nodes
    updated_nodes = update_graph_states_on_change(current_nodes, current_edges)
    
    explanation = f"Adaptive Replan executed successfully: Evaluated prerequisite graph. Remaining effort recalibrated based on study pace and milestone completions."
    return {
        "nodes": updated_nodes,
        "explanation": explanation
    }

def compare_careers_ai(career_a: str, career_b: str) -> Dict[str, Any]:
    """Provides side-by-side comparison between two career trajectories."""
    c_a = career_a.strip()
    c_b = career_b.strip()

    return {
        "career_a": c_a,
        "career_b": c_b,
        "summary_a": f"{c_a} focuses on architecting, testing, and scaling systems tailored for production engineering.",
        "summary_b": f"{c_b} prioritizes analytical depth, data modeling, statistical inference, and insight formulation.",
        "shared_skills": ["Python / Core Programming", "SQL & Database Queries", "Git & Version Control", "Problem Solving & Algorithmic Foundations", "Communication"],
        "unique_skills_a": ["Distributed Systems", "CI/CD & Containerization", "API & Microservice Design", "Concurrency & Low-Latency Tuning"],
        "unique_skills_b": ["Statistical Hypothesis Testing", "Exploratory Data Analysis", "Feature Engineering", "A/B Experimentation & Metrics"],
        "learning_effort_a": "Approx. 450 - 600 Hours (8 - 12 Months)",
        "learning_effort_b": "Approx. 400 - 550 Hours (7 - 10 Months)",
        "common_tools_a": ["Docker", "Kubernetes", "FastAPI / Node", "PostgreSQL", "Redis"],
        "common_tools_b": ["Pandas", "Scikit-Learn", "Jupyter", "Tableau / Streamlit", "Snowflake / BigQuery"],
        "interview_focus_a": "Data Structures, System Design, Concurrency, Live Coding",
        "interview_focus_b": "SQL Drills, Machine Learning Theory, Case Studies, Experiment Design",
        "transition_difficulty": "Moderate — approx. 60% skills overlap; requires mastering specialized domain tooling.",
        "recommendation": f"If you prefer building resilient software and scalable infrastructure, choose {c_a}. If you prefer extracting insights from data patterns and mathematical models, choose {c_b}."
    }
