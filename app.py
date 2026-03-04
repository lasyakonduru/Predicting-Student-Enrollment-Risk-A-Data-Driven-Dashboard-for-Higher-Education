import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64

# -----------------------------
# Paths
# -----------------------------
DATA_PATH = "C:\ASSIGNMENTS\project\student_retention_final.csv"
LOGO_PATH = "C:\ASSIGNMENTS\project\slu.png"  # change to "slu.png" if running locally

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Enrollment & Early Retention Risk Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# CSS (PowerBI-like blue theme)
# -----------------------------
CSS = """
<style>
.stApp { background: #ffffff; }

.pb-header {
  background: #0B3CC1;
  padding: 16px 18px;
  border-radius: 10px;
  color: white;
  margin-bottom: 12px;
  position: relative;
}
.pb-title { font-size: 26px; font-weight: 800; letter-spacing: 0.5px; margin: 0; text-align:center; }
.pb-subtitle { font-size: 18px; font-weight: 500; opacity: 0.95; margin: 4px 0 0 0; text-align:center; }

.logo-wrap {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  display:flex;
  align-items:center;
  gap:10px;
}
.logo-img {
  height: 42px;
  border-radius: 6px;
  background: white;
  padding: 4px;
}

.kpi-card {
  border: 2px solid #0B3CC1;
  border-radius: 12px;
  padding: 14px 14px;
  margin-bottom: 12px;
  background: #ffffff;
}
.kpi-label {
  color: #0B3CC1;
  font-weight: 800;
  font-size: 14px;
  margin-bottom: 8px;
}
.kpi-value {
  color: #0B3CC1;
  font-weight: 900;
  font-size: 34px;
  line-height: 1;
}

.section-title {
  font-size: 16px;
  font-weight: 800;
  color: #111827;
  margin: 6px 0 6px 0;
}

.filter-panel {
  border: 2px solid #0B3CC1;
  border-radius: 12px;
  padding: 12px 12px;
  background: #ffffff;
}
.filter-title {
  color: #0B3CC1;
  font-weight: 900;
  font-size: 14px;
  margin-bottom: 8px;
}

.chart-box {
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 8px 10px;
  background: #ffffff;
}

.block-container { padding-top: 10px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # normalize expected binary columns
    for c in [
        "orientation_attended", "advisor_contacted", "support_program_used",
        "library_used", "study_group_participation", "integrity_policy_viewed",
        "enrolled", "retained_after_first_term", "assignments_submitted_first2weeks"
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    # normalize key columns if missing from synthetic data
    if "international" in df.columns:
        df["international"] = df["international"].astype(str).replace({"1": "Yes", "0": "No"}).replace({"True": "Yes", "False": "No"})

    return df

df = load_data(DATA_PATH)

# -----------------------------
# Logo base64
# -----------------------------
@st.cache_data
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

LOGO_B64 = img_to_base64(LOGO_PATH)

# -----------------------------
# Default filter state
# -----------------------------
def ensure_state():
    defaults = {
        "student_type": "All",
        "program": "All",
        "international": "All",
        "risk_level": "All",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ensure_state()

# -----------------------------
# Helpers
# -----------------------------
def format_pct(x: float) -> str:
    return f"{x:.0%}"

def apply_filters(df_in: pd.DataFrame) -> pd.DataFrame:
    out = df_in.copy()

    if st.session_state["student_type"] != "All" and "student_type" in out.columns:
        out = out[out["student_type"] == st.session_state["student_type"]]

    if st.session_state["program"] != "All" and "program" in out.columns:
        out = out[out["program"] == st.session_state["program"]]

    if st.session_state["international"] != "All" and "international" in out.columns:
        out = out[out["international"] == st.session_state["international"]]

    if st.session_state["risk_level"] != "All" and "risk_level" in out.columns:
        out = out[out["risk_level"] == st.session_state["risk_level"]]

    return out

def kpi_values(df_in: pd.DataFrame):
    total = len(df_in)
    enr_rate = df_in["enrolled"].mean() if total else 0.0
    ret_rate = df_in["retained_after_first_term"].mean() if total else 0.0
    high_pct = (df_in["risk_level"].eq("High").mean() if total and "risk_level" in df_in.columns else 0.0)
    avg_risk = df_in["risk_score"].mean() if total and "risk_score" in df_in.columns else 0.0
    return total, enr_rate, ret_rate, high_pct, avg_risk

def funnel_counts(df_in: pd.DataFrame):
    admitted = len(df_in)
    orientation = int(df_in["orientation_attended"].sum()) if "orientation_attended" in df_in.columns else 0
    enrolled = int(df_in["enrolled"].sum()) if "enrolled" in df_in.columns else 0
    retained = int(df_in["retained_after_first_term"].sum()) if "retained_after_first_term" in df_in.columns else 0
    return pd.DataFrame({
        "stage": ["Admitted", "Orientation", "Enrolled", "Retained"],
        "count": [admitted, orientation, enrolled, retained]
    })

# Risk rules (keep consistent for drilldown + what-if)
RISK_RULES = [
    ("Missed Orientation", lambda r: r.get("orientation_attended", 0) == 0, 20),
    ("No Advisor Contact", lambda r: r.get("advisor_contacted", 0) == 0, 15),
    ("No Support Program", lambda r: r.get("support_program_used", 0) == 0, 10),
    ("No Integrity Policy", lambda r: r.get("integrity_policy_viewed", 0) == 0, 10),
    ("No Library Usage", lambda r: r.get("library_used", 0) == 0, 5),
    ("No Study Group", lambda r: r.get("study_group_participation", 0) == 0, 5),
    ("Low First-Week Login", lambda r: r.get("first_week_login_count", 0) < 3, 10),
    ("No Assignments Submitted", lambda r: r.get("assignments_submitted_first2weeks", 0) == 0, 15),
]

def why_flagged(row: pd.Series):
    reasons = []
    for name, cond, pts in RISK_RULES:
        try:
            if cond(row):
                reasons.append(f"{name} (+{pts})")
        except Exception:
            pass
    return reasons

def recommended_action(row: pd.Series):
    actions = []
    if row.get("orientation_attended", 0) == 0:
        actions.append("Send orientation follow-up and offer the next session link.")
    if row.get("advisor_contacted", 0) == 0:
        actions.append("Schedule advising outreach within 48 hours and share booking link.")
    if row.get("support_program_used", 0) == 0:
        actions.append("Refer to support program (INTO / student success) and confirm next steps.")
    if row.get("first_week_login_count", 0) < 3:
        actions.append("Send LMS engagement reminder and check access issues.")
    if row.get("assignments_submitted_first2weeks", 0) == 0:
        actions.append("Nudge first-week deliverables and connect with academic support resources.")
    if not actions:
        actions.append("Maintain light-touch engagement and monitor weekly.")
    return " ".join(actions)

def top_risk_drivers(df_in: pd.DataFrame):
    # Rank drivers by counts among High risk cohort (most action-focused)
    if len(df_in) == 0 or "risk_level" not in df_in.columns:
        return pd.DataFrame({"driver": [], "count": []})
    high = df_in[df_in["risk_level"] == "High"].copy()
    rows = []
    for name, cond, _pts in RISK_RULES:
        cnt = int(high.apply(cond, axis=1).sum()) if len(high) else 0
        rows.append((name, cnt))
    out = pd.DataFrame(rows, columns=["driver", "count"]).sort_values("count", ascending=False)
    return out

def adjusted_risk_score(row: pd.Series, attend_orientation, contact_advisor, use_support, submit_assignment, boost_login):
    score = int(row.get("risk_score", 0))
    if attend_orientation and row.get("orientation_attended", 0) == 0:
        score -= 20
    if contact_advisor and row.get("advisor_contacted", 0) == 0:
        score -= 15
    if use_support and row.get("support_program_used", 0) == 0:
        score -= 10
    if submit_assignment and row.get("assignments_submitted_first2weeks", 0) == 0:
        score -= 15
    if boost_login and row.get("first_week_login_count", 0) < 3:
        score -= 10
    return max(score, 0)

def risk_level_from_score(score: int):
    if score <= 20:
        return "Low"
    elif score <= 50:
        return "Medium"
    return "High"

def prob_from_risk_level(level: str):
    # simple, explainable estimates (committee-friendly)
    if level == "Low":
        return 0.90, 0.85
    if level == "Medium":
        return 0.60, 0.60
    return 0.30, 0.30

# -----------------------------
# Right-side slicers (PowerBI-like)
# -----------------------------
def right_filters_panel(df_base: pd.DataFrame, container):
    with container:
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.markdown('<div class="filter-title">Filters</div>', unsafe_allow_html=True)

        # Options
        student_type_opt = ["All"] + (sorted(df_base["student_type"].dropna().unique().tolist()) if "student_type" in df_base.columns else [])
        program_opt = ["All"] + (sorted(df_base["program"].dropna().unique().tolist()) if "program" in df_base.columns else [])
        international_opt = ["All"] + (sorted(df_base["international"].dropna().unique().tolist()) if "international" in df_base.columns else ["Yes", "No"])
        risk_opt = ["All"] + (["Low", "Medium", "High"] if "risk_level" in df_base.columns else [])

        # Controls (keys make them persist across pages)
        st.session_state["student_type"] = st.selectbox("Student Type", student_type_opt, index=student_type_opt.index(st.session_state["student_type"]) if st.session_state["student_type"] in student_type_opt else 0, key="flt_student_type")
        st.session_state["program"] = st.selectbox("Program", program_opt, index=program_opt.index(st.session_state["program"]) if st.session_state["program"] in program_opt else 0, key="flt_program")
        st.session_state["international"] = st.selectbox("International", international_opt, index=international_opt.index(st.session_state["international"]) if st.session_state["international"] in international_opt else 0, key="flt_international")
        st.session_state["risk_level"] = st.selectbox("Risk Level", risk_opt, index=risk_opt.index(st.session_state["risk_level"]) if st.session_state["risk_level"] in risk_opt else 0, key="flt_risk")

        if st.button("Reset filters"):
            st.session_state["student_type"] = "All"
            st.session_state["program"] = "All"
            st.session_state["international"] = "All"
            st.session_state["risk_level"] = "All"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Sidebar (navigation only)
# -----------------------------
st.sidebar.image(LOGO_PATH, use_container_width=True)
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Executive Overview", "Drivers & Interventions", "Student Drilldown", "What-If Simulator"],
    label_visibility="collapsed"
)

# -----------------------------
# Header (logo + title)
# -----------------------------
st.markdown(
    f"""
    <div class="pb-header">
      <div class="logo-wrap">
        <img class="logo-img" src="data:image/png;base64,{LOGO_B64}" />
      </div>
      <p class="pb-title">ENROLLMENT &amp; EARLY RETENTION RISK DASHBOARD</p>
      <p class="pb-subtitle">{page}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Top-level layout: Left KPI rail | Center content | Right slicers
# -----------------------------
left, center, right = st.columns([1.05, 3.7, 1.25], gap="large")

# Apply filters based on current session_state
df_f = apply_filters(df)

# KPI rail
with left:
    total, enr_rate, ret_rate, high_pct, avg_risk = kpi_values(df_f)

    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-label">Total Applicants</div>
        <div class="kpi-value">{total}</div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-label">Enrollment Rate %</div>
        <div class="kpi-value">{format_pct(enr_rate)}</div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-label">First-Term Retention %</div>
        <div class="kpi-value">{format_pct(ret_rate)}</div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-label">High-Risk %</div>
        <div class="kpi-value">{format_pct(high_pct)}</div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-label">Avg Risk Score</div>
        <div class="kpi-value">{avg_risk:.2f}</div>
      </div>
    """, unsafe_allow_html=True)

    st.caption("Demo project for interview/portfolio purposes. Not an official SLU system.")

# Right slicers panel (PowerBI-style)
right_filters_panel(df, right)

# After filters might have changed, re-apply
df_f = apply_filters(df)

# -----------------------------
# Home
# -----------------------------
if page == "Home":
    with center:
        st.markdown('<div class="section-title">Purpose</div>', unsafe_allow_html=True)
        st.write(
            "This dashboard helps Admissions and Enrollment teams identify applicants who are at risk of not enrolling "
            "or not being retained after the first term. It turns early engagement signals into an explainable risk score "
            "so teams can prioritize outreach and support in a consistent way."
        )

        st.markdown('<div class="section-title">Why we created it</div>', unsafe_allow_html=True)
        st.write(
            "Admissions reporting often involves multiple systems and a lot of back-and-forth. This dashboard reduces that friction by:\n"
            "- defining clear metrics (yield, retention, risk score)\n"
            "- showing the funnel and drop-off points\n"
            "- highlighting the top drivers of risk\n"
            "- suggesting action steps for counselors and student success teams"
        )

        st.markdown('<div class="section-title">How we created it</div>', unsafe_allow_html=True)
        st.write(
            "1) Cleaned and standardized student engagement fields.\n"
            "2) Built a transparent risk score using weighted rules (orientation, advising, support use, LMS engagement).\n"
            "3) Validated the dashboard views by comparing risk against enrollment and first-term retention.\n"
            "4) Built interactive drilldowns and a What-If simulator to test interventions."
        )

        st.markdown('<div class="section-title">How to use it</div>', unsafe_allow_html=True)
        st.write(
            "- Use the right-side filters to focus on a cohort.\n"
            "- Start with **Executive Overview** for funnel health and rates.\n"
            "- Use **Drivers & Interventions** to see what’s driving risk and which supports correlate with retention.\n"
            "- Use **Student Drilldown** for an individual student view (why flagged + recommended action).\n"
            "- Use **What-If Simulator** to test interventions and see the risk reduction."
        )

        st.info(
            "This design is explainable and action-oriented. With real institutional data, "
            "we can productionize it with governance, security, and privacy controls."
        )

# -----------------------------
# Executive Overview
# -----------------------------
elif page == "Executive Overview":
    with center:
        r1c1, r1c2, r1c3 = st.columns([1.2, 1.3, 1.3], gap="large")

        with r1c1:
            st.markdown('<div class="section-title">Funnel Value by Stage</div>', unsafe_allow_html=True)
            f = funnel_counts(df_f)
            fig = px.funnel(f, x="count", y="stage")
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with r1c2:
            st.markdown('<div class="section-title">Retention Rate by Risk Level</div>', unsafe_allow_html=True)
            tmp = df_f.groupby("risk_level", as_index=False)["retained_after_first_term"].mean()
            order = ["Low", "Medium", "High"]
            tmp["risk_level"] = pd.Categorical(tmp["risk_level"], categories=order, ordered=True)
            tmp = tmp.sort_values("risk_level")
            fig = px.bar(tmp, x="risk_level", y="retained_after_first_term",
                         text=tmp["retained_after_first_term"].map(lambda v: f"{v:.0%}"))
            fig.update_yaxes(range=[0, 1])
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with r1c3:
            st.markdown('<div class="section-title">Enrollment Rate by Risk Level</div>', unsafe_allow_html=True)
            tmp = df_f.groupby("risk_level", as_index=False)["enrolled"].mean()
            order = ["Low", "Medium", "High"]
            tmp["risk_level"] = pd.Categorical(tmp["risk_level"], categories=order, ordered=True)
            tmp = tmp.sort_values("risk_level")
            fig = px.bar(tmp, x="risk_level", y="enrolled", text=tmp["enrolled"].map(lambda v: f"{v:.0%}"))
            fig.update_yaxes(range=[0, 1])
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        r2c1, r2c2, r2c3 = st.columns([1.2, 2.0, 1.2], gap="large")

        with r2c1:
            st.markdown('<div class="section-title">Student Risk Distribution</div>', unsafe_allow_html=True)
            pie = df_f["risk_level"].value_counts().reset_index()
            pie.columns = ["risk_level", "count"]
            fig = px.pie(pie, names="risk_level", values="count", hole=0.35)
            fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with r2c2:
            st.markdown('<div class="section-title">Top Risk Factors of Student Risk (High-Risk Only)</div>', unsafe_allow_html=True)
            drivers = top_risk_drivers(df_f).head(8)
            fig = px.bar(drivers, x="driver", y="count", text="count")
            fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
            fig.update_xaxes(tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

        with r2c3:
            st.markdown('<div class="section-title">Risk Score — International vs Domestic</div>', unsafe_allow_html=True)
            if "international" in df_f.columns:
                tmp = df_f.groupby("international", as_index=False)["risk_score"].mean()
                fig = px.bar(tmp, x="international", y="risk_score",
                             text=tmp["risk_score"].map(lambda v: f"{v:.2f}"))
                fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)

        st.info("Use the filters on the right to compare cohorts and watch how yield and retention change.")

# -----------------------------
# Drivers & Interventions
# -----------------------------
elif page == "Drivers & Interventions":
    with center:
        top_row = st.columns([1.2, 1.2, 1.2], gap="large")

        with top_row[0]:
            st.markdown('<div class="section-title">Orientation vs Retention</div>', unsafe_allow_html=True)
            tmp = df_f.groupby("orientation_attended", as_index=False)["retained_after_first_term"].mean()
            tmp["orientation_attended"] = tmp["orientation_attended"].map({0: "No", 1: "Yes"})
            fig = px.bar(tmp, x="orientation_attended", y="retained_after_first_term",
                         text=tmp["retained_after_first_term"].map(lambda v: f"{v:.0%}"))
            fig.update_yaxes(range=[0, 1])
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with top_row[1]:
            st.markdown('<div class="section-title">Support Program vs Retention</div>', unsafe_allow_html=True)
            tmp = df_f.groupby("support_program_used", as_index=False)["retained_after_first_term"].mean()
            tmp["support_program_used"] = tmp["support_program_used"].map({0: "No", 1: "Yes"})
            fig = px.bar(tmp, x="support_program_used", y="retained_after_first_term",
                         text=tmp["retained_after_first_term"].map(lambda v: f"{v:.0%}"))
            fig.update_yaxes(range=[0, 1])
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with top_row[2]:
            st.markdown('<div class="section-title">Advisor vs Retention</div>', unsafe_allow_html=True)
            tmp = df_f.groupby("advisor_contacted", as_index=False)["retained_after_first_term"].mean()
            tmp["advisor_contacted"] = tmp["advisor_contacted"].map({0: "No", 1: "Yes"})
            fig = px.bar(tmp, x="advisor_contacted", y="retained_after_first_term",
                         text=tmp["retained_after_first_term"].map(lambda v: f"{v:.0%}"))
            fig.update_yaxes(range=[0, 1])
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        mid = st.columns([1.6, 1.4], gap="large")

        with mid[0]:
            st.markdown('<div class="section-title">Driver Ranking Chart (Top Risk Drivers)</div>', unsafe_allow_html=True)
            drivers = top_risk_drivers(df_f).head(10)
            fig = px.bar(drivers, x="driver", y="count", text="count")
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
            fig.update_xaxes(tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

        with mid[1]:
            st.markdown('<div class="section-title">Login vs Risk</div>', unsafe_allow_html=True)
            if "first_week_login_count" in df_f.columns:
                fig = px.scatter(df_f, x="risk_score", y="first_week_login_count", hover_data=["student_id"])
                fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Column 'first_week_login_count' not found in dataset.")

        bottom = st.columns([1.2, 1.2], gap="large")

        with bottom[0]:
            st.markdown('<div class="section-title">International vs Retention</div>', unsafe_allow_html=True)
            if "international" in df_f.columns:
                tmp = df_f.groupby("international", as_index=False)["retained_after_first_term"].mean()
                fig = px.bar(tmp, x="international", y="retained_after_first_term",
                             text=tmp["retained_after_first_term"].map(lambda v: f"{v:.0%}"))
                fig.update_yaxes(range=[0, 1])
                fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)

        with bottom[1]:
            st.markdown('<div class="section-title">What this page helps you do</div>', unsafe_allow_html=True)
            st.write(
                "This page explains *why* students are flagged and which levers (orientation, advising, support programs, LMS engagement) "
                "are most associated with first-term retention. It helps teams prioritize interventions instead of guessing."
            )

# -----------------------------
# Student Drilldown
# -----------------------------
elif page == "Student Drilldown":
    with center:
        st.markdown('<div class="section-title">Student Drilldown</div>', unsafe_allow_html=True)
        st.write("Select a student to view risk reasons and a recommended action plan.")

        if "student_id" not in df_f.columns or len(df_f) == 0:
            st.warning("No students match the current filters.")
        else:
            ids = sorted(df_f["student_id"].astype(int).unique().tolist())
            selected_id = st.selectbox("Selected Student ID", ids, key="drill_student")

            row = df_f[df_f["student_id"].astype(int) == int(selected_id)].iloc[0]

            t1, t2, t3, t4, t5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.2], gap="large")
            t1.metric("Selected Risk Score", int(row.get("risk_score", 0)))
            t2.metric("Selected Risk Level", row.get("risk_level", "NA"))
            t3.metric("Selected Retained", "Yes" if row.get("retained_after_first_term", 0) == 1 else "No")
            t4.metric("Selected Enrolled", "Yes" if row.get("enrolled", 0) == 1 else "No")
            t5.metric("International", row.get("international", "NA"))

            reasons = why_flagged(row)
            st.markdown("**Why flagged**")
            st.write(" • " + " • ".join(reasons) if reasons else "No major risk flags detected.")

            st.markdown("**First recommended action**")
            st.write(recommended_action(row))

            st.markdown('<div class="section-title">Cohort snapshot (top 25 by risk)</div>', unsafe_allow_html=True)
            cols_show = [
                "student_id", "risk_score", "risk_level", "international",
                "orientation_attended", "advisor_contacted", "support_program_used",
                "first_week_login_count", "assignments_submitted_first2weeks",
                "enrolled", "retained_after_first_term"
            ]
            cols_show = [c for c in cols_show if c in df_f.columns]
            st.dataframe(df_f[cols_show].sort_values(["risk_score"], ascending=False).head(25), use_container_width=True)

# -----------------------------
# What-If Simulator
# -----------------------------
else:
    with center:
        st.markdown('<div class="section-title">What-If Simulator</div>', unsafe_allow_html=True)
        st.write(
            "Simulate how common interventions (orientation completion, advising, support engagement, early LMS activity) "
            "could reduce risk and improve expected enrollment and first-term retention."
        )

        if "student_id" not in df_f.columns or len(df_f) == 0:
            st.warning("No students match the current filters.")
        else:
            ids = sorted(df_f["student_id"].astype(int).unique().tolist())
            selected_id = st.selectbox("Choose a student", ids, key="whatif_student")
            row = df_f[df_f["student_id"].astype(int) == int(selected_id)].iloc[0]

            before_score = int(row.get("risk_score", 0))
            before_level = row.get("risk_level", risk_level_from_score(before_score))
            before_enroll_p, before_retain_p = prob_from_risk_level(before_level)

            cA, cB, cC, cD, cE = st.columns([1, 1, 1, 1, 1], gap="large")
            with cA:
                attend_orientation = st.checkbox("Attend Orientation", value=False)
            with cB:
                contact_advisor = st.checkbox("Contact Advisor", value=False)
            with cC:
                use_support = st.checkbox("Use Support Program", value=False)
            with cD:
                submit_assignment = st.checkbox("Submit First Assignment", value=False)
            with cE:
                boost_login = st.checkbox("Improve LMS Logins", value=False)

            after_score = adjusted_risk_score(
                row,
                attend_orientation=attend_orientation,
                contact_advisor=contact_advisor,
                use_support=use_support,
                submit_assignment=submit_assignment,
                boost_login=boost_login,
            )
            after_level = risk_level_from_score(after_score)
            after_enroll_p, after_retain_p = prob_from_risk_level(after_level)

            m1, m2, m3, m4 = st.columns([1.2, 1.2, 1.2, 1.2], gap="large")
            m1.metric("Risk Score (Before)", before_score)
            m2.metric("Risk Level (Before)", before_level)
            m3.metric("Risk Score (After)", after_score, delta=(before_score - after_score))
            m4.metric("Risk Level (After)", after_level)

            p1, p2 = st.columns([1, 1], gap="large")
            with p1:
                st.markdown("**Estimated Enrollment Probability**")
                st.write(f"Before: **{before_enroll_p:.0%}**")
                st.write(f"After: **{after_enroll_p:.0%}**")
            with p2:
                st.markdown("**Estimated First-Term Retention Probability**")
                st.write(f"Before: **{before_retain_p:.0%}**")
                st.write(f"After: **{after_retain_p:.0%}**")

            st.markdown("**Before: Why flagged**")
            reasons = why_flagged(row)
            st.write(" • " + " • ".join(reasons) if reasons else "No major risk flags detected.")

            st.success(
                "This is explainable and action-oriented. We can operationalize these interventions through outreach workflows."
            )