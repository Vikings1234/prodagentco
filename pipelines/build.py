"""Build Pipeline — Engineer → QA → Security, then Gate 3 notification."""

import subprocess
import datetime
from crewai import Crew, Task, Process
from agents.build.engineer import create_engineer_agent
from agents.build.qa import create_qa_agent
from agents.build.security import create_security_agent
from gates.hitl_gates import gate3_notify
from config.settings import OUTPUT_DIR


BUILD_DIR = OUTPUT_DIR / "build"


def run_build_phase() -> str:
    """Run Engineer → QA → Security and save outputs to outputs/build/."""

    BUILD_DIR.mkdir(exist_ok=True)

    # Load context from planning phase
    planning_dir = OUTPUT_DIR / "planning"
    prd_text = (planning_dir / "prd.md").read_text() if (planning_dir / "prd.md").exists() else ""
    arch_text = (planning_dir / "architecture-doc.md").read_text() if (planning_dir / "architecture-doc.md").exists() else ""
    ux_text = (planning_dir / "ux-brief.md").read_text() if (planning_dir / "ux-brief.md").exists() else ""
    brand_text = (planning_dir / "brand-brief.md").read_text() if (planning_dir / "brand-brief.md").exists() else ""

    context_block = (
        f"## PRD (User Stories & Acceptance Criteria)\n{prd_text}\n\n"
        f"## Architecture Document (Tech Stack & API Design)\n{arch_text}\n\n"
        f"## UX Brief (Screens & Components)\n{ux_text}\n\n"
        f"## Brand Brief (Visual Direction)\n{brand_text}"
    )

    # Create agents
    engineer = create_engineer_agent()
    qa = create_qa_agent()
    security = create_security_agent()

    # --- Tasks ---

    engineer_task = Task(
        description=(
            "Write production-ready code for the product described in the PRD and architecture "
            "document below. Follow the tech stack decisions exactly. Implement all P0 user "
            "stories with their acceptance criteria. Output a single markdown document where "
            "each file is a section with the file path as heading and the code in a fenced "
            "code block. Include: project structure, core application code, API routes, data "
            "models, configuration files, environment template, and basic tests.\n\n"
            f"{context_block}"
        ),
        expected_output=(
            "A complete markdown document with all source files. Each file as: "
            "## path/to/file.ext followed by a fenced code block with the file contents. "
            "Include: README.md, package/requirements config, main application entry point, "
            "API routes, data models, middleware, tests, and .env.example."
        ),
        agent=engineer,
        output_file=str(BUILD_DIR / "codebase.md"),
    )

    qa_task = Task(
        description=(
            "Review the Engineer's code output for quality and correctness. Cross-reference "
            "against the PRD's acceptance criteria and the architecture document's design "
            "decisions. Check: code structure, error handling, test coverage of P0 stories, "
            "API contract correctness, data validation, and dependency management.\n\n"
            f"## PRD for reference\n{prd_text[:5000]}"
        ),
        expected_output=(
            "A QA report in markdown with: Overall Verdict (PASS/FAIL/CONDITIONAL), "
            "Code Quality Score (1-10), Issues Found (table with severity/description/location), "
            "Test Coverage Assessment, Acceptance Criteria Checklist, and Recommendations."
        ),
        agent=qa,
        context=[engineer_task],
        output_file=str(BUILD_DIR / "qa-report.md"),
    )

    security_task = Task(
        description=(
            "Perform a security audit of the Engineer's code. Check for OWASP Top 10 "
            "vulnerabilities, hardcoded secrets, insecure dependencies, missing input "
            "validation, authentication flaws, data exposure risks, and CORS issues.\n\n"
            f"## Architecture Document for reference\n{arch_text[:5000]}"
        ),
        expected_output=(
            "A security report in markdown with: Overall Risk Rating (CRITICAL/HIGH/MEDIUM/LOW), "
            "Findings (table with severity/CWE/description/remediation), "
            "Dependency Risk Assessment, Authentication Review, "
            "Data Protection Assessment, and Security Recommendations."
        ),
        agent=security,
        context=[engineer_task],
        output_file=str(BUILD_DIR / "security-report.md"),
    )

    # --- Crew ---

    crew = Crew(
        agents=[engineer, qa, security],
        tasks=[engineer_task, qa_task, security_task],
        process=Process.sequential,
        verbose=True,
    )

    print("🔨 ProdAgentCo Build Phase — Engineer → QA → Security...")
    crew_output = crew.kickoff()

    # Explicitly write each task's output
    task_files = [
        (engineer_task, "codebase.md"),
        (qa_task, "qa-report.md"),
        (security_task, "security-report.md"),
    ]
    for task, filename in task_files:
        filepath = BUILD_DIR / filename
        output = str(task.output)
        filepath.write_text(output)
        print(f"  📄 Saved {filename} ({len(output)} chars)")

    result = str(crew_output)

    # Write build summary
    summary_path = BUILD_DIR / "build-summary.md"
    summary_path.write_text(
        "# ProdAgentCo Build Summary\n\n"
        "## Deliverables\n"
        "- [Codebase](codebase.md)\n"
        "- [QA Report](qa-report.md)\n"
        "- [Security Report](security-report.md)\n\n"
        f"## Final Agent Output\n{result}\n"
    )

    print(f"\n✅ Build complete. 3 deliverables saved to {BUILD_DIR}/")

    # Auto-commit and push
    _commit_and_push()

    # Fire Gate 3 HITL notification
    print("📱 Firing Gate 3 notification...")
    gate3_notify(BUILD_DIR)

    return result


def _commit_and_push():
    """Commit and push build outputs to GitHub."""
    try:
        subprocess.run(['git', 'add', 'outputs/build/'], check=True, capture_output=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subprocess.run(
            ['git', 'commit', '-m', f'Build phase complete — {timestamp}'],
            check=True, capture_output=True
        )
        subprocess.run(['git', 'push'], check=True, capture_output=True)
        print("📤 Build outputs committed and pushed to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
