import streamlit as st
from app.web.utils import jobs_to_dataframe
from app.web.database import get_jobs_with_filters
from app.models.job import Job


def render(db):
  """Render settings page."""
  st.title("⚙️ Settings")
  
  tab1, tab2, tab3 = st.tabs(["Database", "Preferences", "About"])
  
  with tab1:
    _render_database_tab(db)
  
  with tab2:
    _render_preferences_tab()
  
  with tab3:
    _render_about_tab()


def _render_database_tab(db):
  """Render database management tab."""
  st.subheader("Database Management")
  
  col1, col2 = st.columns(2)
  
  with col1:
    st.markdown("**Export Data**")
    if st.button("📥 Export to CSV"):
        jobs = get_jobs_with_filters(db)
        df = jobs_to_dataframe(jobs)
        csv = df.to_csv(index=False)
        st.download_button(
          "Download CSV",
          csv,
          "jobtrail_export.csv",
          "text/csv"
        )
  
  with col2:
    st.markdown("**Database Stats**")
    st.info(f"Total Jobs: {db.query(Job).count()}")
    st.info(f"Database: SQLite")


def _render_preferences_tab():
  """Render preferences tab."""
  st.subheader("Preferences")
  st.info("Coming soon: Notification settings, default filters, etc.")


def _render_about_tab():
  """Render about tab."""
  st.subheader("About JobTrail")
  st.markdown("""
  **JobTrail** - Your personal job search operating system
  
  - Version: 1.0.0
  - Built with: Python, FastAPI, SQLAlchemy, Streamlit
  - Author: Kamso
  
  Features:
  - 🔍 Multi-source job scraping
  - 📊 Application tracking
  - 📈 Analytics & insights
  - 💾 Local database storage
  """)