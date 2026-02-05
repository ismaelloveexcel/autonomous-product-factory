"""Streamlit dashboard for Autonomous Product Factory."""

import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.models import (
    SessionLocal, Project, ProjectStatus, AgentHealth,
    Metric, Task, AgentType, init_db
)
from orchestration.pipeline import AgentPipeline
from utils.cost_tracker import CostTracker
from utils.config import config

# Page config
st.set_page_config(
    page_title="Autonomous Product Factory",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Custom CSS for better UI (following UI_EXCELLENCE_STANDARD)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .status-live { color: #00c851; font-weight: 600; }
    .status-building { color: #ffbb33; font-weight: 600; }
    .status-killed { color: #ff4444; font-weight: 600; }
    .status-failed { color: #ff4444; font-weight: 600; }
    .primary-action {
        font-size: 1.2rem !important;
        padding: 1rem 2rem !important;
        margin: 2rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)


def get_db_session():
    """Get database session."""
    return SessionLocal()


def get_project_stats():
    """Get overall project statistics."""
    session = get_db_session()
    try:
        total = session.query(Project).count()
        live = session.query(Project).filter_by(status=ProjectStatus.LIVE).count()
        building = session.query(Project).filter(
            Project.status.in_([
                ProjectStatus.RESEARCHING,
                ProjectStatus.VALIDATING,
                ProjectStatus.BUILDING,
                ProjectStatus.REVIEWING
            ])
        ).count()
        killed = session.query(Project).filter_by(status=ProjectStatus.KILLED).count()
        failed = session.query(Project).filter_by(status=ProjectStatus.FAILED).count()
        
        return {
            "total": total,
            "live": live,
            "building": building,
            "killed": killed,
            "failed": failed
        }
    finally:
        session.close()


def render_header():
    """Render dashboard header."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<div class="main-header">🏭 Product Factory</div>', unsafe_allow_html=True)
        st.caption("Autonomous app generation and management")
    
    with col2:
        budget = CostTracker.get_monthly_budget()
        remaining_pct = (budget["remaining"] / budget["total_limit"] * 100) if budget["total_limit"] > 0 else 0
        
        if budget["exceeded"]:
            st.error(f"💰 Budget Exceeded")
        elif remaining_pct < 20:
            st.warning(f"💰 ${budget['remaining']:.2f} left")
        else:
            st.success(f"💰 ${budget['remaining']:.2f} left")


def render_overview():
    """Render overview metrics."""
    st.subheader("Overview")
    
    stats = get_project_stats()
    budget = CostTracker.get_monthly_budget()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Projects", stats["total"])
    
    with col2:
        st.metric("🟢 Live", stats["live"])
    
    with col3:
        st.metric("🟡 Building", stats["building"])
    
    with col4:
        st.metric("🔴 Killed", stats["killed"])
    
    with col5:
        st.metric("Budget Used", f"${budget['total_spent']:.2f}", 
                 f"{budget['percentage_used']:.1f}%")


def render_projects_table():
    """Render projects table."""
    st.subheader("Projects")
    
    session = get_db_session()
    try:
        projects = session.query(Project).order_by(Project.created_at.desc()).limit(50).all()
        
        if not projects:
            st.info("No projects yet. Click 'Generate New App' to start!")
            return
        
        # Prepare data
        data = []
        for p in projects:
            status_emoji = {
                ProjectStatus.LIVE: "🟢",
                ProjectStatus.BUILDING: "🟡",
                ProjectStatus.REVIEWING: "🟡",
                ProjectStatus.KILLED: "🔴",
                ProjectStatus.FAILED: "❌"
            }.get(p.status, "⚪")
            
            data.append({
                "ID": p.id,
                "Name": p.name,
                "Status": f"{status_emoji} {p.status.value}",
                "Category": p.category or "-",
                "Age": f"{p.target_age_min}-{p.target_age_max}",
                "DAU": p.daily_active_users,
                "Cost": f"${p.total_cost:.2f}",
                "Created": p.created_at.strftime("%Y-%m-%d"),
                "URL": p.vercel_url or "-"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    finally:
        session.close()


def render_agent_health():
    """Render agent health status."""
    st.subheader("Agent Health")
    
    session = get_db_session()
    try:
        agents = session.query(AgentHealth).all()
        
        cols = st.columns(4)
        
        for i, agent in enumerate(agents):
            with cols[i % 4]:
                status = "✅" if agent.is_healthy else "❌"
                success_rate = (agent.total_successes / agent.total_executions * 100) if agent.total_executions > 0 else 0
                
                st.markdown(f"""
                **{status} {agent.agent_type.value.replace('_', ' ').title()}**  
                Success: {success_rate:.1f}%  
                Executions: {agent.total_executions}  
                Avg Duration: {agent.avg_duration_seconds:.1f}s
                """)
    
    finally:
        session.close()


def render_cost_chart():
    """Render cost trends chart."""
    st.subheader("Cost Trends")
    
    session = get_db_session()
    try:
        # Get projects with costs
        projects = session.query(Project).filter(Project.total_cost > 0).all()
        
        if not projects:
            st.info("No cost data yet")
            return
        
        # Prepare data
        data = []
        for p in projects:
            data.append({
                "Project": p.name[:20],
                "OpenAI": p.openai_cost,
                "Vercel": p.vercel_cost,
                "Total": p.total_cost,
                "Date": p.created_at
            })
        
        df = pd.DataFrame(data)
        
        # Create stacked bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(name="OpenAI", x=df["Project"], y=df["OpenAI"]))
        fig.add_trace(go.Bar(name="Vercel", x=df["Project"], y=df["Vercel"]))
        
        fig.update_layout(
            barmode="stack",
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    finally:
        session.close()


def render_primary_action():
    """Render primary action button."""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Generate New App", key="generate_app", use_container_width=True, type="primary"):
            with st.spinner("Generating new app... This may take several minutes."):
                try:
                    pipeline = AgentPipeline()
                    result = asyncio.run(pipeline.run_full_pipeline())
                    
                    if result["success"]:
                        st.success(f"✅ App generated successfully!")
                        st.info(f"URL: {result.get('deployed_url')}")
                        st.info(f"Cost: ${result.get('total_cost', 0):.2f}")
                        st.balloons()
                    else:
                        st.error(f"❌ Generation failed: {result.get('error') or result.get('stopped_reason')}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            
            st.rerun()


def render_sidebar():
    """Render sidebar with controls."""
    with st.sidebar:
        st.header("Controls")
        
        # Manual project creation
        with st.expander("Create Manual Project"):
            name = st.text_input("App Name")
            description = st.text_area("Description")
            
            if st.button("Create Project"):
                if name and description:
                    session = get_db_session()
                    try:
                        project = Project(
                            name=name,
                            description=description,
                            status=ProjectStatus.IDEA
                        )
                        session.add(project)
                        session.commit()
                        st.success(f"Project {project.id} created!")
                    finally:
                        session.close()
                else:
                    st.error("Name and description required")
        
        # Agent controls
        st.markdown("---")
        st.subheader("Agent Controls")
        
        session = get_db_session()
        try:
            projects = session.query(Project).all()
            if projects:
                project_options = {f"{p.id}: {p.name}": p.id for p in projects}
                selected = st.selectbox("Select Project", list(project_options.keys()))
                selected_id = project_options[selected]
                
                agent_type = st.selectbox("Agent", [
                    "Research", "Viability", "Development", 
                    "Aesthetic", "Marketing", "Launch", "Customer Service"
                ])
                
                if st.button("Run Agent"):
                    st.info(f"Running {agent_type} agent on project {selected_id}...")
                    # Would run specific agent here
        finally:
            session.close()
        
        # Budget controls
        st.markdown("---")
        st.subheader("Budget")
        budget = CostTracker.get_monthly_budget()
        st.write(f"**Spent**: ${budget['total_spent']:.2f}")
        st.write(f"**Limit**: ${budget['total_limit']:.2f}")
        st.progress(budget['percentage_used'] / 100)
        
        # Refresh
        st.markdown("---")
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()


def main():
    """Main dashboard function."""
    render_header()
    render_sidebar()
    
    # Main content
    render_overview()
    
    st.markdown("---")
    
    # Primary action (ONE clear action)
    render_primary_action()
    
    st.markdown("---")
    
    # Tabs for detailed views
    tab1, tab2, tab3 = st.tabs(["📱 Projects", "🤖 Agents", "💰 Costs"])
    
    with tab1:
        render_projects_table()
    
    with tab2:
        render_agent_health()
    
    with tab3:
        render_cost_chart()
    
    # Auto-refresh every 30 seconds
    st.markdown(f"*Last updated: {datetime.now().strftime('%H:%M:%S')}*")


if __name__ == "__main__":
    main()
