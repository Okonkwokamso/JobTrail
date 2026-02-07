import streamlit as st
from app.web import config
from app.web.database import get_db, get_job_stats
from app.web.utils import init_session_state
from app.web.components import dashboard, jobs, applications, scrape, settings

# Configure page
config.configure_page()
config.load_custom_css()

# Initialize
init_session_state()
db = get_db()

# Sidebar
st.sidebar.title("💼 JobTrail")
st.sidebar.markdown("---")

page = st.sidebar.radio(
  "Navigation",
  ["📊 Dashboard", "💼 Jobs", "📝 Applications", "🔍 Scrape Jobs", "⚙️ Settings"],
  label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")
stats = get_job_stats(db)
st.sidebar.metric("Total Jobs", stats['total'])
st.sidebar.metric("Added This Week", stats['recent_7days'])

# Route to pages
if page == "📊 Dashboard":
  dashboard.render(db)
elif page == "💼 Jobs":
  jobs.render(db)
elif page == "📝 Applications":
  applications.render(db)
elif page == "🔍 Scrape Jobs":
  scrape.render(db)
elif page == "⚙️ Settings":
  settings.render(db)