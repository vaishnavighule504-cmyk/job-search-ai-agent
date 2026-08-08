import streamlit as st
import os
import glob
from src.jobs import search_jobs
from src.ui import display_job_card
from src.rag import initialize_rag, process_uploaded_resume
from src.database import get_all_applications, update_application_status, delete_application
from src.ai import analyze_resume_general
from src.company import get_company_facts_from_jobs, generate_company_insights
from src.export import generate_pdf_report

# Initialize RAG vector store on startup
try:
    initialize_rag()
except Exception as e:
    pass

st.set_page_config(
    page_title="Careerly AI / Job Search AI Agent",
    page_icon="ðŸ’¼",
    layout="wide"
)

# Premium warm earth-toned CSS injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

    /* Global Base Reset to Earth/Cream Theme */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F8EDE3 !important;
        color: #000000 !important;
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Disable default vertical sidebar and toggles */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Width limits and margins */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    /* Header removal */
    [data-testid="stHeader"] {
        background-color: transparent !important;
        height: 0px !important;
    }

    /* Global Titles & Headings */
    h1, h2, h3, h4, h5, h6, [data-testid="stHeader"], .stSubheader {
        color: #000000 !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        margin-top: 0px !important;
        letter-spacing: -0.5px !important;
    }

    h1 {
        font-size: 54px !important;
        font-weight: 800 !important;
        line-height: 1.15 !important;
    }

    h2 {
        border-bottom: 2px solid #8D493A !important;
        padding-bottom: 8px !important;
        margin-bottom: 24px !important;
        font-size: 32px !important;
        font-weight: 800 !important;
    }

    h3 {
        font-size: 22px !important;
        font-weight: 600 !important;
    }

    /* Enforce all standard text is black */
    p, li, span, label, input, select, textarea, div {
        color: #000000 !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* Top Navigation Navbar Row */
    div[data-testid="stHorizontalBlock"]:first-of-type {
        background-color: #FFFFFF !important;
        border-bottom: 1px solid #D0B8A8 !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 1px 3px 0 rgba(141, 73, 58, 0.05) !important;
    }

    div[data-testid="stHorizontalBlock"]:first-of-type button {
        background-color: transparent !important;
        color: #000000 !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 8px 14px !important;
        border-radius: 20px !important; /* Rounded pill active style */
        transition: all 0.15s ease-in-out !important;
        height: auto !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type button:hover {
        background-color: #DFD3C3 !important;
        color: #000000 !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"] {
        background-color: #DFD3C3 !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border: 1px solid #8D493A !important;
    }

    /* Primary buttons (Earthy sand background, black text) */
    button[kind="primary"] {
        background-color: #D0B8A8 !important;
        color: #000000 !important;
        border: 1px solid #8D493A !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        transition: all 0.15s ease-in-out !important;
        font-family: 'Outfit', sans-serif !important;
    }
    button[kind="primary"]:hover {
        background-color: #DFD3C3 !important;
        border-color: #8D493A !important;
        color: #000000 !important;
        box-shadow: 0 4px 12px rgba(141, 73, 58, 0.1) !important;
    }

    /* Secondary buttons (White/beige, black text) */
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #D0B8A8 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        transition: all 0.15s ease-in-out !important;
        font-family: 'Outfit', sans-serif !important;
    }
    button[kind="secondary"]:hover {
        background-color: #F8EDE3 !important;
        border-color: #8D493A !important;
        color: #000000 !important;
    }

    /* Vertical block border wrapper styled as clean white SaaS cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D0B8A8 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px 0 rgba(141, 73, 58, 0.03) !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
    }

    /* Expander styling to override dark backgrounds */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D0B8A8 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px 0 rgba(141, 73, 58, 0.03) !important;
        margin-bottom: 20px !important;
    }
    div[data-testid="stExpander"] summary {
        background-color: #F8EDE3 !important;
        color: #8D493A !important;
        border-bottom: 1px solid #D0B8A8 !important;
        padding: 12px 16px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: #DFD3C3 !important;
    }
    div[data-testid="stExpander"] summary svg {
        fill: #8D493A !important;
    }
    div[data-testid="stExpander"] summary span {
        color: #8D493A !important;
        font-weight: 600 !important;
    }

    /* Inputs text box, selectbox, number input, and textarea overrides */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius: 6px !important;
        border: 1px solid #D0B8A8 !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: 'Outfit', sans-serif !important;
        height: auto !important;
    }

    /* Selectbox specific overrides targeting BaseWeb select components */
    div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border-radius: 6px !important;
        border: 1px solid #D0B8A8 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: none !important;
    }
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span {
        color: #000000 !important;
    }

    div[data-testid="stNumberInput"] > div {
        background-color: #FFFFFF !important;
        border-radius: 6px !important;
        border: 1px solid #D0B8A8 !important;
    }

    div[data-testid="stNumberInput"] button {
        background-color: #F8EDE3 !important;
        color: #000000 !important;
        border: none !important;
    }
    div[data-testid="stNumberInput"] button:hover {
        background-color: #DFD3C3 !important;
    }

    /* Dropdown popover list styling */
    div[data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] div,
    div[data-baseweb="popover"] span {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] li:hover div,
    div[data-baseweb="popover"] li:hover span {
        background-color: #F8EDE3 !important;
        color: #8D493A !important;
    }

    /* File Uploader overrides */
    div[data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 1px dashed #D0B8A8 !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }
    div[data-testid="stFileUploader"] section {
        background-color: transparent !important;
        color: #000000 !important;
    }
    div[data-testid="stFileUploader"] button {
        background-color: #F8EDE3 !important;
        color: #000000 !important;
        border: 1px solid #D0B8A8 !important;
    }
    div[data-testid="stFileUploader"] button:hover {
        background-color: #DFD3C3 !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus,
    div[data-baseweb="select"]:focus {
        border-color: #8D493A !important;
        box-shadow: 0 0 0 2px rgba(141, 73, 58, 0.15) !important;
    }

    /* Metric styling */
    div[data-testid="stMetricValue"] {
        color: #000000 !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session state variables
if "jobs" not in st.session_state:
    st.session_state.jobs = []
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# ==================================================
# HORIZONTAL TOP NAVIGATION BAR
# ==================================================
nav_col_logo, nav_col_menu, nav_col_profile = st.columns([1.5, 4.5, 1])

with nav_col_logo:
    st.markdown(
        "<div style='display: flex; align-items: center; height: 50px;'>"
        "<span style='font-size: 20px; font-weight: 700; color: #8D493A; letter-spacing: -0.5px;'>ðŸ’¼ Careerly AI</span>"
        "</div>",
        unsafe_allow_html=True
    )

with nav_col_menu:
    menu_cols = st.columns(6)
    pages = ["Home", "Jobs", "Resume", "AI Career Coach", "Applications", "Companies"]
    for i, p in enumerate(pages):
        with menu_cols[i]:
            is_active = st.session_state.current_page == p
            btn_kind = "primary" if is_active else "secondary"
            if st.button(p, key=f"nav_tab_{p}", use_container_width=True, type=btn_kind):
                st.session_state.current_page = p
                st.rerun()

with nav_col_profile:
    st.markdown(
        "<div style='text-align: right; line-height: 50px; font-size: 14px; font-weight: 500; color: #6D4C41;'>"
        "ðŸ‘¤ Profile"
        "</div>",
        unsafe_allow_html=True
    )

# Status indicators checks
pdf_files = glob.glob(os.path.join("documents", "*.pdf"))
has_pdfs = len(pdf_files) > 0
has_resume = st.session_state.resume_text is not None

# Load SQLite data globally for use in stats/summary
tracked_apps = get_all_applications()
stats = {"Saved": 0, "Applied": 0, "Interview": 0, "Offer": 0}
for app in tracked_apps:
    status = app.get("status")
    if status in stats:
        stats[status] += 1

# ==================================================
# PAGE RENDER ROUTING
# ==================================================

# ----------------- 1. HOME / DASHBOARD PAGE -----------------
if st.session_state.current_page == "Home":
    # Two-column hero section
    col_hero_left, col_hero_right = st.columns([3, 2])

    with col_hero_left:
        st.write("") # spacing
        st.markdown(
            "<p style='font-size: 12px; font-weight: 700; color: #8D493A; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px;'>YOUR AI CAREER COMPANION</p>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<h1 style='font-size: 52px; line-height: 1.15; font-weight: 800; color: #8D493A; margin-bottom: 20px; letter-spacing: -1px;'>"
            "Your career journey, <br><span style='color: #6D4C41;'>simplified with AI.</span>"
            "</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='font-size: 18px; line-height: 1.5; color: #6D4C41; margin-bottom: 30px;'>"
            "Discover relevant opportunities, improve your resume, and get personalized career guidance â€” all in one place."
            "</p>",
            unsafe_allow_html=True
        )

        # Hero CTA buttons
        col_cta1, col_cta2 = st.columns([1, 1.2])
        with col_cta1:
            if st.button("Explore Jobs", key="hero_explore_jobs", use_container_width=True, type="primary"):
                st.session_state.current_page = "Jobs"
                st.rerun()
        with col_cta2:
            if st.button("Review Resume", key="hero_upload_resume", use_container_width=True, type="secondary"):
                st.session_state.current_page = "Resume"
                st.rerun()

    with col_hero_right:
        st.write("")
        # Clean visual card mockup representing resume ATS matching using earthy palette
        st.markdown("""<div style="background-color: #FFFFFF; border: 1px solid #D0B8A8; border-radius: 12px; padding: 24px; box-shadow: 0 10px 25px -5px rgba(141, 73, 58, 0.06); font-family: sans-serif;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
<span style="font-size: 11px; font-weight: 700; color: #6D4C41; text-transform: uppercase; letter-spacing: 0.5px;">ATS Match Audit</span>
<span style="background-color: #DFD3C3; color: #8D493A; font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 20px;">85/100 Score</span>
</div>
<h4 style="margin: 0 0 4px 0; color: #8D493A; font-size: 18px; font-weight: 700; letter-spacing: -0.3px;">Senior Software Engineer</h4>
<p style="margin: 0 0 20px 0; color: #6D4C41; font-size: 13px;">Google LLC â€¢ Bangalore</p>
<div style="margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12px; font-weight: 600; color: #3E2723;">
<span>Resume Keyword Matching</span>
<span>85% Match</span>
</div>
<div style="background-color: #DFD3C3; height: 6px; border-radius: 3px; overflow: hidden;">
<div style="background-color: #8D493A; width: 85%; height: 100%;"></div>
</div>
</div>
<div style="display: flex; gap: 12px;">
<div style="flex: 1; background-color: #F8EDE3; padding: 12px; border-radius: 8px; border: 1px solid #D0B8A8;">
<span style="font-size: 10px; font-weight: 700; color: #8D493A; text-transform: uppercase; letter-spacing: 0.2px;">Matching Skills</span>
<ul style="margin: 6px 0 0 0; padding-left: 12px; font-size: 11px; color: #3E2723; line-height: 1.4; font-weight: 500;">
<li>Python Backend</li>
<li>Django / FastAPI</li>
<li>SQL Optimization</li>
</ul>
</div>
<div style="flex: 1; background-color: #F8EDE3; padding: 12px; border-radius: 8px; border: 1px solid #D0B8A8;">
<span style="font-size: 10px; font-weight: 700; color: #6D4C41; text-transform: uppercase; letter-spacing: 0.2px;">Identified Gaps</span>
<ul style="margin: 6px 0 0 0; padding-left: 12px; font-size: 11px; color: #6D4C41; line-height: 1.4; font-weight: 500;">
<li>AWS Deployments</li>
<li>Kubernetes Orchestration</li>
</ul>
</div>
</div>
</div>""", unsafe_allow_html=True)

    st.write("")

    # 5. DASHBOARD STATS (Horizontal metrics)
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"""
        <div style='background-color: #FFFFFF; border: 1px solid #D0B8A8; border-radius: 8px; padding: 16px; text-align: center;'>
            <div style='font-size: 26px; font-weight: 700; color: #8D493A;'>{stats['Saved']}</div>
            <div style='font-size: 12px; font-weight: 600; color: #6D4C41; text-transform: uppercase;'>Saved Jobs</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div style='background-color: #FFFFFF; border: 1px solid #D0B8A8; border-radius: 8px; padding: 16px; text-align: center;'>
            <div style='font-size: 26px; font-weight: 700; color: #8D493A;'>{stats['Applied']}</div>
            <div style='font-size: 12px; font-weight: 600; color: #6D4C41; text-transform: uppercase;'>Applications</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
        <div style='background-color: #FFFFFF; border: 1px solid #D0B8A8; border-radius: 8px; padding: 16px; text-align: center;'>
            <div style='font-size: 26px; font-weight: 700; color: #8D493A;'>{stats['Interview']}</div>
            <div style='font-size: 12px; font-weight: 600; color: #6D4C41; text-transform: uppercase;'>Interviews</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s4:
        st.markdown(f"""
        <div style='background-color: #FFFFFF; border: 1px solid #D0B8A8; border-radius: 8px; padding: 16px; text-align: center;'>
            <div style='font-size: 26px; font-weight: 700; color: #8D493A;'>{stats['Offer']}</div>
            <div style='font-size: 12px; font-weight: 600; color: #6D4C41; text-transform: uppercase;'>Offers</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 6. QUICK ACTIONS GRID
    st.markdown("<h3 style='font-size: 22px; color: #8D493A;'>Continue your career journey</h3>", unsafe_allow_html=True)
    col_q1, col_q2, col_q3 = st.columns(3)

    with col_q1:
        with st.container(border=True):
            st.markdown("<h4 style='font-size: 18px; font-weight: 600; color: #8D493A; margin-bottom: 8px;'>01 â€” Find Opportunities</h4>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 14px; color: #6D4C41; line-height: 1.4;'>Search jobs based on role, location and filters.</p>", unsafe_allow_html=True)
            if st.button("Explore Opportunities", key="q_explore", use_container_width=True):
                st.session_state.current_page = "Jobs"
                st.rerun()

    with col_q2:
        with st.container(border=True):
            st.markdown("<h4 style='font-size: 18px; font-weight: 600; color: #8D493A; margin-bottom: 8px;'>02 â€” Improve Your Resume</h4>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 14px; color: #6D4C41; line-height: 1.4;'>Upload and analyze your resume using AI.</p>", unsafe_allow_html=True)
            if st.button("Optimize Resume", key="q_resume", use_container_width=True):
                st.session_state.current_page = "Resume"
                st.rerun()

    with col_q3:
        with st.container(border=True):
            st.markdown("<h4 style='font-size: 18px; font-weight: 600; color: #8D493A; margin-bottom: 8px;'>03 â€” Ask Careerly</h4>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 14px; color: #6D4C41; line-height: 1.4;'>Get AI guidance about jobs, skills, and planning.</p>", unsafe_allow_html=True)
            if st.button("Start Chat", key="q_coach", use_container_width=True):
                st.session_state.current_page = "AI Career Coach"
                st.rerun()

    st.write("")

    # 7. RECENT ACTIVITY & 8. PIPELINE SUMMARY
    col_act, col_pipe = st.columns([1, 1])

    with col_act:
        st.markdown("<h3 style='font-size: 22px; color: #8D493A;'>Recent Activity</h3>", unsafe_allow_html=True)
        recent_apps = tracked_apps[:3]
        if not recent_apps:
            st.markdown(
                "<div style='background-color: #FFFFFF; border: 1px solid #D0B8A8; border-radius: 8px; padding: 24px; text-align: center;'>"
                "<p style='color: #6D4C41; font-weight: 500; margin-bottom: 8px;'>No recent activity yet.</p>"
                "<p style='color: #6D4C41; font-size: 13px;'>Start by searching for your next opportunity.</p>"
                "</div>",
                unsafe_allow_html=True
            )
        else:
            for app in recent_apps:
                title = app["job_title"]
                company = app["employer_name"]
                status = app["status"]
                st.markdown(f"""
                <div style='background-color: #FFFFFF; border: 1px solid #D0B8A8; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;'>
                    <div style='font-size: 14px;'>
                        <span style='font-weight: 600; color: #8D493A;'>{title}</span> @ <span style='font-weight: 500; color: #3E2723;'>{company}</span>
                    </div>
                    <span style='background-color: #DFD3C3; color: #8D493A; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;'>{status}</span>
                </div>
                """, unsafe_allow_html=True)

    with col_pipe:
        st.markdown("<h3 style='font-size: 22px; color: #8D493A;'>Pipeline Summary</h3>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background-color: #FFFFFF; border: 1px solid #D0B8A8; border-radius: 8px; padding: 24px; text-align: center;'>
            <div style='display: flex; justify-content: space-around; align-items: center; font-size: 13px; font-weight: 600; color: #3E2723;'>
                <div>
                    <div style='font-size: 18px; font-weight: 700; color: #8D493A;'>{stats['Saved']}</div>
                    <div style='margin-top: 4px; color: #6D4C41; font-size: 11px;'>Saved</div>
                </div>
                <div style='color: #D0B8A8; font-size: 16px;'>âž”</div>
                <div>
                    <div style='font-size: 18px; font-weight: 700; color: #8D493A;'>{stats['Applied']}</div>
                    <div style='margin-top: 4px; color: #6D4C41; font-size: 11px;'>Applied</div>
                </div>
                <div style='color: #D0B8A8; font-size: 16px;'>âž”</div>
                <div>
                    <div style='font-size: 18px; font-weight: 700; color: #8D493A;'>{stats['Interview']}</div>
                    <div style='margin-top: 4px; color: #6D4C41; font-size: 11px;'>Interview</div>
                </div>
                <div style='color: #D0B8A8; font-size: 16px;'>âž”</div>
                <div>
                    <div style='font-size: 18px; font-weight: 700; color: #8D493A;'>{stats['Offer']}</div>
                    <div style='margin-top: 4px; color: #6D4C41; font-size: 11px;'>Offer</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 9. AI CAREER COACH CARD (Dashboard version)
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 20px; color: #8D493A; margin-top:0;'>ðŸ¤– Meet your AI Career Coach</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6D4C41;'>Get personalized guidance based on your resume, target roles and career goals.</p>", unsafe_allow_html=True)
        if st.button("Ask Careerly", key="dash_coach_ask_btn"):
            st.session_state.current_page = "AI Career Coach"
            st.rerun()

# ----------------- 2. JOBS PAGE -----------------
elif st.session_state.current_page == "Jobs":
    st.markdown("<h2>Explore Opportunities</h2>", unsafe_allow_html=True)
    st.write("Browse active listings and find your next role using filters and sorting.")

    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("ðŸ” Job Title / Keyword", placeholder="e.g. Python Developer", key="search_title")
    with col2:
        location = st.text_input("ðŸ“ Location", placeholder="e.g. Sangli, Remote", key="search_loc")

    # Filters expander
    with st.expander("âš™ï¸ Advanced Dashboard Filters", expanded=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            employment_filter = st.selectbox(
                "ðŸ’¼ Employment Type",
                ["All", "FULLTIME", "PARTTIME", "CONTRACTOR", "INTERN"],
                key="filter_employment"
            )
        with col_f2:
            experience_filter = st.selectbox(
                "ðŸ“ˆ Experience Level",
                ["All", "Entry Level (< 2 yrs)", "Mid Level (2-5 yrs)", "Senior Level (> 5 yrs)"],
                key="filter_experience"
            )
        with col_f3:
            remote_filter = st.selectbox(
                "ðŸŒ Work Mode",
                ["All", "Remote Only", "On-site / Hybrid"],
                key="filter_remote"
            )
        with col_f4:
            sort_by = st.selectbox(
                "ðŸ”€ Sort Results By",
                ["None", "Title", "Company Name", "Salary (High to Low)"],
                key="filter_sort"
            )

        col_f5, col_f6 = st.columns(2)
        with col_f5:
            min_salary = st.number_input("ðŸ’° Minimum Annual Salary", min_value=0, value=0, step=100000, key="filter_min_salary")
        with col_f6:
            company_filter = st.text_input("ðŸ¢ Company Name (Optional)", placeholder="e.g. Google", key="filter_company_name")

    st.write("")

    if st.button("ðŸ” Search Jobs", use_container_width=True, type="primary"):
        if not job_title.strip() and not location.strip():
            st.error("âš ï¸ Please enter a job title/keyword or a location to search.")
        else:
            query = job_title.strip() if job_title.strip() else "Developer"
            if location.strip():
                query += f" jobs in {location}"
            else:
                query += " jobs"

            with st.spinner("Searching active jobs..."):
                try:
                    st.session_state.jobs = search_jobs(query)
                except Exception as e:
                    st.error(f"Search API encountered a problem: {e}")
                    st.info("Falling back to local mock job database.")
                    st.session_state.jobs = []

    # Apply Filters Locally
    filtered = []
    for job in st.session_state.jobs:
        # Employment Type filter
        if employment_filter != "All":
            types = job.get("job_employment_types") or []
            job_emp = job.get("job_employment_type")
            if job_emp:
                types.append(job_emp)
            if not any(employment_filter in str(t).upper() for t in types):
                continue

        # Company name filter
        if company_filter.strip():
            employer = job.get("employer_name") or ""
            if company_filter.lower() not in employer.lower():
                continue

        # Remote WFH filter
        is_remote = job.get("job_is_remote", False)
        city_lower = (job.get("job_city") or "").lower()
        is_wfh = is_remote or "remote" in city_lower
        if remote_filter == "Remote Only" and not is_wfh:
            continue
        elif remote_filter == "On-site / Hybrid" and is_wfh:
            continue

        # Experience filter
        req_exp_months = job.get("job_required_experience_in_months")
        if req_exp_months is not None:
            exp_years = req_exp_months / 12.0
            if experience_filter == "Entry Level (< 2 yrs)" and exp_years >= 2:
                continue
            elif experience_filter == "Mid Level (2-5 yrs)" and (exp_years < 2 or exp_years > 5):
                continue
            elif experience_filter == "Senior Level (> 5 yrs)" and exp_years <= 5:
                continue

        # Salary filter
        max_sal = job.get("job_max_salary") or job.get("job_min_salary") or 0
        if min_salary > 0 and max_sal < min_salary:
            continue

        filtered.append(job)

    # Sort results
    if sort_by == "Title":
        filtered.sort(key=lambda x: x.get("job_title", "").lower())
    elif sort_by == "Company Name":
        filtered.sort(key=lambda x: x.get("employer_name", "").lower())
    elif sort_by == "Salary (High to Low)":
        filtered.sort(key=lambda x: x.get("job_max_salary") or x.get("job_min_salary") or 0, reverse=True)

    # Display Results
    if filtered:
        st.write("")
        col_header, col_export = st.columns([4, 1])
        with col_header:
            st.subheader(f"ðŸ’¼ Match Results ({len(filtered)})")
        with col_export:
            pdf_bytes = generate_pdf_report(filtered)
            if pdf_bytes:
                st.download_button(
                    label="ðŸ“¥ Export results to PDF",
                    data=pdf_bytes,
                    file_name="job_search_results.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        for job in filtered:
            display_job_card(job)

    elif st.session_state.jobs:
        st.warning("âš ï¸ No job listings matched your filters. Adjust them and try again.")
    else:
        st.info("ðŸ’¡ Fill in the search inputs and click 'Search Jobs' to get started!")

# ----------------- 3. RESUME PAGE -----------------
elif st.session_state.current_page == "Resume":
    st.markdown("<h2>Resume Center</h2>", unsafe_allow_html=True)
    st.write("Upload your resume profile to view text extraction and perform ATS audits.")

    # Active resume loading uploader widget
    uploaded_file = st.file_uploader(
        "Upload your resume PDF (PDF only, max 5MB):",
        type=["pdf"],
        key="resume_page_uploader"
    )

    if uploaded_file is not None:
        MAX_FILE_SIZE_MB = 5
        if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.error("âš ï¸ File size exceeds the 5MB limit. Please upload a smaller PDF resume.")
        else:
            if st.session_state.last_uploaded_file != uploaded_file.name:
                with st.spinner("Processing resume..."):
                    res_text = process_uploaded_resume(uploaded_file)
                    if res_text.startswith("Error"):
                        st.error(f"âš ï¸ {res_text}")
                        st.session_state.resume_text = None
                        st.session_state.last_uploaded_file = None
                    else:
                        st.session_state.resume_text = res_text
                        st.session_state.last_uploaded_file = uploaded_file.name
                        st.success(f"Successfully uploaded: {uploaded_file.name}")
            else:
                st.success(f"ðŸ“‚ Active Resume: {uploaded_file.name}")

    st.write("")

    if not has_resume:
        st.info("ðŸ’¡ Upload your resume above to view parser output and run ATS analysis audits.")
    else:
        # General resume analysis triggers
        if st.button("ðŸ“Š Run General Resume ATS Audit", use_container_width=True, type="primary"):
            with st.spinner("Analyzing resume content against recruitment standards..."):
                try:
                    res_analysis = analyze_resume_general(st.session_state.resume_text)
                    st.session_state.general_resume_analysis = res_analysis
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

        if "general_resume_analysis" in st.session_state:
            st.markdown("### ðŸ“Š ATS and Skills Assessment Report")
            st.markdown(st.session_state.general_resume_analysis)

        with st.expander("ðŸ“„ View Parsed Resume Plain Text"):
            st.text_area("Extracted Resume Text:", st.session_state.resume_text, height=350)

# ----------------- 4. AI CAREER COACH PAGE -----------------
elif st.session_state.current_page == "AI Career Coach":
    st.markdown("<h2>AI Career Coach</h2>", unsafe_allow_html=True)
    st.write("Interact with your persistent career assistant. Ask about keywords, learning roadmaps, and interview preparation.")

    if not has_resume:
        st.info("ðŸ’¡ **Tip:** Upload your resume PDF in the **Resume** tab to unlock personalized match analyses.")
    if not has_pdfs:
        st.warning("âš ï¸ RAG Knowledge base is active, but no career guides were found in your documents folder.")

    # Standard chatbot interaction logic mapped on main screen
    user_question = st.text_input(
        "Ask anything about Resume, Jobs, Interview, or Roadmap:",
        key="main_chat_input"
    )

    suggested_questions = [
        "How can I improve my resume?",
        "What skills am I missing?",
        "How should I prepare for an interview?",
        "Should I apply for this job?",
        "What skills should I learn next?"
    ]

    selected_sug = st.selectbox(
        "ðŸ’¡ Quick Suggestions",
        ["-- Choose a suggested question --"] + suggested_questions,
        key="main_suggested_select"
    )

    if selected_sug != "-- Choose a suggested question --":
        user_question = selected_sug

    ask_button = st.button("ðŸ¤– Ask Assistant", type="primary")

    if ask_button:
        if not user_question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Generating expert response..."):
                from src.chatbot import career_chat
                try:
                    response = career_chat(user_question)
                    st.session_state.main_chat_response = response
                    st.session_state.main_last_question = user_question
                except Exception as e:
                    st.error(f"Chatbot Error: {e}")

    # Render chatbot responses in clean SaaS container cards
    if "main_chat_response" in st.session_state:
        with st.container(border=True):
            st.markdown(f"### â“ Question")
            st.markdown(st.session_state.main_last_question)
            st.divider()
            st.markdown(f"### ðŸ¤– Response")
            st.markdown(st.session_state.main_chat_response)

# ----------------- 5. APPLICATIONS PAGE -----------------
elif st.session_state.current_page == "Applications":
    st.markdown("<h2>Application Lifecycle Tracker</h2>", unsafe_allow_html=True)
    st.write("Manage status pipelines (Saved, Applied, Interview, Rejected, Offer) for saved positions.")

    if not tracked_apps:
        st.info("ðŸ’¡ You have not tracked any jobs yet. Save jobs in the 'Jobs' section to start tracking.")
    else:
        # Metric columns summary
        cols = st.columns(5)
        statuses = ["Saved", "Applied", "Interview", "Rejected", "Offer"]
        emojis = {"Saved": "ðŸ“", "Applied": "ðŸ“¨", "Interview": "ðŸ’¬", "Rejected": "âŒ", "Offer": "ðŸŽ‰"}

        # Recount pipeline values specifically
        tracker_counts = {"Saved": 0, "Applied": 0, "Interview": 0, "Rejected": 0, "Offer": 0}
        for app in tracked_apps:
            st_val = app.get("status", "Saved")
            if st_val in tracker_counts:
                tracker_counts[st_val] += 1

        for idx, status in enumerate(statuses):
            with cols[idx]:
                st.metric(label=f"{emojis[status]} {status}", value=tracker_counts[status])

        st.write("")

        # Export PDF button
        pdf_tracker_bytes = generate_pdf_report(tracked_apps)
        if pdf_tracker_bytes:
            st.download_button(
                label="ðŸ“¥ Export Tracked Applications (PDF)",
                data=pdf_tracker_bytes,
                file_name="tracked_applications.pdf",
                mime="application/pdf",
                key="tracker_export_download_btn"
            )

        st.write("")

        # Display application cards
        for app in tracked_apps:
            job_id = app["job_id"]
            title = app["job_title"]
            company = app["employer_name"]
            city = app["job_city"] or "Not specified"
            link = app["job_apply_link"]
            curr_status = app["status"]
            date_added = app.get("date_added", "N/A")

            with st.container(border=True):
                col_info, col_status_update, col_actions = st.columns([3, 1, 1])

                with col_info:
                    st.markdown(f"### {title} @ {company}")
                    st.markdown(f"ðŸ“ **Location:** {city} | ðŸ“… **Tracked on:** {date_added}")
                    if link and link != "N/A":
                        st.markdown(f"ðŸ”— [Apply Link]({link})")

                with col_status_update:
                    status_opts = ["Saved", "Applied", "Interview", "Rejected", "Offer"]
                    selected_idx = status_opts.index(curr_status) if curr_status in status_opts else 0

                    new_status = st.selectbox(
                        "Pipeline Stage",
                        status_opts,
                        index=selected_idx,
                        key=f"tracker_status_sel_{job_id}"
                    )

                    if new_status != curr_status:
                        if update_application_status(job_id, new_status):
                            st.toast(f"Updated status for {title}!")
                            st.rerun()

                with col_actions:
                    st.write("") # vertical spacing
                    if st.button("Delete ðŸ—‘ï¸", key=f"tracker_delete_{job_id}", use_container_width=True):
                        if delete_application(job_id):
                            st.toast(f"Removed {title} from pipeline!")
                            st.rerun()

# ----------------- 6. COMPANIES PAGE -----------------
elif st.session_state.current_page == "Companies":
    st.markdown("<h2>Company Insights Research</h2>", unsafe_allow_html=True)
    st.write("Lookup key company facts from active job posts and generate Gemini-driven corporate profiling.")

    comp_input = st.text_input("ðŸ¢ Company Name to Research:", placeholder="e.g. Google, Amazon, TCS", key="company_input_box")

    if st.button("ðŸ¢ Research Company", use_container_width=True, type="primary"):
        if not comp_input.strip():
            st.warning("Please enter a valid company name.")
        else:
            with st.spinner(f"Compiling profiles for {comp_input}..."):
                facts = get_company_facts_from_jobs(comp_input, st.session_state.jobs)
                ai_insights = generate_company_insights(comp_input)

                st.session_state.company_research_results = {
                    "company_name": comp_input,
                    "facts": facts,
                    "ai_insights": ai_insights
                }

    if "company_research_results" in st.session_state:
        res_data = st.session_state.company_research_results
        st.subheader(f"ðŸ¢ Research Report: {res_data['company_name']}")

        # Facts (Factual Data)
        with st.container(border=True):
            st.markdown("### ðŸ“‹ Factual Job Post Data (From Listings API)")
            facts = res_data["facts"]
            if facts["found"]:
                st.markdown(f"**Verified API Title:** {facts['employer_name']}")
                if facts["employer_website"]:
                    st.markdown(f"**Corporate Website:** [{facts['employer_website']}]({facts['employer_website']})")
                if facts["locations"]:
                    st.markdown(f"**Hiring Locations Found:** {', '.join(facts['locations'])}")
                if facts["job_types"]:
                    st.markdown(f"**Hiring Job Types:** {', '.join(facts['job_types'])}")
                if facts["job_titles"]:
                    st.markdown(f"**Active Positions:**")
                    for t in facts["job_titles"][:5]:
                        st.markdown(f"- {t}")
            else:
                st.info("No matching job listings from this employer were found in the current search query. Facts could not be verified from active posts.")

        # AI generated overview (AI-Generated content)
        st.write("")
        with st.container(border=True):
            st.markdown("### ðŸ¤– AI-Generated Insight (Estimated)")
            st.warning("âš ï¸ The following profile is synthesized by Gemini AI using public domain information. Individual experiences may vary.")
            st.markdown(res_data["ai_insights"])