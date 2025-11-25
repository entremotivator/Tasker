import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import json

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
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        max-width: 100%;
        word-wrap: break-word;
    }
    
    .user-message {
        background: #667eea;
        color: white;
        margin-left: 1rem;
    }
    
    .bot-message {
        background: #f7fafc;
        color: #2d3748;
        margin-right: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    .webhook-section {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to load data from Google Sheets
@st.cache_data(ttl=60)
def load_data():
    sheet_id = "1OZC_Wk4rQZqzhdCwzEHXjbsQUsih3G0uaAaTf-svAds"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Function to send message to webhook
def send_to_webhook(message, webhook_url):
    try:
        payload = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "source": "streamlit_dashboard"
        }
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.json() if response.status_code == 200 else {"error": "Failed to get response"}
    except Exception as e:
        return {"error": str(e)}

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
        
        st.metric("Total Tasks", total)
        st.metric("Completed", completed)
        st.metric("Remaining", total - completed)
    
    # Webhook Configuration Section
    st.markdown("---")
    st.markdown("### 🔗 Webhook Configuration")
    
    webhook_url = st.text_input(
        "Webhook URL:",
        value="https://agentonline-u29564.vm.elestio.app/webhook-test/Projectchat",
        help="Enter the webhook endpoint URL"
    )
    
    if st.button("🧪 Test Webhook", use_container_width=True):
        with st.spinner("Testing webhook..."):
            test_response = send_to_webhook("Test message from dashboard", webhook_url)
            if "error" not in test_response:
                st.success("✅ Webhook test successful!")
            else:
                st.error(f"❌ Webhook test failed: {test_response.get('error', 'Unknown error')}")
    
    # Chatbot Section
    st.markdown("---")
    st.markdown("### 💬 AI Assistant")
    st.caption("Ask questions about your tasks")
    
    # Chat display area
    chat_container = st.container()
    
    with chat_container:
        for chat in st.session_state.chat_history[-5:]:  # Show last 5 messages
            if chat['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {chat['message']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 Assistant:</strong> {chat['message']}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    user_message = st.text_input("Type your message:", key="chat_input", placeholder="Ask me anything...")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("📤 Send", use_container_width=True):
            if user_message:
                # Add user message to history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'message': user_message,
                    'timestamp': datetime.now()
                })
                
                # Send to webhook and get response
                with st.spinner("Thinking..."):
                    bot_response = send_to_webhook(user_message, webhook_url)
                    
                    if "error" not in bot_response:
                        response_text = bot_response.get('response', 'Message received!')
                    else:
                        response_text = f"Sorry, I encountered an error: {bot_response['error']}"
                    
                    # Add bot response to history
                    st.session_state.chat_history.append({
                        'role': 'bot',
                        'message': response_text,
                        'timestamp': datetime.now()
                    })
                
                st.rerun()
    
    with col2:
        if st.button("🗑️", use_container_width=True, help="Clear chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("This dashboard displays real-time task data from Google Sheets with integrated webhook notifications and AI chat assistance.")
    
    st.markdown("---")
    st.caption(f"🕒 Last updated: {datetime.now().strftime('%I:%M:%S %p')}")

# Main content
st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
st.title("📊 Advanced Task Management Dashboard")
st.markdown("Real-time task tracking, analytics, and AI-powered assistance")
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
    
    # Performance Insights Section
    st.markdown("### 🎯 Performance Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stats-container">
            <h5>🏆 Productivity Score</h5>
            <p>Based on completion rate and task velocity</p>
        </div>
        """, unsafe_allow_html=True)
        
        productivity_score = min(100, completion_percentage + (completed / max(1, total_tasks) * 50))
        st.metric("Score", f"{productivity_score:.0f}/100", delta="Excellent" if productivity_score > 75 else "Good")
    
    with col2:
        st.markdown("""
        <div class="stats-container">
            <h5>⚡ Task Velocity</h5>
            <p>Average tasks completed per status</p>
        </div>
        """, unsafe_allow_html=True)
        
        velocity = completed / len(df['Status'].unique()) if len(df['Status'].unique()) > 0 else 0
        st.metric("Velocity", f"{velocity:.1f}", delta="tasks/status")
    
    with col3:
        st.markdown("""
        <div class="stats-container">
            <h5>🎲 Work Distribution</h5>
            <p>Balance across different statuses</p>
        </div>
        """, unsafe_allow_html=True)
        
        distribution_score = (1 - (max(completed, in_progress, todo, pending) / max(1, total_tasks))) * 100
        st.metric("Balance", f"{distribution_score:.0f}%", delta="Optimal" if distribution_score > 50 else "Needs balance")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row
    st.markdown("### 📊 Visual Analytics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🥧 Status Distribution")
        status_counts = df['Status'].value_counts()
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color_discrete_sequence=['#48bb78', '#ed8936', '#4299e1', '#f56565', '#9f7aea', '#38b2ac']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
        fig_pie.update_layout(showlegend=True, height=400, margin=dict(t=40, b=40))
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Task Status Breakdown")
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
            },
            text='Count'
        )
        fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
        fig_bar.update_layout(showlegend=False, height=400, margin=dict(t=40, b=40))
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Additional Analytics
    st.markdown("### 📈 Trend Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📉 Completion Funnel")
        funnel_data = pd.DataFrame({
            'Stage': ['Total Tasks', 'In Progress', 'Completed'],
            'Count': [total_tasks, in_progress, completed]
        })
        fig_funnel = px.funnel(
            funnel_data,
            x='Count',
            y='Stage',
            color='Stage',
            color_discrete_sequence=['#667eea', '#ed8936', '#48bb78']
        )
        fig_funnel.update_layout(height=350, margin=dict(t=40, b=40))
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎯 Goal Progress")
        goal_target = total_tasks
        goal_achieved = completed
        goal_percentage = (goal_achieved / goal_target * 100) if goal_target > 0 else 0
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=goal_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Completion %", 'font': {'size': 20}},
            delta={'reference': 75, 'increasing': {'color': "#48bb78"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#667eea"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 50], 'color': '#f56565'},
                    {'range': [50, 75], 'color': '#ed8936'},
                    {'range': [75, 100], 'color': '#48bb78'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=350, margin=dict(t=40, b=40))
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Filter Section
    st.markdown("---")
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("### 🔍 Advanced Filter & Search")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔎 Search tasks by name or description:", "", placeholder="Type to search...")
    
    with col2:
        status_filter = st.multiselect(
            "Filter by Status:",
            options=df['Status'].unique(),
            default=df['Status'].unique()
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by:",
            options=["Status", "Task", "Description"],
            index=0
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = df[df['Status'].isin(status_filter)]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Task'].str.contains(search_term, case=False, na=False) |
            filtered_df['Description'].str.contains(search_term, case=False, na=False)
        ]
    
    # Sort data
    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=sort_by)
    
    # Display Tasks
    st.markdown(f"### 📋 Task List ({len(filtered_df)} items)")
    
    if len(filtered_df) > 0:
        # Group by status for better organization
        for status in filtered_df['Status'].unique():
            status_tasks = filtered_df[filtered_df['Status'] == status]
            
            with st.expander(f"{get_status_emoji(status)} {status} ({len(status_tasks)} tasks)", expanded=True):
                for idx, row in status_tasks.iterrows():
                    task = row['Task'] if pd.notna(row['Task']) else 'Untitled Task'
                    description = row['Description'] if pd.notna(row['Description']) else 'No description provided'
                    task_status = row['Status'] if pd.notna(row['Status']) else 'Pending'
                    
                    status_class = get_status_class(task_status)
                    status_emoji = get_status_emoji(task_status)
                    
                    st.markdown(f"""
                    <div class="task-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <div class="task-title">{status_emoji} {task}</div>
                                <div class="task-description">{description}</div>
                            </div>
                            <div>
                                <span class="status-badge {status_class}">{task_status}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("🔍 No tasks match your current filters. Try adjusting your search criteria.")
    
    # Detailed Data Table
    st.markdown("---")
    st.markdown("### 📊 Detailed Data View")
    
    with st.expander("📊 View Complete Data Table", expanded=False):
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400
        )
        
        # Column statistics
        st.markdown("#### 📈 Column Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Rows", len(filtered_df))
        with col2:
            st.metric("Total Columns", len(filtered_df.columns))
        with col3:
            st.metric("Unique Statuses", filtered_df['Status'].nunique())
    
    # Analytics Section
    st.markdown("---")
    st.markdown("### 📊 Advanced Analytics Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Completion Rate",
            f"{completion_percentage:.1f}%",
            delta=f"{completed} completed",
            delta_color="normal"
        )
    
    with col2:
        active_tasks = in_progress + todo
        st.metric(
            "Active Tasks",
            active_tasks,
            delta=f"{in_progress} in progress",
            delta_color="normal"
        )
    
    with col3:
        avg_per_status = total_tasks / len(df['Status'].unique()) if len(df['Status'].unique()) > 0 else 0
        st.metric(
            "Avg per Status",
            f"{avg_per_status:.1f}",
            delta="tasks",
            delta_color="off"
        )
    
    with col4:
        remaining_percentage = ((total_tasks - completed) / total_tasks * 100) if total_tasks > 0 else 0
        st.metric(
            "Remaining",
            f"{remaining_percentage:.1f}%",
            delta=f"{total_tasks - completed} tasks",
            delta_color="inverse"
        )
    
    # Timeline view
    st.markdown("### 📅 Task Timeline & Distribution")
    timeline_fig = go.Figure()
    
    status_colors = {
        'Completed': '#48bb78',
        'In Progress': '#ed8936',
        'To Do': '#4299e1',
        'Pending': '#f56565'
    }
    
    for status in df['Status'].unique():
        status_tasks = df[df['Status'] == status]
        color = status_colors.get(status, '#667eea')
        
        timeline_fig.add_trace(go.Bar(
            name=status,
            x=[status],
            y=[len(status_tasks)],
            text=[len(status_tasks)],
            textposition='auto',
            marker_color=color,
            hovertemplate=f'<b>{status}</b><br>Tasks: %{{y}}<extra></extra>'
        ))
    
    timeline_fig.update_layout(
        barmode='group',
        height=350,
        showlegend=True,
        xaxis_title="Status Category",
        yaxis_title="Number of Tasks",
        hovermode='x unified',
        margin=dict(t=40, b=40)
    )
    
    st.plotly_chart(timeline_fig, use_container_width=True)
    
    # Heatmap for task density
    st.markdown("### 🔥 Task Density Heatmap")
    
    if 'Priority' in df.columns or 'Category' in df.columns:
        # Create a heatmap if we have additional dimensions
        st.info("📊 Heatmap visualization requires Priority or Category columns in your data.")
    else:
        # Create a simple status-based heatmap
        status_matrix = pd.DataFrame({
            'Status': df['Status'].unique(),
            'Count': [len(df[df['Status'] == s]) for s in df['Status'].unique()]
        })
        
        fig_heatmap = px.density_heatmap(
            df,
            x='Status',
            color_continuous_scale='Viridis'
        )
        fig_heatmap.update_layout(height=300, margin=dict(t=40, b=40))
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Export options
    st.markdown("---")
    st.markdown("### 💾 Export & Share Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
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
        json_data = filtered_df.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        excel_buffer = filtered_df.to_html(index=False)
        st.download_button(
            label="📥 Download HTML",
            data=excel_buffer,
            file_name=f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            use_container_width=True
        )
    
    with col4:
        if st.button("🔗 Open Google Sheet", use_container_width=True):
            st.markdown('[Click here to open the Google Sheet](https://docs.google.com/spreadsheets/d/1OZC_Wk4rQZqzhdCwzEHXjbsQUsih3G0uaAaTf-svAds/edit?usp=sharing)', unsafe_allow_html=True)
    
    # Summary Report Section
    st.markdown("---")
    st.markdown("### 📝 Executive Summary Report")
    
    summary_col1, summary_col2 = st.columns([2, 1])
    
    with summary_col1:
        st.markdown(f"""
        <div class="stats-container">
            <h4>📊 Performance Summary</h4>
            <p><strong>Total Tasks:</strong> {total_tasks}</p>
            <p><strong>Completed Tasks:</strong> {completed} ({completion_percentage:.1f}%)</p>
            <p><strong>In Progress:</strong> {in_progress} tasks</p>
            <p><strong>To Do:</strong> {todo} tasks</p>
            <p><strong>Pending:</strong> {pending} tasks</p>
            <hr>
            <p><strong>Productivity Score:</strong> {productivity_score:.0f}/100</p>
            <p><strong>Task Velocity:</strong> {velocity:.1f} tasks per status</p>
            <p><strong>Work Balance:</strong> {distribution_score:.0f}% optimal distribution</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="stats-container">
            <h4>💡 Recommendations</h4>
            <ul>
                <li>Focus on completing in-progress tasks</li>
                <li>Prioritize high-value pending items</li>
                <li>Maintain steady task velocity</li>
                <li>Balance workload across statuses</li>
                <li>Review and update task descriptions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

else:
    st.error("⚠️ Unable to load data from Google Sheets. Please check the sheet ID and permissions.")
    st.info("Make sure the Google Sheet is set to 'Anyone with the link can view'")
    
    # Troubleshooting section
    st.markdown("### 🔧 Troubleshooting")
    st.markdown("""
    <div class="stats-container">
        <h5>Common Issues:</h5>
        <ol>
            <li><strong>Sheet not accessible:</strong> Ensure sharing settings allow public access</li>
            <li><strong>Wrong sheet ID:</strong> Verify the sheet ID in the URL</li>
            <li><strong>Network issues:</strong> Check your internet connection</li>
            <li><strong>API limits:</strong> Google Sheets may have rate limits</li>
        </ol>
        <p><strong>Current Sheet ID:</strong> 1OZC_Wk4rQZqzhdCwzEHXjbsQUsih3G0uaAaTf-svAds</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 2rem;'>
    <h4>🚀 Advanced Task Management System</h4>
    <p>🔗 <strong>Connected to Google Sheets</strong> | 🔄 Auto-refreshes every 60 seconds | 💬 AI-Powered Chat Assistant</p>
    <p>🔔 <strong>Webhook Integration:</strong> Real-time notifications enabled</p>
    <p style='font-size: 0.85rem; opacity: 0.8; margin-top: 1rem;'>
        Built with Streamlit • Powered by Plotly • Data updates in real-time<br>
        📊 Analytics Dashboard • 🤖 AI Assistant • 🔗 Webhook Integration
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh functionality
if auto_refresh:
    import time
    time.sleep(60)
    st.rerun()

