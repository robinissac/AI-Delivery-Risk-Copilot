 from pathlib import Path

clean_code = r'''"""
AI Delivery Risk Copilot - Version 2
Improved version with validation, logging, docstrings, and better error handling.
"""

import json
import logging
import os
from datetime import datetime, date
from typing import Any

import streamlit as st

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

RISK_THRESHOLDS = {
    "progress_critical": 40,
    "progress_warning": 70,
    "budget_critical": 90,
    "budget_warning": 75,
    "risks_critical": 5,
    "risks_warning": 3,
    "blockers_critical": 3,
    "blockers_warning": 1,
    "scope_changes_critical": 3,
    "scope_changes_warning": 1,
}

RISK_BANDS = {
    "high": 8,
    "medium": 4,
    "low": 0,
}

DOMAINS = [
    "Banking",
    "Fintech",
    "Infrastructure",
    "Cloud",
    "Security",
    "AI Platform",
    "Healthcare",
    "Retail",
]

STAKEHOLDER_OPTIONS = ["Green", "Amber", "Red"]
TESTING_OPTIONS = ["Yes", "No"]

# ============================================================================
# INPUT VALIDATION
# ============================================================================


def validate_project_data(data: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate input data before processing.

    Args:
        data: Input data dictionary containing project metrics.

    Returns:
        Tuple of (is_valid, error_message).
    """
    try:
        if not data.get("project_name", "").strip():
            return False, "Project name cannot be empty"

        if not (0 <= data.get("progress", 0) <= 100):
            return False, "Progress must be between 0 and 100"

        if data.get("budget_utilization", 0) < 0:
            return False, "Budget utilization cannot be negative"

        if data.get("domain") not in DOMAINS:
            return False, f"Domain must be one of {DOMAINS}"

        if data.get("stakeholder_status") not in STAKEHOLDER_OPTIONS:
            return False, f"Stakeholder status must be one of {STAKEHOLDER_OPTIONS}"

        if data.get("testing_readiness") not in TESTING_OPTIONS:
            return False, f"Testing readiness must be one of {TESTING_OPTIONS}"

        if not (0 <= data.get("risks_count", 0) <= 50):
            return False, "Risks count must be between 0 and 50"

        if not (0 <= data.get("blockers_count", 0) <= 50):
            return False, "Blockers count must be between 0 and 50"

        if not (0 <= data.get("scope_changes", 0) <= 50):
            return False, "Scope changes must be between 0 and 50"

        go_live_raw = data.get("go_live_date")
        if not go_live_raw:
            return False, "Go-live date is required"

        go_live = datetime.fromisoformat(str(go_live_raw)).date()
        if go_live < date.today():
            return False, "Go-live date cannot be in the past"

        logger.info("All input validation passed")
        return True, ""

    except Exception as exc:
        error_msg = f"Validation error: {exc}"
        logger.error(error_msg)
        return False, error_msg


# ============================================================================
# RISK SCORING ENGINE
# ============================================================================


def score_risk(
    progress: int,
    budget_util: int,
    risks_count: int,
    blockers_count: int,
    scope_changes: int,
    testing_ready: str,
    stakeholder_status: str,
    thresholds: dict[str, int] | None = None,
) -> int:
    """
    Calculate delivery risk score based on project metrics.
    """
    if thresholds is None:
        thresholds = RISK_THRESHOLDS

    score = 0

    if progress < thresholds["progress_critical"]:
        score += 2
        logger.debug("Progress %s%% is critical", progress)
    elif progress < thresholds["progress_warning"]:
        score += 1
        logger.debug("Progress %s%% is warning", progress)

    if budget_util > thresholds["budget_critical"]:
        score += 2
        logger.debug("Budget %s%% is critical", budget_util)
    elif budget_util > thresholds["budget_warning"]:
        score += 1
        logger.debug("Budget %s%% is warning", budget_util)

    if risks_count >= thresholds["risks_critical"]:
        score += 2
        logger.debug("Risks count %s is critical", risks_count)
    elif risks_count >= thresholds["risks_warning"]:
        score += 1
        logger.debug("Risks count %s is warning", risks_count)

    if blockers_count >= thresholds["blockers_critical"]:
        score += 2
        logger.debug("Blockers count %s is critical", blockers_count)
    elif blockers_count >= thresholds["blockers_warning"]:
        score += 1
        logger.debug("Blockers count %s is warning", blockers_count)

    if scope_changes >= thresholds["scope_changes_critical"]:
        score += 2
        logger.debug("Scope changes %s is critical", scope_changes)
    elif scope_changes >= thresholds["scope_changes_warning"]:
        score += 1
        logger.debug("Scope changes %s is warning", scope_changes)

    if testing_ready == "No":
        score += 1
        logger.debug("Testing readiness is No")

    if stakeholder_status == "Red":
        score += 2
        logger.debug("Stakeholder status is Red")
    elif stakeholder_status == "Amber":
        score += 1
        logger.debug("Stakeholder status is Amber")

    logger.info("Risk score calculated: %s", score)
    return score


def band(score: int) -> str:
    """
    Convert risk score to risk band.
    """
    if score >= RISK_BANDS["high"]:
        return "High"
    if score >= RISK_BANDS["medium"]:
        return "Medium"
    return "Low"


def recommendation(score: int) -> list[str]:
    """
    Generate recommended actions based on risk score.
    """
    if score >= RISK_BANDS["high"]:
        actions = [
            "Run an executive risk review within 24 hours",
            "Freeze non-critical scope changes",
            "Assign owners and due dates for top 3 blockers",
            "Issue a decision paper with options, impacts, and recommendation",
        ]
    elif score >= RISK_BANDS["medium"]:
        actions = [
            "Increase governance cadence to twice weekly",
            "Re-baseline milestone dates and dependencies",
            "Convert open issues into action-owned mitigation items",
            "Validate testing readiness and cutover criteria",
        ]
    else:
        actions = [
            "Maintain weekly governance",
            "Continue proactive RAID tracking",
            "Confirm milestone readiness with delivery leads",
            "Keep stakeholder communication concise and data-driven",
        ]

    logger.info("Generated %s recommendations for score %s", len(actions), score)
    return actions


# ============================================================================
# EXECUTIVE SUMMARY & RAID GENERATION
# ============================================================================


def build_exec_summary(
    project_name: str,
    domain: str,
    progress: int,
    budget_util: int,
    risk_band: str,
    go_live_date: str,
    top_risk: str,
) -> str:
    """
    Generate executive summary for CXO stakeholders.
    """
    summary = f"""
Project: {project_name}
Domain: {domain}
Overall risk is currently assessed as {risk_band}.
Delivery progress is {progress}% with budget utilization at {budget_util}%.
Current target go-live date is {go_live_date}.
Most pressing delivery concern: {top_risk}

Executive view:
The project requires focused attention on schedule health, risk ownership, and stakeholder alignment.
Recommended next step is to drive a leadership review on top delivery risks and confirm mitigation owners with dates.
""".strip()

    logger.info("Executive summary generated")
    return summary


def build_raid_items(
    risks_text: str,
    blockers_text: str,
    team_members: list[str] | None = None,
) -> list[dict[str, str]]:
    """
    Generate RAID register items from risks and blockers.
    """
    risk_items = [r.strip("-• ").strip() for r in risks_text.splitlines() if r.strip()]
    blocker_items = [b.strip("-• ").strip() for b in blockers_text.splitlines() if b.strip()]

    if not risk_items and not blocker_items:
        logger.warning("No risks or blockers provided")
        return []

    if team_members is None:
        team_members = ["TBD"] * 6

    raid: list[dict[str, str]] = []

    for i, item in enumerate(risk_items[:3], start=1):
        owner = team_members[i - 1] if i - 1 < len(team_members) else "TBD"
        raid.append(
            {
                "type": "Risk",
                "title": item,
                "owner": owner,
                "mitigation": "Review impact, define workaround, and track in governance",
                "due_date": "This week",
                "priority": "High" if i == 1 else "Medium",
            }
        )

    for i, item in enumerate(blocker_items[:3], start=1):
        idx = 3 + i - 1
        owner = team_members[idx] if idx < len(team_members) else "TBD"
        raid.append(
            {
                "type": "Issue",
                "title": item,
                "owner": owner,
                "mitigation": "Escalate dependency and secure decision or resource support",
                "due_date": "Immediate",
                "priority": "Critical" if i == 1 else "High",
            }
        )

    logger.info(
        "Generated %s RAID items (%s risks, %s blockers)",
        len(raid),
        len(risk_items),
        len(blocker_items),
    )
    return raid


# ============================================================================
# LOCAL ANALYSIS ENGINE
# ============================================================================


def generate_local_analysis(
    data: dict[str, Any],
    thresholds: dict[str, int] | None = None,
) -> dict[str, Any]:
    """
    Generate complete local analysis without LLM.
    """
    logger.info("Starting local analysis generation")

    is_valid, error_msg = validate_project_data(data)
    if not is_valid:
        raise ValueError(error_msg)

    if thresholds is None:
        thresholds = RISK_THRESHOLDS

    risk_score = score_risk(
        data["progress"],
        data["budget_utilization"],
        data["risks_count"],
        data["blockers_count"],
        data["scope_changes"],
        data["testing_readiness"],
        data["stakeholder_status"],
        thresholds,
    )

    risk_band = band(risk_score)
    actions = recommendation(risk_score)
    top_risk = (
        data["top_risk"].strip()
        if data["top_risk"].strip()
        else "Dependency and schedule slippage"
    )

    summary = build_exec_summary(
        data["project_name"],
        data["domain"],
        data["progress"],
        data["budget_utilization"],
        risk_band,
        data["go_live_date"],
        top_risk,
    )

    raid = build_raid_items(data["risks_text"], data["blockers_text"])

    result = {
        "risk_score": risk_score,
        "risk_band": risk_band,
        "executive_summary": summary,
        "recommended_actions": actions,
        "raid_register": raid,
        "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    logger.info("Local analysis completed successfully")
    return result


# ============================================================================
# LLM INTEGRATION
# ============================================================================


def call_openai_if_configured(
    data: dict[str, Any],
    local_result: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Call OpenAI API if configured via environment variables.

    Requires OPENAI_API_KEY.
    Optional MODEL_NAME defaults to gpt-4o-mini.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("MODEL_NAME", "gpt-4o-mini").strip()

    if not api_key:
        logger.info("OPENAI_API_KEY not configured, skipping LLM enhancement")
        return None

    try:
        logger.info("Calling OpenAI API with model: %s", model)
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        prompt = f"""
You are a senior delivery management copilot for banking and enterprise transformation programs.

Project data:
{json.dumps(data, indent=2)}

Local risk engine output:
{json.dumps(local_result, indent=2)}

Return a JSON response with these exact keys:
{{
  "executive_summary": "2-3 sentence CXO-ready summary",
  "cxo_update": "One paragraph update suitable for steering committee",
  "top_3_risks": ["Risk 1 with mitigation", "Risk 2 with mitigation", "Risk 3 with mitigation"],
  "top_3_actions": ["Action 1 with owner", "Action 2 with owner", "Action 3 with owner"],
  "confidence_level": "High/Medium/Low based on data quality"
}}

Rules:
- Keep the language suitable for CXO stakeholders.
- Be concise, direct, and business-focused.
- Do not invent metrics not present in the input.
- Mention operational continuity if relevant.
- Return valid JSON only.
"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise enterprise delivery advisor. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1000,
        )

        content = response.choices[0].message.content or "{}"
        result = json.loads(content)
        logger.info("LLM call successful")
        return result

    except ImportError:
        logger.error("OpenAI library not installed. Run: pip install openai")
        return {"error": "OpenAI library not installed. Install with: pip install openai"}
    except json.JSONDecodeError as exc:
        logger.error("LLM response was not valid JSON: %s", exc)
        return {"error": f"LLM response parsing failed: {exc}"}
    except Exception as exc:
        logger.error("LLM API call failed: %s", exc)
        return {"error": str(exc)}


# ============================================================================
# STREAMLIT UI
# ============================================================================


def main() -> None:
    """
    Main Streamlit application entry point.
    """
    st.set_page_config(
        page_title="AI Delivery Risk Copilot",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("📈 AI Delivery Risk Copilot")
    st.caption("Interview-ready demo for Senior Delivery Manager roles, v2 enhanced")

    with st.sidebar:
        st.header("About this app")
        st.write(
            "This app simulates how a Senior Delivery Manager can turn raw project signals "
            "into an executive summary, risk view, and action plan."
        )
        st.write("**Features:**")
        st.write("- Works locally without an API key")
        st.write("- Optional LLM enhancement with OpenAI")
        st.write("- Input validation and error handling")
        st.write("- Configurable risk thresholds")
        st.write("- RAID register generation")

        st.divider()
        st.subheader("How to use")
        st.write("1. Fill in project metrics on the left")
        st.write("2. Click Generate Delivery Insight")
        st.write("3. Review risk analysis and recommendations")
        st.write("4. Download analysis as JSON for reports")

        st.divider()
        st.subheader("LLM Configuration, optional")
        st.write("Set these environment variables to enable AI enhancement:")
        st.code(
            "export OPENAI_API_KEY='your-key-here'\nexport MODEL_NAME='gpt-4o-mini'",
            language="bash",
        )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Project Basics")
        project_name = st.text_input(
            "Project name *",
            value="Enterprise Cloud Migration",
            key="project_name",
        )
        domain = st.selectbox("Domain *", DOMAINS, key="domain")
        progress = st.slider("Delivery progress (%)", 0, 100, 55, key="progress")
        budget_utilization = st.slider("Budget utilized (%)", 0, 150, 78, key="budget")
        go_live_date = st.date_input("Target go-live date *", key="go_live_date")

        st.subheader("Stakeholder Status")
        stakeholder_status = st.selectbox(
            "Stakeholder confidence *",
            STAKEHOLDER_OPTIONS,
            key="stakeholder",
        )
        testing_readiness = st.selectbox(
            "Testing readiness *",
            TESTING_OPTIONS,
            key="testing",
        )

    with col2:
        st.subheader("Risk Indicators")
        risks_count = st.number_input("Open risks", 0, 50, 4, key="risks_count")
        blockers_count = st.number_input("Open blockers", 0, 50, 2, key="blockers_count")
        scope_changes = st.number_input("Scope changes", 0, 50, 2, key="scope_changes")
        top_risk = st.text_input(
            "Top delivery risk *",
            value="Dependency on vendor firewall changes",
            key="top_risk",
        )

        st.subheader("Detailed Issues")
        risks_text = st.text_area(
            "Key risks, one per line *",
            value="- Vendor delivery delay\n- Test environment instability\n- Scope creep from late change requests",
            height=130,
            key="risks_text",
        )
        blockers_text = st.text_area(
            "Current blockers, one per line *",
            value="- Firewall approval pending\n- UAT sign-off delayed",
            height=100,
            key="blockers_text",
        )

    data = {
        "project_name": project_name,
        "domain": domain,
        "progress": int(progress),
        "budget_utilization": int(budget_utilization),
        "go_live_date": str(go_live_date),
        "stakeholder_status": stakeholder_status,
        "testing_readiness": testing_readiness,
        "risks_count": int(risks_count),
        "blockers_count": int(blockers_count),
        "scope_changes": int(scope_changes),
        "top_risk": top_risk,
        "risks_text": risks_text,
        "blockers_text": blockers_text,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    if st.button("🚀 Generate Delivery Insight", type="primary", use_container_width=True):
        try:
            with st.spinner("Analyzing project health..."):
                local_result = generate_local_analysis(data)

            llm_result = None
            with st.spinner("Enhancing with AI insights..."):
                llm_result = call_openai_if_configured(data, local_result)

            st.divider()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Risk Score", f"{local_result['risk_score']}/10", delta="Assessment")
            m2.metric("Risk Band", local_result["risk_band"])
            m3.metric("Progress", f"{data['progress']}%", delta=f"{100 - data['progress']}% remaining")
            m4.metric("Budget Used", f"{data['budget_utilization']}%")

            st.subheader("Executive Summary")
            st.info(local_result["executive_summary"])

            st.subheader("Recommended Actions")
            for action in local_result["recommended_actions"]:
                st.write(f"- {action}")

            st.subheader("Draft RAID Register")
            if local_result["raid_register"]:
                st.dataframe(
                    local_result["raid_register"],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.warning("No risks or blockers provided for RAID register")

            if llm_result:
                st.divider()
                st.subheader("AI Enhancement, LLM")

                if "error" in llm_result:
                    st.warning(f"LLM call failed: {llm_result['error']}")
                else:
                    st.write("**CXO Update:**")
                    st.write(llm_result.get("cxo_update", ""))

                    st.write("**Top 3 Risks:**")
                    for item in llm_result.get("top_3_risks", []):
                        st.write(f"- {item}")

                    st.write("**Top 3 Actions:**")
                    for item in llm_result.get("top_3_actions", []):
                        st.write(f"- {item}")

                    confidence = llm_result.get("confidence_level", "Unknown")
                    st.write(f"**LLM Confidence Level:** {confidence}")

            st.divider()
            export_payload = {
                "input": data,
                "local_result": local_result,
                "llm_result": llm_result,
            }

            st.download_button(
                label="📥 Download analysis as JSON",
                data=json.dumps(export_payload, indent=2),
                file_name=f"delivery_risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )

        except ValueError as exc:
            st.error(f"Input validation failed: {exc}")
            logger.error("Validation error: %s", exc)
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
            logger.error("Unexpected error during analysis: %s", exc)

    st.divider()
    st.subheader("Interview Talking Points")
    st.write(
        """
**Problem:** Delivery managers spend hours on manual risk assessment and reporting.

**Solution:** This app automates the conversion of project signals into executive-ready insights.

**Key Features:**
- Local-first analysis, no API required
- Optional LLM enhancement for CXO communications
- RAID register auto-generation
- Configurable risk thresholds for different project types

**Scalability Path:**
- Portfolio view across multiple projects
- Jira or Excel integration for real-time data
- PDF export for steering committee packs
- Database storage for historical trends
"""
    )


if __name__ == "__main__":
    main()
'''

requirements = "streamlit\nopenai\n"

base = Path("/mnt/data")
(base / "app_fixed.py").write_text(clean_code, encoding="utf-8")
(base / "requirements_fixed.txt").write_text(requirements, encoding="utf-8")
print("/mnt/data/app_fixed.py")
print("/mnt/data/requirements_fixed.txt")
