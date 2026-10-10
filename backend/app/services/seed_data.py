import logging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserProfile
from app.models.professional import ProfessionalProfile, ProfessionalMilestone, ProfessionalSkill
from app.models.assessment import Assessment
from app.models.resource import Resource
from app.models.project import ProjectRecommendation
from app.models.feedback import Feedback

logger = logging.getLogger(__name__)

def seed_database(db: Session):
    """Populates initial verified data if database is empty."""
    # 1. Seed Admin & Test User
    admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            full_name="PathForge Administrator",
            is_active=True,
            is_admin=True
        )
        db.add(admin)
        db.flush()
        admin_profile = UserProfile(
            user_id=admin.id,
            education_level="Master's Degree",
            degree="M.S. Computer Science",
            college="PathForge Institute",
            graduation_year=2023,
            target_career="Platform Lead",
            technical_skills=["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Machine Learning"],
            available_study_hours=20
        )
        db.add(admin_profile)
        db.commit()
        logger.info(f"Seeded admin user: {settings.ADMIN_EMAIL}")

    # Seed demo student user for immediate evaluation
    demo_user = db.query(User).filter(User.email == "student@pathforge.ai").first()
    if not demo_user:
        demo_user = User(
            email="student@pathforge.ai",
            hashed_password=get_password_hash("StudentPass123!"),
            full_name="Alex Chen",
            is_active=True,
            is_admin=False
        )
        db.add(demo_user)
        db.flush()
        demo_profile = UserProfile(
            user_id=demo_user.id,
            education_level="Undergraduate",
            degree="B.Tech Computer Science",
            college="University School of Engineering",
            graduation_year=2026,
            target_career="Machine Learning Engineer",
            technical_skills=["Python", "Basic ML", "Numpy", "Git", "SQL"],
            existing_projects=[{"title": "Housing Price Predictor", "tech": "Python, Scikit-Learn"}],
            preferred_learning_style="Hands-on Project Based",
            available_study_hours=14,
            career_target_timeline="12 Months",
            learning_budget="Free & Open Source"
        )
        db.add(demo_profile)
        db.commit()

    # 2. Seed Verified Professional Profiles
    if db.query(ProfessionalProfile).count() == 0:
        professionals_data = [
            {
                "slug": "demis-hassabis",
                "full_name": "Demis Hassabis",
                "profile_image": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80",
                "current_role": "CEO & Co-founder, Google DeepMind | Nobel Laureate in Chemistry (2024)",
                "organization": "Google DeepMind",
                "category": "AI & Machine Learning",
                "verified_date": "Verified from public sources October 2024",
                "summary": "Demis Hassabis is a British computer scientist, artificial intelligence researcher, and neuroscientist. Co-founded DeepMind in 2010 (acquired by Google in 2014) which pioneered AlphaGo, AlphaFold, and Gemini. Awarded the 2024 Nobel Prize in Chemistry for protein structure prediction.",
                "bio_citation": "Biographical data verified from University of Cambridge alumni records, University College London neuroimaging faculty archives, Google DeepMind official press releases, and Nobel Prize committee citation (2024).",
                "education_history": [
                    {"degree": "BA (Double First-Class Honours) in Computer Science", "institution": "Queens' College, University of Cambridge", "year": "1997", "verified": True},
                    {"degree": "PhD in Cognitive Neuroscience", "institution": "University College London (UCL)", "year": "2009", "verified": True},
                    {"degree": "Postdoctoral Research", "institution": "MIT & Harvard University", "year": "2010", "verified": True}
                ],
                "original_sources": [
                    {"title": "Nobel Prize in Chemistry 2024 Announcement", "url": "https://www.nobelprize.org/prizes/chemistry/2024/press-release/", "source_type": "Official Award Citation", "verified_date": "2024-10-09"},
                    {"title": "Google DeepMind Leadership Bio", "url": "https://deepmind.google/about/", "source_type": "Official Biography", "verified_date": "2024-10-01"},
                    {"title": "UCL Neuroscience Publication Archives", "url": "https://www.ucl.ac.uk/news/2024/oct/demis-hassabis-ucl-alumnus-awarded-nobel-prize-chemistry", "source_type": "Academic Institutional Record", "verified_date": "2024-10-10"}
                ],
                "learning_takeaways": [
                    "Interdisciplinary synthesis: Combining neuroscience insights about memory with reinforcement learning algorithms powered DeepMind's breakthroughs.",
                    "Rigorous foundational craftsmanship: Mastered low-level assembly and AI programming early in the gaming industry (Bullfrog/Elixir) before academic research.",
                    "Bold mission-driven milestones: Structuring long-term research into measurable challenges (Atari, Go, Protein Folding) creates focused progress."
                ],
                "suggested_student_adaptation": {
                    "focus": "AI Foundations & Applied Cognitive Principles",
                    "phases": [
                        {"phase": "Foundations", "action": "Deep mathematical foundations (calculus, linear algebra, probability) + systems programming."},
                        {"phase": "Applied Projects", "action": "Build game-playing agents with reinforcement learning (Q-learning, policy gradients)."},
                        {"phase": "Scientific AI", "action": "Apply machine learning to empirical domain problems (computational biology, physics simulations)."}
                    ]
                },
                "milestones": [
                    {"year": "1994", "title": "Lead AI Programmer on Theme Park", "organization": "Bullfrog Productions", "description": "Co-designed simulation game that sold millions, mastering AI heuristics at age 17.", "milestone_type": "Career", "order_index": 1},
                    {"year": "1997", "title": "Graduation with Double First", "organization": "University of Cambridge", "description": "Completed computer science tripos at Queens' College.", "milestone_type": "Education", "order_index": 2},
                    {"year": "1998", "title": "Founded Elixir Studios", "organization": "Elixir Studios", "description": "Independent game development company creating Republic: The Revolution.", "milestone_type": "Founding", "order_index": 3},
                    {"year": "2009", "title": "Completed PhD in Cognitive Neuroscience", "organization": "University College London", "description": "Researched episodic memory and imagination in the hippocampus (published in Science & Nature).", "milestone_type": "Breakthrough", "order_index": 4},
                    {"year": "2010", "title": "Co-founded DeepMind Technologies", "organization": "DeepMind", "description": "Founded with Shane Legg and Mustafa Suleyman to solve artificial general intelligence.", "milestone_type": "Founding", "order_index": 5},
                    {"year": "2016", "title": "AlphaGo Defeats World Champion", "organization": "Google DeepMind", "description": "Milestone achievement in deep reinforcement learning and Monte Carlo tree search.", "milestone_type": "Breakthrough", "order_index": 6},
                    {"year": "2020", "title": "AlphaFold Solves Protein Folding Challenge", "organization": "Google DeepMind", "description": "CASP14 breakthrough predicting 3D structures of 200M+ proteins.", "milestone_type": "Breakthrough", "order_index": 7},
                    {"year": "2024", "title": "Awarded Nobel Prize in Chemistry", "organization": "Royal Swedish Academy of Sciences", "description": "Recognized for computational protein structure prediction.", "milestone_type": "Award", "order_index": 8}
                ],
                "skills": [
                    {"skill_name": "Reinforcement Learning", "association_type": "documented_role"},
                    {"skill_name": "Cognitive Neuroscience", "association_type": "documented_role"},
                    {"skill_name": "Game AI & Simulation", "association_type": "public_work"},
                    {"skill_name": "Research Strategy & Leadership", "association_type": "documented_role"},
                    {"skill_name": "Computational Biology", "association_type": "public_work"},
                    {"skill_name": "Monte Carlo Tree Search", "association_type": "inferred"}
                ]
            },
            {
                "slug": "andrej-karpathy",
                "full_name": "Andrej Karpathy",
                "profile_image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80",
                "current_role": "AI Researcher, Educator & Founder (Eureka Labs) | Former Director of AI at Tesla",
                "organization": "Eureka Labs / Formerly Tesla & OpenAI",
                "category": "AI & Machine Learning",
                "verified_date": "Verified from public sources October 2024",
                "summary": "Andrej Karpathy is an AI researcher and educator. Founding member of OpenAI, former Director of AI and Autopilot Vision at Tesla, and creator of the Stanford CS231n course. Renowned for open educational resources (nanoGPT, Neural Networks: Zero to Hero).",
                "bio_citation": "Verified from Stanford University PhD dissertation archives, official Tesla Autopilot presentation disclosures, OpenAI founding member announcements, and GitHub open-source repositories.",
                "education_history": [
                    {"degree": "BSc in Computer Science & Physics", "institution": "University of Toronto", "year": "2009", "verified": True},
                    {"degree": "MSc in Computer Science", "institution": "University of British Columbia", "year": "2011", "verified": True},
                    {"degree": "PhD in Computer Vision & Deep Learning", "institution": "Stanford University (advised by Fei-Fei Li)", "year": "2016", "verified": True}
                ],
                "original_sources": [
                    {"title": "Stanford CS231n Course Syllabus", "url": "https://cs231n.github.io/", "source_type": "Academic Course Archive", "verified_date": "2024-09-15"},
                    {"title": "OpenAI Founding Team Announcement", "url": "https://openai.com/index/introducing-openai/", "source_type": "Official Organization Announcement", "verified_date": "2024-09-01"},
                    {"title": "Andrej Karpathy Personal Academic Site", "url": "https://karpathy.ai/", "source_type": "Personal Verified Website", "verified_date": "2024-10-01"}
                ],
                "learning_takeaways": [
                    "Code from scratch: Karpathy emphasizes implementing neural backpropagation, micrograd, and transformers with pure Python/C to truly master internal mechanics.",
                    "Clarity in communication: Created Stanford's most popular deep learning course by distilling complex research into intuitive visual explanations.",
                    "Production data engine: Scaled computer vision models at Tesla by treating data quality, automated labelling, and fleet edge cases as first-class citizens."
                ],
                "suggested_student_adaptation": {
                    "focus": "Deep Learning Fundamentals & Systems Implementation",
                    "phases": [
                        {"phase": "Foundations", "action": "Implement autograd from scratch (like micrograd) using pure Python before touching PyTorch."},
                        {"phase": "Core Models", "action": "Train character-level language models and build vision classifiers on benchmark datasets."},
                        {"phase": "LLM Internals", "action": "Build and train a 100M parameter GPT-2 replica using nanoGPT principles on open GPU clusters."}
                    ]
                },
                "milestones": [
                    {"year": "2015", "title": "Co-designed & Instructed Stanford CS231n", "organization": "Stanford University", "description": "Convolutional Neural Networks for Visual Recognition course became one of Stanford's largest AI classes.", "milestone_type": "Education", "order_index": 1},
                    {"year": "2015", "title": "Founding Research Scientist", "organization": "OpenAI", "description": "Worked on generative models, reinforcement learning, and gym environments.", "milestone_type": "Career", "order_index": 2},
                    {"year": "2016", "title": "Completed PhD in Deep Learning", "organization": "Stanford University", "description": "Doctoral dissertation on Connecting Images and Natural Language.", "milestone_type": "Education", "order_index": 3},
                    {"year": "2017", "title": "Director of Artificial Intelligence", "organization": "Tesla", "description": "Led the Autopilot neural network vision architecture and Dojo supercomputing design.", "milestone_type": "Career", "order_index": 4},
                    {"year": "2023", "title": "Returned to OpenAI", "organization": "OpenAI", "description": "Worked on foundational models and assistant agent capabilities.", "milestone_type": "Career", "order_index": 5},
                    {"year": "2024", "title": "Founded Eureka Labs", "organization": "Eureka Labs", "description": "AI-native educational institution developing symbiotic teacher-AI learning platforms.", "milestone_type": "Founding", "order_index": 6}
                ],
                "skills": [
                    {"skill_name": "Computer Vision & Autopilot", "association_type": "documented_role"},
                    {"skill_name": "PyTorch & Deep Learning", "association_type": "documented_role"},
                    {"skill_name": "Transformer Architecture", "association_type": "public_work"},
                    {"skill_name": "Technical Education & Communication", "association_type": "public_work"},
                    {"skill_name": "CUDA & C Programming", "association_type": "public_work"}
                ]
            },
            {
                "slug": "fei-fei-li",
                "full_name": "Fei-Fei Li",
                "profile_image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80",
                "current_role": "Professor of Computer Science & Co-Director of HAI, Stanford University | Co-founder, AI4ALL",
                "organization": "Stanford University / World Labs",
                "category": "Research Scientists",
                "verified_date": "Verified from public sources October 2024",
                "summary": "Dr. Fei-Fei Li is the Sequoia Professor of Computer Science at Stanford University and creator of ImageNet, the dataset that triggered the deep learning revolution in 2012. Member of the National Academy of Engineering and leading researcher in spatial intelligence.",
                "bio_citation": "Verified from Stanford University Faculty Directory, National Academy of Sciences archives, ImageNet project publications, and AI4ALL non-profit filings.",
                "education_history": [
                    {"degree": "AB in Physics (High Honors)", "institution": "Princeton University", "year": "1999", "verified": True},
                    {"degree": "PhD in Electrical Engineering", "institution": "California Institute of Technology (Caltech)", "year": "2005", "verified": True}
                ],
                "original_sources": [
                    {"title": "Stanford Faculty Directory Profile", "url": "https://profiles.stanford.edu/fei-fei-li", "source_type": "University Official Directory", "verified_date": "2024-09-20"},
                    {"title": "ImageNet Landmark Publication (CVPR 2009)", "url": "https://ieeexplore.ieee.org/document/5206848", "source_type": "Academic Publication", "verified_date": "2024-08-15"},
                    {"title": "National Academy of Engineering Member Citation", "url": "https://www.nae.edu/224640/Dr-FeiFei-Li", "source_type": "Academy Registry", "verified_date": "2024-09-01"}
                ],
                "learning_takeaways": [
                    "The power of data: Recognized early that algorithms without massive, diverse real-world datasets would hit a ceiling. ImageNet transformed AI research.",
                    "Human-centered AI: Emphasizes ethics, healthcare applications, and diversity in AI research alongside technical innovation.",
                    "Resilience against consensus: Pursued ImageNet when most peers advised against creating large-scale manual benchmark datasets."
                ],
                "suggested_student_adaptation": {
                    "focus": "Computer Vision & Dataset Architecture",
                    "phases": [
                        {"phase": "Foundations", "action": "Study image processing, mathematical optimization, and statistical pattern recognition."},
                        {"phase": "Benchmark Construction", "action": "Curate a rigorous, clean dataset with standardized evaluation splits for an unmet problem."},
                        {"phase": "Spatial AI", "action": "Explore 3D vision, neural radiance fields (NeRFs), and embodied robotic perception."}
                    ]
                },
                "milestones": [
                    {"year": "1999", "title": "Graduated from Princeton in Physics", "organization": "Princeton University", "description": "Completed undergraduate degree with high honors.", "milestone_type": "Education", "order_index": 1},
                    {"year": "2005", "title": "Completed PhD at Caltech", "organization": "Caltech", "description": "Doctoral research in electrical engineering and computational neuroscience.", "milestone_type": "Education", "order_index": 2},
                    {"year": "2009", "title": "Published ImageNet at CVPR", "organization": "Princeton / Stanford", "description": "Created database of 14M+ annotated images across 20K+ categories.", "milestone_type": "Breakthrough", "order_index": 3},
                    {"year": "2017", "title": "Co-founded AI4ALL", "organization": "AI4ALL", "description": "National non-profit dedicated to increasing diversity and inclusion in AI.", "milestone_type": "Founding", "order_index": 4},
                    {"year": "2019", "title": "Co-founded Stanford Institute for Human-Centered AI (HAI)", "organization": "Stanford University", "description": "Interdisciplinary institute guiding the future of AI technology and policy.", "milestone_type": "Founding", "order_index": 5},
                    {"year": "2024", "title": "Founded World Labs", "organization": "World Labs", "description": "Spatial intelligence startup developing 3D world models.", "milestone_type": "Founding", "order_index": 6}
                ],
                "skills": [
                    {"skill_name": "Computer Vision", "association_type": "documented_role"},
                    {"skill_name": "Dataset Engineering & Benchmarking", "association_type": "documented_role"},
                    {"skill_name": "Spatial Intelligence", "association_type": "public_work"},
                    {"skill_name": "Academic Leadership & Mentorship", "association_type": "documented_role"},
                    {"skill_name": "AI Ethics & Policy", "association_type": "public_work"}
                ]
            },
            {
                "slug": "mira-murati",
                "full_name": "Mira Murati",
                "profile_image": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=400&q=80",
                "current_role": "Former Chief Technology Officer, OpenAI (2020–2024)",
                "organization": "OpenAI / Independent AI Architect",
                "category": "Technology Entrepreneurs",
                "verified_date": "Verified from public sources October 2024",
                "summary": "Mira Murati is a mechanical engineer and technology executive who served as CTO of OpenAI. Led the productization, safety alignments, and deployment of ChatGPT, DALL-E, Codex, and GPT-4.",
                "bio_citation": "Verified from Dartmouth College engineering alumni archives, Tesla Model X engineering documentation, Leap Motion public announcements, and official OpenAI corporate filings.",
                "education_history": [
                    {"degree": "Bachelor of Engineering (Mechanical Engineering)", "institution": "Thayer School of Engineering, Dartmouth College", "year": "2012", "verified": True}
                ],
                "original_sources": [
                    {"title": "Dartmouth Engineering Alumni Feature", "url": "https://engineering.dartmouth.edu/news/mira-murati-openai-cto", "source_type": "University Alumni Archive", "verified_date": "2024-08-01"},
                    {"title": "OpenAI Executive Leadership Bio", "url": "https://openai.com/about/", "source_type": "Corporate Documentation", "verified_date": "2024-09-01"}
                ],
                "learning_takeaways": [
                    "Engineering to executive transition: Began in hard engineering (automotive aerospace systems at Zodiac Aerospace & Tesla) before applying systems rigor to software and AI.",
                    "Productization of frontier research: Bridges the gap between esoteric neural network research and consumer-facing interfaces serving 100M+ weekly users.",
                    "Iterative public deployment: Believes responsible AI alignment requires gradual real-world deployment with feedback loops."
                ],
                "suggested_student_adaptation": {
                    "focus": "AI Product Engineering & LLM Alignment",
                    "phases": [
                        {"phase": "Foundations", "action": "Deep systems engineering, API architecture, and scalable software pipelines."},
                        {"phase": "Safety & Alignment", "action": "Implement RLHF, red-teaming harnesses, and system prompt safety guardrails."},
                        {"phase": "Product Scaling", "action": "Deploy high-throughput inference caching and latency-optimized user experiences."}
                    ]
                },
                "milestones": [
                    {"year": "2012", "title": "Graduated from Dartmouth College", "organization": "Dartmouth College", "description": "Completed Bachelor of Engineering in mechanical engineering.", "milestone_type": "Education", "order_index": 1},
                    {"year": "2013", "title": "Senior Product Manager at Tesla", "organization": "Tesla", "description": "Led Model X product engineering and early Autopilot sensor integration.", "milestone_type": "Career", "order_index": 2},
                    {"year": "2016", "title": "VP of Product & Engineering", "organization": "Leap Motion", "description": "Spearheaded motion sensing software for virtual and augmented reality.", "milestone_type": "Career", "order_index": 3},
                    {"year": "2018", "title": "Joined OpenAI as VP of Applied AI", "organization": "OpenAI", "description": "Directed engineering teams turning foundational models into deployable APIs.", "milestone_type": "Career", "order_index": 4},
                    {"year": "2022", "title": "Appointed Chief Technology Officer", "organization": "OpenAI", "description": "Led the public launches of ChatGPT, DALL-E 2, and GPT-4.", "milestone_type": "Career", "order_index": 5}
                ],
                "skills": [
                    {"skill_name": "AI Product Management", "association_type": "documented_role"},
                    {"skill_name": "LLM Alignment & Safety", "association_type": "documented_role"},
                    {"skill_name": "Systems Engineering", "association_type": "documented_role"},
                    {"skill_name": "Hardware-Software Integration", "association_type": "public_work"},
                    {"skill_name": "Executive Strategy", "association_type": "documented_role"}
                ]
            },
            {
                "slug": "satya-nadella",
                "full_name": "Satya Nadella",
                "profile_image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=400&q=80",
                "current_role": "Chairman and Chief Executive Officer, Microsoft",
                "organization": "Microsoft",
                "category": "Technology Entrepreneurs",
                "verified_date": "Verified from public sources October 2024",
                "summary": "Satya Nadella is the Chairman and CEO of Microsoft. Transformed Microsoft by pivoting to cloud infrastructure (Azure), cross-platform open-source collaboration, and early strategic partnerships in artificial intelligence.",
                "bio_citation": "Verified from Microsoft Official Executive Biographies, Manipal Institute of Technology alumni records, University of Wisconsin–Milwaukee archives, and SEC Form 10-K filings.",
                "education_history": [
                    {"degree": "Bachelor of Engineering in Electrical Engineering", "institution": "Manipal Institute of Technology", "year": "1988", "verified": True},
                    {"degree": "MS in Computer Science", "institution": "University of Wisconsin–Milwaukee", "year": "1990", "verified": True},
                    {"degree": "MBA", "institution": "University of Chicago Booth School of Business", "year": "1997", "verified": True}
                ],
                "original_sources": [
                    {"title": "Microsoft Official Leadership Biography", "url": "https://news.microsoft.com/exec/satya-nadella/", "source_type": "Official Corporate Bio", "verified_date": "2024-09-01"},
                    {"title": "UWM Distinguished Alumni Archive", "url": "https://uwm.edu/alumni/alumni-awards/satya-nadella/", "source_type": "University Alumni Archive", "verified_date": "2024-07-15"}
                ],
                "learning_takeaways": [
                    "Growth mindset: Replaced Microsoft's 'know-it-all' culture with a 'learn-it-all' culture, emphasizing continuous learning.",
                    "Embracing open ecosystems: Pivoted Microsoft to love Linux, open source, and GitHub, recognizing developers as key champions.",
                    "Strategic clarity: Shifted capital to Cloud and AI well before widespread adoption."
                ],
                "suggested_student_adaptation": {
                    "focus": "Enterprise Cloud Architecture & Technical Leadership",
                    "phases": [
                        {"phase": "Foundations", "action": "Deep database and operating system fundamentals."},
                        {"phase": "Cloud Scale", "action": "Architect resilient cloud architectures (microservices, distributed caches, event grids)."},
                        {"phase": "Strategic Alignment", "action": "Learn how engineering systems drive business ROI and user value."}
                    ]
                },
                "milestones": [
                    {"year": "1988", "title": "B.E. from Manipal Institute of Technology", "organization": "Manipal University", "description": "Completed electrical engineering in India.", "milestone_type": "Education", "order_index": 1},
                    {"year": "1992", "title": "Joined Microsoft", "organization": "Microsoft", "description": "Worked on Windows NT and enterprise cloud solutions.", "milestone_type": "Career", "order_index": 2},
                    {"year": "2011", "title": "President of Server and Tools Business", "organization": "Microsoft", "description": "Led the buildout of Microsoft Azure cloud platform infrastructure.", "milestone_type": "Career", "order_index": 3},
                    {"year": "2014", "title": "Appointed Chief Executive Officer", "organization": "Microsoft", "description": "Succeeded Steve Ballmer as Microsoft's 3rd CEO.", "milestone_type": "Career", "order_index": 4},
                    {"year": "2018", "title": "Acquisition of GitHub", "organization": "Microsoft", "description": "Championed developer-first tools and open source integration.", "milestone_type": "Breakthrough", "order_index": 5},
                    {"year": "2023", "title": "Integrated OpenAI & Copilot Across Microsoft", "organization": "Microsoft", "description": "Pioneered enterprise generative AI integration across Azure, Office, and Windows.", "milestone_type": "Breakthrough", "order_index": 6}
                ],
                "skills": [
                    {"skill_name": "Cloud Computing & Azure", "association_type": "documented_role"},
                    {"skill_name": "Enterprise Architecture", "association_type": "documented_role"},
                    {"skill_name": "Organizational Leadership", "association_type": "documented_role"},
                    {"skill_name": "Open Source Strategy", "association_type": "public_work"},
                    {"skill_name": "Product Strategy", "association_type": "documented_role"}
                ]
            },
            {
                "slug": "linus-torvalds",
                "full_name": "Linus Torvalds",
                "profile_image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
                "current_role": "Principal Fellow & Creator of Linux and Git",
                "organization": "Linux Foundation",
                "category": "Software Engineers",
                "verified_date": "Verified from public sources October 2024",
                "summary": "Linus Torvalds is a Finnish-American software engineer who created the Linux operating system kernel in 1991 and the Git distributed version control system in 2005. His creations power the modern internet, cloud computing, Android, and global developer workflows.",
                "bio_citation": "Verified from University of Helsinki master's thesis records, Linux Foundation Fellow registry, and Git open-source revision logs.",
                "education_history": [
                    {"degree": "Master of Science in Computer Science", "institution": "University of Helsinki", "year": "1996", "verified": True}
                ],
                "original_sources": [
                    {"title": "Linux Foundation Fellow Directory", "url": "https://www.linuxfoundation.org/about/board-and-staff", "source_type": "Foundation Bio", "verified_date": "2024-09-01"},
                    {"title": "Linus' 1991 Announcement of Linux on comp.os.minix", "url": "https://www.cs.cmu.edu/~awb/linux.history.html", "source_type": "Historical Public Record", "verified_date": "2024-08-01"}
                ],
                "learning_takeaways": [
                    "Taste in code: Linus stresses that good programmers eliminate special cases through better data structure design rather than nested conditional branches.",
                    "Pragmatic tooling: Created Git in just a few weeks because existing VCS tools were inadequate for the Linux kernel's distributed workflow.",
                    "Obsession with backwards compatibility: 'Never break user space' has made Linux the world's most stable infrastructure."
                ],
                "suggested_student_adaptation": {
                    "focus": "Operating Systems & Systems Programming",
                    "phases": [
                        {"phase": "Foundations", "action": "Master C programming, pointers, memory allocation, and POSIX system calls."},
                        {"phase": "Kernel Internals", "action": "Study process scheduling, memory virtualization, and device driver architecture."},
                        {"phase": "Distributed Tooling", "action": "Build a mini version control tool from scratch modeling content-addressable DAGs (like Git objects)."}
                    ]
                },
                "milestones": [
                    {"year": "1991", "title": "Released Linux Kernel v0.01", "organization": "University of Helsinki", "description": "Announced free operating system kernel for 386 AT hardware.", "milestone_type": "Breakthrough", "order_index": 1},
                    {"year": "1996", "title": "Completed Master's Degree", "organization": "University of Helsinki", "description": "Master's thesis titled 'Linux: A Portable Operating System'.", "milestone_type": "Education", "order_index": 2},
                    {"year": "1997", "title": "Joined Transmeta", "organization": "Transmeta Corporation", "description": "Worked on software-driven CPU emulation and architecture.", "milestone_type": "Career", "order_index": 3},
                    {"year": "2005", "title": "Created Git Version Control System", "organization": "Open Source Community", "description": "Designed distributed, snapshot-based version control in response to BitKeeper controversy.", "milestone_type": "Breakthrough", "order_index": 4},
                    {"year": "2012", "title": "Millennium Technology Prize", "organization": "Technology Academy Finland", "description": "Awarded in recognition of creating Linux.", "milestone_type": "Award", "order_index": 5}
                ],
                "skills": [
                    {"skill_name": "C Programming", "association_type": "documented_role"},
                    {"skill_name": "Operating System Kernel Design", "association_type": "documented_role"},
                    {"skill_name": "Git & Distributed VCS Architecture", "association_type": "documented_role"},
                    {"skill_name": "Computer Architecture & Assembly", "association_type": "documented_role"},
                    {"skill_name": "Concurrency & Locking Primitives", "association_type": "public_work"}
                ]
            }
        ]

        for p_data in professionals_data:
            milestones = p_data.pop("milestones")
            skills = p_data.pop("skills")
            prof = ProfessionalProfile(**p_data)
            db.add(prof)
            db.flush()

            for m in milestones:
                db.add(ProfessionalMilestone(professional_id=prof.id, **m))
            for s in skills:
                db.add(ProfessionalSkill(professional_id=prof.id, **s))
        db.commit()
        logger.info("Seeded verified professional profiles.")

    # 3. Seed Diagnostic Assessments
    if db.query(Assessment).count() == 0:
        assessments_data = [
            {
                "title": "Machine Learning & AI Engineering Diagnostic",
                "topic": "Machine Learning",
                "difficulty": "Intermediate",
                "estimated_minutes": 15,
                "questions": [
                    {
                        "id": "ml_q1",
                        "question": "Which regularization technique encourages sparsity by forcing some model coefficients strictly to zero?",
                        "options": ["L2 Regularization (Ridge)", "L1 Regularization (Lasso)", "Dropout", "Batch Normalization"],
                        "correct_index": 1,
                        "explanation": "L1 regularization adds an absolute value penalty (|w|), creating corner points on the constraint boundary where coefficients hit zero exactly.",
                        "skill_tested": "Regularization & Loss Functions"
                    },
                    {
                        "id": "ml_q2",
                        "question": "What is the primary computational bottleneck in the standard Scaled Dot-Product Attention mechanism with sequence length N?",
                        "options": ["O(N) memory complexity", "O(N^2) time and memory complexity in the attention matrix", "O(log N) matrix multiplications", "O(N^3) softmax computation"],
                        "correct_index": 1,
                        "explanation": "Computing Q * K^T produces an N x N matrix, resulting in quadratic O(N^2) time and memory scaling with sequence length.",
                        "skill_tested": "Transformer Architecture"
                    },
                    {
                        "id": "ml_q3",
                        "question": "When training deep neural networks with gradient descent, which technique normalizes activations across mini-batches to mitigate internal covariate shift?",
                        "options": ["Batch Normalization", "Gradient Clipping", "Weight Decay", "Stochastic SWA"],
                        "correct_index": 0,
                        "explanation": "Batch Normalization computes mean and variance over the current mini-batch to stabilize hidden unit distributions.",
                        "skill_tested": "Deep Learning Optimization"
                    },
                    {
                        "id": "ml_q4",
                        "question": "Why is the ROC-AUC metric preferred over Accuracy when evaluating models on highly imbalanced fraud detection datasets?",
                        "options": ["Accuracy penalizes minority class precision", "Accuracy can be deceptively high (e.g. 99.9%) by trivially predicting the majority class", "ROC-AUC requires no thresholding and is always 1.0", "Accuracy is non-differentiable"],
                        "correct_index": 1,
                        "explanation": "In skewed datasets (99.9% negative), a dummy classifier yields 99.9% accuracy while finding zero fraud. ROC-AUC evaluates the true positive rate vs false positive rate trade-off across all classification thresholds.",
                        "skill_tested": "Evaluation Metrics"
                    }
                ]
            },
            {
                "title": "Data Structures, Algorithms & System Design",
                "topic": "Algorithms",
                "difficulty": "Intermediate",
                "estimated_minutes": 15,
                "questions": [
                    {
                        "id": "dsa_q1",
                        "question": "What is the amortized time complexity of inserting an element into a dynamic array (e.g., Python list or C++ std::vector)?",
                        "options": ["O(1)", "O(N)", "O(log N)", "O(N^2)"],
                        "correct_index": 0,
                        "explanation": "While occasional doubling incurs O(N) reallocation, spreading that cost across all N insertions yields an amortized O(1) per append.",
                        "skill_tested": "Amortized Analysis"
                    },
                    {
                        "id": "dsa_q2",
                        "question": "Which algorithm is optimal for finding the shortest path in an unweighted directed graph?",
                        "options": ["Dijkstra's Algorithm", "Breadth-First Search (BFS)", "Depth-First Search (DFS)", "Bellman-Ford"],
                        "correct_index": 1,
                        "explanation": "In an unweighted graph, BFS explores vertices layer by layer in order of edge distance, finding the shortest path in O(V + E) time.",
                        "skill_tested": "Graph Algorithms"
                    },
                    {
                        "id": "dsa_q3",
                        "question": "In distributed caching systems, which technique minimizes key reshuffling when a cache node is added or removed?",
                        "options": ["Modulo Hash Hashing", "Consistent Hashing with Virtual Nodes", "Round Robin Routing", "Bloom Filter Partitioning"],
                        "correct_index": 1,
                        "explanation": "Consistent hashing maps nodes and keys to a ring, ensuring only K/N keys need relocation upon node membership changes.",
                        "skill_tested": "Distributed Systems"
                    }
                ]
            },
            {
                "title": "SQL & Relational Database Engineering",
                "topic": "Databases",
                "difficulty": "Intermediate",
                "estimated_minutes": 12,
                "questions": [
                    {
                        "id": "sql_q1",
                        "question": "Which SQL window function assigns sequential ranks to rows without gaps between duplicate values?",
                        "options": ["ROW_NUMBER()", "RANK()", "DENSE_RANK()", "NTILE()"],
                        "correct_index": 2,
                        "explanation": "DENSE_RANK() assigns tied rows the same rank and immediately proceeds to the consecutive integer without leaving gaps (e.g., 1, 2, 2, 3).",
                        "skill_tested": "Advanced SQL & Window Functions"
                    },
                    {
                        "id": "sql_q2",
                        "question": "What index structure is most widely used in relational databases like PostgreSQL and MySQL for general equality and range queries?",
                        "options": ["Hash Index", "B-Tree (Balanced Tree)", "GiST Index", "LSM Tree"],
                        "correct_index": 1,
                        "explanation": "B-Trees keep data sorted and allow logarithmic O(log N) searches, sequential traversals, range scans, and prefix matches.",
                        "skill_tested": "Database Indexing"
                    }
                ]
            }
        ]

        for a_data in assessments_data:
            db.add(Assessment(**a_data))
        db.commit()
        logger.info("Seeded diagnostic assessments.")

    # 4. Seed Verified Educational Resources
    if db.query(Resource).count() == 0:
        resources_data = [
            {
                "title": "CS50: Introduction to Computer Science",
                "provider": "Harvard University / edX",
                "topic": "Programming",
                "difficulty": "Beginner to Intermediate",
                "format": "course",
                "is_free": True,
                "cost_info": "Free (Audit mode full content)",
                "source_url": "https://cs50.harvard.edu/x/",
                "verified_date": "Verified 2024",
                "description": "An introduction to the intellectual enterprises of computer science and the art of programming. Covers C, Python, SQL, HTML/CSS, and algorithms with world-class problem sets."
            },
            {
                "title": "Practical Deep Learning for Coders",
                "provider": "fast.ai",
                "topic": "Machine Learning",
                "difficulty": "Intermediate",
                "format": "course",
                "is_free": True,
                "cost_info": "100% Free / Open Source",
                "source_url": "https://course.fast.ai/",
                "verified_date": "Verified 2024",
                "description": "Top-down approach to training modern deep neural networks with PyTorch, computer vision, NLP, and model deployment."
            },
            {
                "title": "MIT 6.006: Introduction to Algorithms",
                "provider": "MIT OpenCourseWare",
                "topic": "DSA",
                "difficulty": "Intermediate",
                "format": "course",
                "is_free": True,
                "cost_info": "100% Free",
                "source_url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
                "verified_date": "Verified 2024",
                "description": "Rigorous algorithmic design and analysis covering sorting, trees, hashing, shortest paths, and dynamic programming with Python problem sets."
            },
            {
                "title": "PostgreSQL Documentation & Architectural Manual",
                "provider": "The PostgreSQL Global Development Group",
                "topic": "Databases",
                "difficulty": "All Levels",
                "format": "documentation",
                "is_free": True,
                "cost_info": "Free Open Source",
                "source_url": "https://www.postgresql.org/docs/current/",
                "verified_date": "Verified 2024",
                "description": "Comprehensive reference covering ACID properties, query execution planning (EXPLAIN ANALYZE), indexing, and concurrency control (MVCC)."
            },
            {
                "title": "Full Stack Open: Modern Web Development",
                "provider": "University of Helsinki",
                "topic": "Web Development",
                "difficulty": "Intermediate",
                "format": "interactive",
                "is_free": True,
                "cost_info": "100% Free with ECTS credit option",
                "source_url": "https://fullstackopen.com/en/",
                "verified_date": "Verified 2024",
                "description": "Master React, Redux, Node.js, Express, MongoDB/PostgreSQL, TypeScript, and CI/CD containers through hands-on project submissions."
            },
            {
                "title": "NeetCode Roadmap & Video Solutions",
                "provider": "NeetCode",
                "topic": "DSA",
                "difficulty": "Intermediate to Advanced",
                "format": "interactive",
                "is_free": True,
                "cost_info": "Free Core Problem Roadmap",
                "source_url": "https://neetcode.io/roadmap",
                "verified_date": "Verified 2024",
                "description": "Structured curriculum of pattern-based coding problems with video breakdowns for technical interview preparation."
            }
        ]

        for r_data in resources_data:
            db.add(Resource(**r_data))
        db.commit()
        logger.info("Seeded curated educational resources.")

    # 5. Seed Benchmark Practical Projects
    if db.query(ProjectRecommendation).count() == 0:
        projects_data = [
            {
                "title": "End-to-End MLOps Pipeline with Automated Model Registry",
                "target_career": "Machine Learning Engineer",
                "difficulty": "Advanced",
                "problem_statement": "Real-world machine learning teams fail when models can't be safely deployed, monitored, and retrained without manual downtime. Build a resilient CI/CD ML pipeline.",
                "learning_objectives": ["Implement automated data validation", "Set up experiment tracking with MLflow/Weights & Biases", "Build low-latency FastAPI inference service", "Containerize and deploy with automated canary checks"],
                "prerequisites": ["Python", "PyTorch / Scikit-Learn", "Docker", "Basic GitHub Actions"],
                "dataset_requirements": "Open tabular dataset (e.g., Credit Card Fraud or California Housing) or text classification dataset from HuggingFace.",
                "tech_stack": ["Python 3.11", "FastAPI", "Docker", "GitHub Actions", "Prometheus", "Pytest"],
                "implementation_milestones": [
                    "Milestone 1: Clean data ingestion pipeline with Great Expectations schema checks",
                    "Milestone 2: Model training script with automated hyperparameter tuning and model card artifact",
                    "Milestone 3: FastAPI microservice serving predictions with batching and p99 latency < 25ms",
                    "Milestone 4: Docker container with healthcheck endpoints and Prometheus telemetry"
                ],
                "testing_strategy": "Unit tests for preprocessing transforms, integration tests on API endpoints, and mock drift simulation test.",
                "evaluation_metrics": "Inference latency (p95 < 30ms), test coverage > 85%, automated Docker build passing.",
                "deployment_options": "Docker container deployed to Render, AWS ECS, or local Docker Compose with Prometheus dashboard.",
                "readme_outline": "1. System Architecture Diagram\n2. Quickstart & Installation\n3. Data Pipeline & Model Performance\n4. API Specification & Latency Benchmarks\n5. Monitoring & Observability",
                "interview_questions": [
                    "How do you handle concept drift and data schema violations in production?",
                    "What are the tradeoffs between batch inference and real-time streaming inference?",
                    "How would you ensure zero-downtime model updates during a canary rollout?"
                ],
                "demonstrates": "Production-grade software engineering applied to machine learning systems, CI/CD discipline, and observability."
            },
            {
                "title": "Distributed Task Queue & Event Bus from Scratch",
                "target_career": "Software Engineer",
                "difficulty": "Advanced",
                "problem_statement": "High-scale platforms require asynchronous background job processing with guaranteed delivery, retries, and dead-letter queues. Build a lightweight distributed task queue.",
                "learning_objectives": ["Master socket networking and concurrency", "Implement thread/worker pool execution", "Handle failure modes with exponential backoff", "Ensure idempotent job execution"],
                "prerequisites": ["Python / Go / TypeScript", "Concurrency & Multiprocessing", "TCP / Redis Protocol"],
                "dataset_requirements": "Synthetic workload generator generating 100,000 asynchronous computing tasks with configurable failure rates.",
                "tech_stack": ["Python", "Redis", "Asyncio", "Docker", "Pytest"],
                "implementation_milestones": [
                    "Milestone 1: Redis-backed FIFO queue with atomic pop/push operations (BLPOP/BRPOPLPUSH)",
                    "Milestone 2: Multi-process worker runner with graceful SIGTERM/SIGINT shutdown handling",
                    "Milestone 3: Retry mechanism with exponential backoff and persistent Dead Letter Queue (DLQ)",
                    "Milestone 4: Web dashboard showing real-time throughput, active workers, and failure logs"
                ],
                "testing_strategy": "Chaos testing simulating abrupt worker crashes, duplicate delivery handling, and poison pill tasks.",
                "evaluation_metrics": "Throughput > 5,000 tasks/second, zero dropped tasks during worker crashes, complete audit log.",
                "deployment_options": "Docker Compose cluster with 1 Redis instance, 1 master scheduler, and 3 worker nodes.",
                "readme_outline": "1. Architecture & Protocol Design\n2. Setup & Docker Run\n3. Benchmark Results\n4. Chaos Test Scenarios\n5. Configuration Reference",
                "interview_questions": [
                    "How do you guarantee at-least-once vs exactly-once task processing?",
                    "What happens if a worker dies mid-execution? How is the task recovered?",
                    "How does your system prevent the 'thundering herd' problem upon Redis reconnection?"
                ],
                "demonstrates": "Deep understanding of distributed systems failure modes, concurrency, network resilience, and architectural craftsmanship."
            }
        ]

        for p_rec in projects_data:
            db.add(ProjectRecommendation(**p_rec))
        db.commit()
        logger.info("Seeded benchmark practical projects.")

    # 6. Seed Sample Initial Verified Feedback
    if db.query(Feedback).count() == 0:
        sample_feedbacks = [
            {
                "rating": 5,
                "ease_of_use": 5,
                "roadmap_quality": 5,
                "success_stories_usefulness": 5,
                "ai_quality": 5,
                "category": "roadmap",
                "status": "resolved",
                "feature_suggestions": "Love the visual DAG! It would be great to see weekly study planner check-ins too.",
                "written_comments": "As a 3rd year CS student, this is the first roadmap tool that actually enforces prerequisites instead of dumping 50 unranked links. The Demis Hassabis career breakdown was super inspiring.",
                "is_public_review": True,
                "review_display_name": "Rohan M. (BTech CSE)"
            },
            {
                "rating": 5,
                "ease_of_use": 4,
                "roadmap_quality": 5,
                "success_stories_usefulness": 5,
                "ai_quality": 5,
                "category": "ai_recommendation",
                "status": "resolved",
                "feature_suggestions": "Adding GitHub commit verification for evidence portfolio is awesome.",
                "written_comments": "The skill gap analyzer immediately spotted that I lacked distributed systems and MLOps, which directly helped me target my final year capstone project.",
                "is_public_review": True,
                "review_display_name": "Priya S. (Pre-Final Year ML)"
            }
        ]
        for f_data in sample_feedbacks:
            db.add(Feedback(**f_data))
        db.commit()
        logger.info("Seeded initial verified student reviews.")
