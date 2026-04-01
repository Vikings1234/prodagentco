"""Planning Pipeline — 7 agents produce deliverables after Gate 1 APPROVE."""

from crewai import Crew, Task, Process
from agents.planning.pm import create_pm_planning_agent
from agents.planning.cto import create_cto_planning_agent
from agents.planning.cfo import create_cfo_planning_agent
from agents.planning.marketing import create_marketing_planning_agent
from agents.planning.brand_manager import create_brand_manager_agent
from agents.planning.designer import create_designer_agent
from agents.planning.legal import create_legal_planning_agent
from config.settings import OUTPUT_DIR


PLANNING_DIR = OUTPUT_DIR / "planning"


def run_planning_phase() -> str:
    """Run all 7 planning agents and save outputs to outputs/planning/."""

    PLANNING_DIR.mkdir(exist_ok=True)

    # Load context from previous phases
    brief_path = OUTPUT_DIR / "discovery-brief.md"
    verdict_path = OUTPUT_DIR / "debate-verdict.md"

    discovery_brief = brief_path.read_text() if brief_path.exists() else ""
    debate_verdict = verdict_path.read_text() if verdict_path.exists() else ""

    context_block = (
        f"## Discovery Brief\n{discovery_brief}\n\n"
        f"## Debate Verdict\n{debate_verdict}"
    )

    # Create agents
    pm = create_pm_planning_agent()
    cto = create_cto_planning_agent()
    cfo = create_cfo_planning_agent()
    marketing = create_marketing_planning_agent()
    brand = create_brand_manager_agent()
    designer = create_designer_agent()
    legal = create_legal_planning_agent()

    # --- Tasks ---

    pm_task = Task(
        description=(
            "Write a complete PRD for the approved opportunity. Include: executive summary, "
            "problem statement, target personas, user stories with acceptance criteria, "
            "feature priority matrix (P0/P1/P2), success metrics, scope boundaries, "
            "and phased release plan.\n\n"
            f"{context_block}"
        ),
        expected_output=(
            "A full PRD in markdown with sections: Executive Summary, Problem Statement, "
            "Personas, User Stories (with acceptance criteria), Feature Priority Matrix, "
            "Success Metrics, Out of Scope, Release Plan."
        ),
        agent=pm,
        output_file=str(PLANNING_DIR / "prd.md"),
    )

    cto_task = Task(
        description=(
            "Write a complete technical specification. Reference the PRD for feature scope. "
            "Include: system architecture, tech stack decisions, API design, database schema, "
            "infrastructure plan, security architecture, effort estimates, and risk register.\n\n"
            f"{context_block}"
        ),
        expected_output=(
            "A full tech spec in markdown with sections: Architecture Overview, Tech Stack, "
            "API Design, Data Model, Infrastructure, Security, Effort Estimates, Risk Register."
        ),
        agent=cto,
        context=[pm_task],
        output_file=str(PLANNING_DIR / "tech-spec.md"),
    )

    cfo_task = Task(
        description=(
            "Write a complete financial model brief. Reference the PRD for scope and the "
            "tech spec for cost inputs. Include: pricing model, unit economics, revenue "
            "projections, cost structure, burn rate, break-even, and sensitivity analysis.\n\n"
            f"{context_block}"
        ),
        expected_output=(
            "A financial model brief in markdown with sections: Pricing Model, Unit Economics, "
            "Revenue Projections, Cost Structure, Burn Rate & Runway, Break-Even, Sensitivity Analysis."
        ),
        agent=cfo,
        context=[pm_task, cto_task],
        output_file=str(PLANNING_DIR / "financial-model.md"),
    )

    marketing_task = Task(
        description=(
            "Write a complete GTM plan. Reference the PRD for product scope and the "
            "financial model for budget constraints. Include: ICP, positioning, competitive "
            "map, channel strategy, launch timeline, and 90-day metrics.\n\n"
            f"{context_block}"
        ),
        expected_output=(
            "A GTM plan in markdown with sections: ICP, Positioning & Messaging, "
            "Competitive Positioning, Channel Strategy, Launch Timeline, 90-Day Metrics."
        ),
        agent=marketing,
        context=[pm_task, cfo_task],
        output_file=str(PLANNING_DIR / "gtm-plan.md"),
    )

    brand_task = Task(
        description=(
            "Create a brand brief. Reference the PRD for product identity and the GTM plan "
            "for positioning. Include: 3-5 name candidates, brand personality, tone of voice, "
            "color palette direction, typography, tagline options, and positioning statement.\n\n"
            f"{context_block}"
        ),
        expected_output=(
            "A brand brief in markdown with sections: Name Candidates, Brand Personality, "
            "Tone of Voice, Visual Direction, Tagline Options, Positioning Statement."
        ),
        agent=brand,
        context=[pm_task, marketing_task],
        output_file=str(PLANNING_DIR / "brand-brief.md"),
    )

    designer_task = Task(
        description=(
            "Create a UX brief. Reference the PRD user stories for coverage and the brand "
            "brief for visual direction. Include: complete user flows, screen-by-screen "
            "wireframe descriptions, UI component inventory, interaction patterns, "
            "accessibility requirements, and responsive considerations.\n\n"
            f"{context_block}"
        ),
        expected_output=(
            "A UX brief in markdown with sections: User Flows, Screen Wireframes, "
            "Component Inventory, Interaction Patterns, Accessibility, Responsive Design."
        ),
        agent=designer,
        context=[pm_task, brand_task],
        output_file=str(PLANNING_DIR / "ux-brief.md"),
    )

    legal_task = Task(
        description=(
            "Write a complete legal and compliance brief. Reference the PRD, tech spec, "
            "and financial model for scope. Include: regulatory requirements by jurisdiction, "
            "licenses, data privacy, IP strategy, ToS/privacy policy needs, liability, "
            "insurance, and a compliance checklist with launch-blocker vs. post-launch items.\n\n"
            f"{context_block}"
        ),
        expected_output=(
            "A legal brief in markdown with sections: Regulatory Requirements, Licenses, "
            "Data Privacy, IP Strategy, Terms & Policies, Liability, Compliance Checklist."
        ),
        agent=legal,
        context=[pm_task, cto_task, cfo_task],
        output_file=str(PLANNING_DIR / "legal-brief.md"),
    )

    # --- Crew ---

    all_agents = [pm, cto, cfo, marketing, brand, designer, legal]
    all_tasks = [pm_task, cto_task, cfo_task, marketing_task, brand_task, designer_task, legal_task]

    # Map tasks to output filenames for manual file writing
    task_files = [
        (pm_task, "prd.md"),
        (cto_task, "tech-spec.md"),
        (cfo_task, "financial-model.md"),
        (marketing_task, "gtm-plan.md"),
        (brand_task, "brand-brief.md"),
        (designer_task, "ux-brief.md"),
        (legal_task, "legal-brief.md"),
    ]

    crew = Crew(
        agents=all_agents,
        tasks=all_tasks,
        process=Process.sequential,
        verbose=True,
    )

    print("🏗️ ProdAgentCo Planning Phase — 7 agents starting...")
    crew_output = crew.kickoff()

    # Explicitly write each task's output to file
    for task, filename in task_files:
        filepath = PLANNING_DIR / filename
        output = str(task.output)
        filepath.write_text(output)
        print(f"  📄 Saved {filename} ({len(output)} chars)")

    result = str(crew_output)

    # Write combined summary
    summary_path = PLANNING_DIR / "planning-summary.md"
    summary_path.write_text(
        "# ProdAgentCo Planning Summary\n\n"
        "## Deliverables\n"
        "- [PRD](prd.md)\n"
        "- [Tech Spec](tech-spec.md)\n"
        "- [Financial Model](financial-model.md)\n"
        "- [GTM Plan](gtm-plan.md)\n"
        "- [Brand Brief](brand-brief.md)\n"
        "- [UX Brief](ux-brief.md)\n"
        "- [Legal Brief](legal-brief.md)\n\n"
        f"## Final Agent Output\n{result}\n"
    )

    print(f"\n✅ Planning complete. 7 deliverables saved to {PLANNING_DIR}/")
    return result
