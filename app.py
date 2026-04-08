"""
AI Delivery Risk Copilot - Version 2
Improved version with validation, logging, docstrings, and better error handling.
"""

import os
import json
import logging
from datetime import datetime
import streamlit as st

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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

DOMAINS = ["Banking", "Fintech", "Infrastructure", "Cloud", "Security", "AI Platform", "Healthcare", "Retail"]

STAKEHOLDER_OPTIONS = ["Green", "Amber", "Red"]
TESTING_OPTIONS = ["Yes", "No"]

# ============================================================================
# INPUT VALIDATION
# ============================================================================

def validate_project_data(data: dict) -> tuple[bool, str]:
"""
Validate input data before processing.

Args:
data (dict): Input data dictionary containing project metrics

Returns:
tuple: (is_valid: bool, error_message: str)

Examples:
>>> is_valid, msg = validate_project_data({"project_name": "", ...})
>>> is_valid
False
"""
try:
# Validate project name
if not data.get("project_name", "").strip():
return False, "Project name cannot be empty"

# Validate progress percentage
if not (0 <= data.get("progress", 0) <= 100):
return False, "Progress must be between 0-100%"

# Validate budget utilization
if data.get("budget_utilization", 0) < 0:
return False, "Budget utilization cannot be negative"

# Validate domain
if data.get("domain") not in DOMAINS:
return False, f"Domain must be one of {DOMAINS}"

# Validate stakeholder status
if data.get("stakeholder_status") not in STAKEHOLDER_OPTIONS:
return False, f"Stakeholder status must be one of {STAKEHOLDER_OPTIONS}"

# Validate testing readiness
if data.get("testing_readiness") not in TESTING_OPTIONS:
return False, f"Testing readiness must be one of {TESTING_OPTIONS}"

# Validate risk counts
if data.get("risks_count", 0) < 0 or data.get("risks_count", 0) > 50:
return False, "Risks count must be between 0-50"

if data.get("blockers_count", 0) < 0 or data.get("blockers_count", 0) > 50:
return False, "Blockers count must be between 0-50"

if data.get("scope_changes", 0) < 0 or data.get("scope_changes", 0) > 50:
return False, "Scope changes must be between 0-50"

# Validate go-live date
go_live = datetime.fromisoformat(str(data.get("go_live_date")))
if go_live.date() < datetime.now().date():
return False, "Go-live date cannot be in the past"

logger.info("✅ All input validation passed")
return True, ""

except Exception as e:
error_msg = f"Validation error: {str(e)}"
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
thresholds: dict = None
) -> int:
"""
Calculate delivery risk score based on project metrics.

Uses a weighted scoring model where higher scores indicate higher risk.

Args:
progress (int): Delivery progress percentage (0-100)
budget_util (int): Budget utilization percentage (0-120+)
risks_count (int): Number of open risks (0-50+)
blockers_count (int): Number of open blockers (0-50+)
scope_changes (int): Number of scope changes (0-50+)
testing_ready (str): Testing readiness ("Yes" or "No")
stakeholder_status (str): Stakeholder confidence ("Green", "Amber", "Red")
thresholds (dict, optional): Custom risk thresholds. Defaults to RISK_THRESHOLDS.

Returns:
int: Risk score (higher = more risk)

Examples:
>>> score_risk(55, 78, 4, 2, 2, "No", "Amber")
5
>>> score_risk(90, 50, 1, 0, 0, "Yes", "Green")
0
"""
if thresholds is None:
thresholds = RISK_THRESHOLDS

score = 0

# Progress scoring
if progress < thresholds["progress_critical"]:
score += 2
logger.debug(f"Progress {progress}% is critical (<{thresholds['progress_critical']}%)")
elif progress < thresholds["progress_warning"]:
score += 1
logger.debug(f"Progress {progress}% is warning (<{thresholds['progress_warning']}%)")

# Budget scoring
if budget_util > thresholds["budget_critical"]:
score += 2
logger.debug(f"Budget {budget_util}% is critical (>{thresholds['budget_critical']}%)")
elif budget_util > thresholds["budget_warning"]:
score += 1
logger.debug(f"Budget {budget_util}% is warning (>{thresholds['budget_warning']}%)")

# Risks scoring
if risks_count >= thresholds["risks_critical"]:
score += 2
logger.debug(f"Risks count {risks_count} is critical (>={thresholds['risks_critical']})")
elif risks_count >= thresholds["risks_warning"]:
score += 1
logger.debug(f"Risks count {risks_count} is warning (>={thresholds['risks_warning']})")

# Blockers scoring
if blockers_count >= thresholds["blockers_critical"]:
score += 2
logger.debug(f"Blockers {blockers_count} is critical (>={thresholds['blockers_critical']})")
elif blockers_count >= thresholds["blockers_warning"]:
score += 1
logger.debug(f"Blockers {blockers_count} is warning (>={thresholds['blockers_warning']})")

# Scope changes scoring
if scope_changes >= thresholds["scope_changes_critical"]:
score += 2
logger.debug(f"Scope changes {scope_changes} is critical (>={thresholds['scope_changes_critical']})")
elif scope_changes >= thresholds["scope_changes_warning"]:
score += 1
logger.debug(f"Scope changes {scope_changes} is warning (>={thresholds['scope_changes_warning']})")

# Testing readiness scoring
if testing_ready == "No":
score += 1
logger.debug("Testing readiness is 'No' - risk added")

# Stakeholder status scoring
if stakeholder_status == "Red":
score += 2
logger.debug("Stakeholder status is Red - high risk")
elif stakeholder_status == "Amber":
score += 1
logger.debug("Stakeholder status is Amber - moderate risk")

logger.info(f"Risk score calculated: {score}")
return score

def band(score: int) -> str:
"""
Convert risk score to risk band (Low, Medium, High).

Args:
score (int): Risk score from score_risk()

Returns:
str: Risk band ("Low", "Medium", or "High")

Examples:
>>> band(9)
'High'
>>> band(5)
'Medium'
>>> band(1)
'Low'
"""
if score >= RISK_BANDS["high"]:
return "High"
if score >= RISK_BANDS["medium"]:
return "Medium"
return "Low"

def recommendation(score: int) -> list:
"""
Generate recommended actions based on risk score.

Args:
score (int): Risk score from score_risk()

Returns:
list: List of recommended actions

Examples:
>>> recommendation(9)
['Run an executive risk review within 24 hours', ...]
"""
if score >= RISK_BANDS["high"]:
actions = [
"🔴 Run an executive risk review within 24 hours",
"🔴 Freeze non-critical scope changes",
"🔴 Assign owners and due dates for top 3 blockers",
"🔴 Issue a decision paper with options, impacts, and recommendation",
]
elif score >= RISK_BANDS["medium"]:
actions = [
"🟡 Increase governance cadence to twice weekly",
"🟡 Re-baseline milestone dates and dependencies",
"🟡 Convert open issues into action-owned mitigation items",
"🟡 Validate testing readiness and cutover criteria",
]
else:
actions = [
"🟢 Maintain weekly governance",
"🟢 Continue proactive RAID tracking",
"🟢 Confirm milestone readiness with delivery leads",
"🟢 Keep stakeholder communication concise and data-driven",
]

logger.info(f"Generated {len(actions)} recommendations for score {score}")
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
top_risk: str
) -> str:
"""
Generate executive summary for CXO stakeholders.

Args:
project_name (str): Name of the project
domain (str): Project domain/vertical
progress (int): Delivery progress percentage
budget_util (int): Budget utilization percentage
risk_band (str): Risk band (Low/Medium/High)
go_live_date (str): Target go-live date
top_risk (str): Most pressing delivery concern

Returns:
str: Formatted executive summary
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

def build_raid_items(risks_text: str, blockers_text: str, team_members: list = None) -> list:
"""
Generate RAID register items from risks and blockers.

Args:
risks_text (str): Multi-line text of risks
blockers_text (str): Multi-line text of blockers
team_members (list, optional): List of team member names for ownership

Returns:
list: List of RAID items (dict format)

Examples:
>>> build_raid_items("- Risk A\n- Risk B", "- Blocker 1")
[{'type': 'Risk', 'title': 'Risk A', ...}, ...]
"""
# Parse risks and blockers
risk_items = [r.strip("-• ").strip() for r in risks_text.splitlines() if r.strip()]
blocker_items = [b.strip("-• ").strip() for b in blockers_text.splitlines() if b.strip()]

if not risk_items and not blocker_items:
logger.warning("No risks or blockers provided")
return []

# Default team members if not provided
if team_members is None:
team_members = ["TBD"] * 6

raid = []

# Add risk items (top 3)
for i, item in enumerate(risk_items[:3], start=1):
owner = team_members[i-1] if i-1 < len(team_members) else "TBD"
raid.append({
"type": "Risk",
"title": item,
"owner": owner,
"mitigation": "Review impact, define workaround, and track in governance",
"due_date": "This week",
"priority": "High" if i == 1 else "Medium"
})

# Add blocker items (top 3)
for i, item in enumerate(blocker_items[:3], start=1):
owner = team_members[3 + i-1] if 3 + i-1 < len(team_members) else "TBD"
raid.append({
"type": "Issue",
"title": item,
"owner": owner,
"mitigation": "Escalate dependency and secure decision or resource support",
"due_date": "Immediate",
"priority": "Critical" if i == 1 else "High"
})

logger.info(f"Generated {len(raid)} RAID items ({len(risk_items)} risks, {len(blocker_items)} blockers)")
return raid

# ============================================================================
# LOCAL ANALYSIS ENGINE
# ============================================================================

def generate_local_analysis(data: dict, thresholds: dict = None) -> dict:
"""
Generate complete local analysis without LLM.

Args:
data (dict): Input data dictionary
thresholds (dict, optional): Custom risk thresholds

Returns:
dict: Analysis results with risk score, band, summary, actions, and RAID items

Raises:
ValueError: If input data is invalid
"""
logger.info("Starting local analysis generation")

# Validate data
is_valid, error_msg = validate_project_data(data)
if not is_valid:
raise ValueError(error_msg)

if thresholds is None:
thresholds = RISK_THRESHOLDS

# Calculate risk score
risk_score = score_risk(
data["progress"],
data["budget_utilization"],
data["risks_count"],
data["blockers_count"],
data["scope_changes"],
data["testing_readiness"],
data["stakeholder_status"],
thresholds
)

risk_band = band(risk_score)
actions = recommendation(risk_score)
top_risk = data["top_risk"].strip() if data["top_risk"].strip() else "Dependency and schedule slippage"

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
"analysis_timestamp": datetime.utcnow().isoformat() + "Z"
}

logger.info("Local analysis completed successfully")
return result

# ============================================================================
# LLM INTEGRATION
# ============================================================================

def call_openai_if_configured(data: dict, local_result: dict) -> dict:
"""
Call OpenAI API if configured via environment variables.

Args:
data (dict): Original input data
local_result (dict): Local analysis results

Returns:
dict: LLM response with CXO update, risks, and actions.
Returns None if API key not configured.
Returns dict with 'error' key if API call fails.

Note:
Requires OPENAI_API_KEY environment variable.
Optional MODEL_NAME environment variable (defaults to gpt-4o-mini).
"""
api_key = os.getenv("OPENAI_API_KEY", "").strip()
model = os.getenv("MODEL_NAME", "gpt-4o-mini").strip()

if not api_key:
logger.info("OPENAI_API_KEY not configured, skipping LLM enhancement")
return None

try:
logger.info(f"Calling OpenAI API with model: {model}")
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
{{"role": "system", "content": "You are a concise enterprise delivery advisor. Always respond with valid JSON."}},
{{"role": "user", "content": prompt}},
],
temperature=0.2,
max_tokens=1000,
)

content = response.choices[0].message.content
result = json.loads(content)
logger.info("LLM call successful")
return result

except ImportError:
logger.error("OpenAI library not installed. Run: pip install openai")
return {"error": "OpenAI library not installed. Install with: pip install openai"}
except json.JSONDecodeError as e:
logger.error(f"LLM response was not valid JSON: {e}")
return {"error": f"LLM response parsing failed: {str(e)}"}
except Exception as e:
logger.error(f"LLM API call failed: {e}")
return {"error": str(e)}

# ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
"""Main Streamlit application entry point."""

# Page configuration
st.set_page_config(
page_title="AI Delivery Risk Copilot",
page_icon="📈",
layout="wide",
initial_sidebar_state="expanded"
)

# Header
st.title("📈 AI Delivery Risk Copilot")
st.caption("Interview-ready demo for Senior Delivery Manager roles (v2 - Enhanced)")

# Sidebar information
with st.sidebar:
st.header("ℹ️ About this app")
st.write(
"This app simulates how an SDM (Senior Delivery Manager) can use AI to turn raw project signals into "
"an executive summary, risk view, and action plan."
)
st.write("**Features:**")
st.write("- ✅ Works locally without an API key")
st.write("- ✅ Optional LLM enhancement with OpenAI")
st.write("- ✅ Input validation and error handling")
st.write("- ✅ Configurable risk thresholds")
st.write("- ✅ RAID register generation")

st.divider()
st.subheader("📋 How to use")
st.write("1. Fill in project metrics on the left")
st.write("2. Click 'Generate Delivery Insight'")
st.write("3. Review risk analysis and recommendations")
st.write("4. Download analysis as JSON for reports")

st.divider()
st.subheader("🔑 LLM Configuration (Optional)")
st.write("Set these environment variables to enable AI enhancement:")
st.code("export OPENAI_API_KEY='your-key-here'\nexport MODEL_NAME='gpt-4o-mini'", language="bash")

# Input columns
col1, col2 = st.columns(2)

with col1:
st.subheader("📊 Project Basics")
project_name = st.text_input("Project name *", value="Enterprise Cloud Migration", key="project_name")
domain = st.selectbox("Domain *", DOMAINS, key="domain")
progress = st.slider("Delivery progress (%)", 0, 100, 55, key="progress")
budget_utilization = st.slider("Budget utilized (%)", 0, 150, 78, key="budget")
go_live_date = st.date_input("Target go-live date *", key="go_live_date")

st.subheader("👥 Stakeholder Status")
stakeholder_status = st.selectbox("Stakeholder confidence *", STAKEHOLDER_OPTIONS, key="stakeholder")
testing_readiness = st.selectbox("Testing readiness *", TESTING_OPTIONS, key="testing")

with col2:
st.subheader("⚠️ Risk Indicators")
risks_count = st.number_input("Open risks", 0, 50, 4, key="risks_count")
blockers_count = st.number_input("Open blockers", 0, 50, 2, key="blockers_count")
scope_changes = st.number_input("Scope changes", 0, 50, 2, key="scope_changes")
top_risk = st.text_input(
"Top delivery risk *",
value="Dependency on vendor firewall changes",
key="top_risk"
)

st.subheader("📝 Detailed Issues")
risks_text = st.text_area(
"Key risks (one per line) *",
value="- Vendor delivery delay\n- Test environment instability\n- Scope creep from late change requests",
height=130,
key="risks_text"
)
blockers_text = st.text_area(
"Current blockers (one per line) *",
value="- Firewall approval pending\n- UAT sign-off delayed",
height=100,
key="blockers_text"
)

# Prepare data
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

# Generate insights button
if st.button("🚀 Generate Delivery Insight", type="primary", use_container_width=True):
try:
# Generate local analysis
with st.spinner("Analyzing project health..."):
local_result = generate_local_analysis(data)

# Call LLM if configured
llm_result = None
with st.spinner("Enhancing with AI insights..."):
llm_result = call_openai_if_configured(data, local_result)

# Display metrics
st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.metric("Risk Score", f"{local_result['risk_score']}/10", delta="Assessment")
m2.metric("Risk Band", local_result["risk_band"], delta=None)
m3.metric("Progress", f"{data['progress']}%", delta=f"{100-data['progress']}% remaining")
m4.metric("Budget Used", f"{data['budget_utilization']}%", delta=None)

# Executive Summary
st.subheader("📋 Executive Summary")
st.info(local_result["executive_summary"])

# Recommended Actions
st.subheader("✅ Recommended Actions")
for action in local_result["recommended_actions"]:
st.write(action)

# RAID Register
st.subheader("🛡️ Draft RAID Register")
if local_result["raid_register"]:
st.dataframe(
local_result["raid_register"],
use_container_width=True,
hide_index=True
)
else:
st.warning("No risks or blockers provided for RAID register")

# LLM Enhancement
if llm_result:
st.divider()
st.subheader("🤖 AI Enhancement (LLM)")

if "error" in llm_result:
st.warning(f"⚠️ LLM call failed: {llm_result['error']}")
else:
# CXO Update
st.write("**CXO Update:**")
st.write(llm_result.get("cxo_update", ""))

# Top 3 Risks
st.write("**Top 3 Risks:**")
for item in llm_result.get("top_3_risks", []):
st.write(f"- {item}")

# Top 3 Actions
st.write("**Top 3 Actions:**")
for item in llm_result.get("top_3_actions", []):
st.write(f"- {item}")

# Confidence Level
confidence = llm_result.get("confidence_level", "Unknown")
st.write(f"**LLM Confidence Level:** {confidence}")

# Export payload
st.divider()
export_payload = {
"input": data,
"local_result": local_result,
"llm_result": llm_result,
}

try:
st.download_button(
label="📥 Download analysis as JSON",
data=json.dumps(export_payload, indent=2),
file_name=f"delivery_risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
mime="application/json",
use_container_width=True
)
except Exception as e:
st.error(f"Failed to prepare download: {str(e)}")
logger.error(f"Download button error: {e}")

except ValueError as e:
st.error(f"❌ Input validation failed: {str(e)}")
logger.error(f"Validation error: {e}")
except Exception as e:
st.error(f"❌ Analysis failed: {str(e)}")
logger.error(f"Unexpected error during analysis: {e}")

# Footer information
st.divider()
st.subheader("💡 Interview Talking Points")
st.write(
"""
**Problem:** Delivery managers spend hours on manual risk assessment and reporting.

**Solution:** This app automates the conversion of project signals into executive-ready insights.

**Key Features:**
- Local-first analysis (no API required)
- Optional LLM enhancement for CXO communications
- RAID register auto-generation
- Configurable risk thresholds for different project types

**Scalability Path:**
- Portfolio view across multiple projects
- Jira/Excel integration for real-time data
- PDF export for steering committee packs
- Database storage for historical trends
"""
)

if __name__ == "__main__":
main()
