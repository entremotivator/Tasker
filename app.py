import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Task Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for beautiful styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * {font-family: 'Inter', sans-serif;}
    
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem;}
    
    .dashboard-header {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: white;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {transform: translateY(-5px);}
    
    .metric-value {font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0;}
    .metric-label {font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;}
    
    .task-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .task-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transform: translateX(5px);
    }
    
    .task-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .task-description {
        color: #718096;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-completed {background: #48bb78; color: white;}
    .status-progress {background: #ed8936; color: white;}
    .status-todo {background: #4299e1; color: white;}
    .status-pending {background: #f56565; color: white;}
    
    .filter-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }
    
    .stats-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }
    
    .progress-bar {
        height: 10px;
        background: #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #48bb78 0%, #38a169 100%);
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Function to load data from Google Sheets
@st.cache_data(ttl=60)
def load_data():
    sheet_id = "1pbK-B-Q9p8fVjxJIsjEVrAfRgqEPCeYw8rZojZPAb84"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Function to get status color
def get_status_class(status):
    if pd.isna(status):
        return 'status-pending'
    status = status.lower()
    if 'completed' in status or 'complete' in status:
        return 'status-completed'
    elif 'progress' in status:
        return 'status-progress'
    elif 'to do' in status or 'todo' in status:
        return 'status-todo'
    else:
        return 'status-pending'

def get_status_emoji(status):
    if pd.isna(status):
        return '⏳'
    status = status.lower()
    if 'completed' in status or 'complete' in status:
        return '✅'
    elif 'progress' in status:
        return '🔄'
    elif 'to do' in status or 'todo' in status:
        return '📝'
    else:
        return '⏳'

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Dashboard Controls")
    st.markdown("---")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("🔄 Auto-refresh (60s)", value=True)
    
    if st.button("🔃 Manual Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    df = load_data()
    if df is not None and not df.empty:
        total = len(df)
        completed = len(df[df['Status'].str.contains('Completed|Complete', case=False, na=False)])
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
        st.progress(completion_rate / 100)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("This dashboard displays real-time task data from Google Sheets. Tasks are categorized by status and displayed with detailed analytics.")
    
    st.markdown("---")
    st.caption(f"🕒 Last updated: {datetime.now().strftime('%I:%M:%S %p')}")

# Main content
st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
st.title("📊 Task Management Dashboard")
st.markdown("Real-time task tracking and analytics powered by Google Sheets")
st.markdown('</div>', unsafe_allow_html=True)

# Load data
df = load_data()

if df is not None and not df.empty:
    
    # Key Metrics Row
    st.markdown("### 📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = len(df)
    completed = len(df[df['Status'].str.contains('Completed|Complete', case=False, na=False)])
    in_progress = len(df[df['Status'].str.contains('Progress', case=False, na=False)])
    todo = len(df[df['Status'].str.contains('To Do|todo', case=False, na=False)])
    pending = total_tasks - completed - in_progress - todo
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="metric-label">Total Tasks</div>
            <div class="metric-value">{total_tasks}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);">
            <div class="metric-label">Completed</div>
            <div class="metric-value">{completed}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);">
            <div class="metric-label">In Progress</div>
            <div class="metric-value">{in_progress}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);">
            <div class="metric-label">To Do</div>
            <div class="metric-value">{todo}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Progress Overview
    completion_percentage = (completed / total_tasks * 100) if total_tasks > 0 else 0
    st.markdown(f"""
    <div class="stats-container">
        <h4>📊 Overall Progress</h4>
        <p>You've completed <strong>{completed}</strong> out of <strong>{total_tasks}</strong> tasks ({completion_percentage:.1f}%)</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {completion_percentage}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Status Distribution")
        status_counts = df['Status'].value_counts()
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color_discrete_sequence=['#48bb78', '#ed8936', '#4299e1', '#f56565']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=True, height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Task Status Breakdown")
        status_data = pd.DataFrame({
            'Status': ['Completed', 'In Progress', 'To Do', 'Pending'],
            'Count': [completed, in_progress, todo, pending]
        })
        fig_bar = px.bar(
            status_data,
            x='Status',
            y='Count',
            color='Status',
            color_discrete_map={
                'Completed': '#48bb78',
                'In Progress': '#ed8936',
                'To Do': '#4299e1',
                'Pending': '#f56565'
            }
        )
        fig_bar.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Filter Section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("### 🔍 Filter & Search Tasks")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("🔎 Search tasks by name or description:", "")
    
    with col2:
        status_filter = st.multiselect(
            "Filter by Status:",
            options=df['Status'].unique(),
            default=df['Status'].unique()
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = df[df['Status'].isin(status_filter)]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Task'].str.contains(search_term, case=False, na=False) |
            filtered_df['Description'].str.contains(search_term, case=False, na=False)
        ]
    
    # Display Tasks
    st.markdown(f"### 📋 Tasks ({len(filtered_df)} items)")
    
    if len(filtered_df) > 0:
        for idx, row in filtered_df.iterrows():
            task = row['Task'] if pd.notna(row['Task']) else 'Untitled Task'
            description = row['Description'] if pd.notna(row['Description']) else 'No description provided'
            status = row['Status'] if pd.notna(row['Status']) else 'Pending'
            
            status_class = get_status_class(status)
            status_emoji = get_status_emoji(status)
            
            st.markdown(f"""
            <div class="task-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div class="task-title">{status_emoji} {task}</div>
                        <div class="task-description">{description}</div>
                    </div>
                    <div>
                        <span class="status-badge {status_class}">{status}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No tasks match your current filters.")
    
    # Detailed Data Table
    with st.expander("📊 View Detailed Data Table"):
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400
        )
    
    # Analytics Section
    st.markdown("### 📊 Advanced Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Completion Rate",
            f"{completion_percentage:.1f}%",
            delta=f"{completed} completed"
        )
    
    with col2:
        active_tasks = in_progress + todo
        st.metric(
            "Active Tasks",
            active_tasks,
            delta=f"{in_progress} in progress"
        )
    
    with col3:
        avg_per_status = total_tasks / len(df['Status'].unique()) if len(df['Status'].unique()) > 0 else 0
        st.metric(
            "Avg per Status",
            f"{avg_per_status:.1f}",
            delta="tasks"
        )
    
    # Timeline view
    st.markdown("### 📅 Task Timeline")
    timeline_fig = go.Figure()
    
    for status in df['Status'].unique():
        status_tasks = df[df['Status'] == status]
        timeline_fig.add_trace(go.Bar(
            name=status,
            x=[status],
            y=[len(status_tasks)],
            text=[len(status_tasks)],
            textposition='auto',
        ))
    
    timeline_fig.update_layout(
        barmode='group',
        height=300,
        showlegend=True,
        xaxis_title="Status",
        yaxis_title="Number of Tasks"
    )
    
    st.plotly_chart(timeline_fig, use_container_width=True)
    
    # Export options
    st.markdown("### 💾 Export Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        json_data = filtered_df.to_json(orient='records')
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        st.button("🔗 Open Google Sheet", use_container_width=True, 
                 on_click=lambda: st.markdown('[Open Sheet](https://docs.google.com/spreadsheets/d/1pbK-B-Q9p8fVjxJIsjEVrAfRgqEPCeYw8rZojZPAb84/edit)'))

else:
    st.error("⚠️ Unable to load data from Google Sheets. Please check the sheet ID and permissions.")
    st.info("Make sure the Google Sheet is set to 'Anyone with the link can view'")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 2rem;'>
    <p>🔗 <strong>Connected to Google Sheets</strong> | Auto-refreshes every 60 seconds</p>
    <p style='font-size: 0.85rem; opacity: 0.8;'>Built with Streamlit • Data updates in real-time</p>
</div>
""", unsafe_allow_html=True)
