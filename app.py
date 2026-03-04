"""
Streamlit Web App for Jira Weekly Tasks Dashboard.
"""
import streamlit as st
from datetime import datetime
from jira_client import JiraClient, get_monday_of_current_week
from typing import List, Dict, Any

# Page configuration
st.set_page_config(
    page_title="Jira Weekly Tasks",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .status-badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
    }
    .status-todo { background-color: #DFE1E6; color: #42526E; }
    .status-inprogress { background-color: #DEEBFF; color: #0747A6; }
    .status-done { background-color: #E3FCEF; color: #006644; }
    .status-blocked { background-color: #FFEBE6; color: #BF2600; }
    .status-review { background-color: #EAE6FF; color: #403294; }
    .status-other { background-color: #F4F5F7; color: #42526E; }
    
    .priority-highest { color: #BF2600; }
    .priority-high { color: #DE350B; }
    .priority-medium { color: #FF8B00; }
    .priority-low { color: #0065FF; }
    .priority-lowest { color: #00875A; }
    
    .task-card {
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #DFE1E6;
        margin-bottom: 8px;
        background-color: #FAFBFC;
    }
    
    .metric-card {
        text-align: center;
        padding: 16px;
        border-radius: 8px;
        background-color: #F4F5F7;
    }
    
    .week-header {
        font-size: 14px;
        color: #6B778C;
        margin-bottom: 8px;
    }
    
    div[data-testid="stExpander"] {
        border: 1px solid #DFE1E6;
        border-radius: 8px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


def get_status_class(status: str) -> str:
    """Get CSS class for status badge."""
    status_lower = status.lower()
    if 'done' in status_lower or 'complete' in status_lower or 'closed' in status_lower:
        return 'status-done'
    elif 'progress' in status_lower or 'doing' in status_lower:
        return 'status-inprogress'
    elif 'todo' in status_lower or 'to do' in status_lower or 'open' in status_lower or 'backlog' in status_lower:
        return 'status-todo'
    elif 'block' in status_lower or 'impediment' in status_lower:
        return 'status-blocked'
    elif 'review' in status_lower or 'testing' in status_lower:
        return 'status-review'
    else:
        return 'status-other'


def get_status_category_order(status_category: str) -> int:
    """Get sort order for status categories."""
    order = {
        'To Do': 1,
        'In Progress': 2,
        'Done': 3
    }
    return order.get(status_category, 2)


def get_priority_icon(priority: str) -> str:
    """Get icon for priority level."""
    priority_lower = priority.lower()
    if 'highest' in priority_lower:
        return '🔴'
    elif 'high' in priority_lower:
        return '🟠'
    elif 'medium' in priority_lower:
        return '🟡'
    elif 'low' in priority_lower:
        return '🟢'
    elif 'lowest' in priority_lower:
        return '⚪'
    return '⚪'


def format_datetime(dt_str: str) -> str:
    """Format ISO datetime string to readable format."""
    if not dt_str:
        return 'N/A'
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%b %d, %Y %H:%M')
    except:
        return dt_str


def render_status_badge(status: str) -> str:
    """Render HTML status badge."""
    css_class = get_status_class(status)
    return f'<span class="status-badge {css_class}">{status}</span>'


def filter_tasks(tasks: List[Dict], search_query: str) -> List[Dict]:
    """Filter tasks by search query."""
    if not search_query:
        return tasks
    
    query = search_query.lower()
    filtered = []
    for task in tasks:
        if (query in task['key'].lower() or 
            query in task['summary'].lower() or
            query in task['project_name'].lower()):
            filtered.append(task)
    return filtered


def group_tasks_by_status(tasks: List[Dict]) -> Dict[str, List[Dict]]:
    """Group tasks by their status."""
    groups = {}
    for task in tasks:
        status = task['status']
        if status not in groups:
            groups[status] = []
        groups[status].append(task)
    return groups


def render_task_card(task: Dict[str, Any]):
    """Render a single task as an expandable card."""
    priority_icon = get_priority_icon(task['priority'])
    status_badge = render_status_badge(task['status'])
    
    # Create expander with task summary
    with st.expander(f"{priority_icon} **{task['key']}** - {task['summary']}", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Status:** {status_badge}", unsafe_allow_html=True)
            st.markdown(f"**Priority:** {priority_icon} {task['priority']}")
            st.markdown(f"**Type:** {task['issue_type']}")
            st.markdown(f"**Project:** {task['project_name']} ({task['project_key']})")
        
        with col2:
            st.markdown(f"**Created:** {format_datetime(task['created'])}")
            st.markdown(f"**Updated:** {format_datetime(task['updated'])}")
        
        st.divider()
        st.markdown("**Description:**")
        description = task['description']
        if len(description) > 500:
            description = description[:500] + "..."
        st.markdown(description)
        
        st.divider()
        st.link_button("🔗 Open in Jira", task['url'], use_container_width=True)


def render_metrics(tasks: List[Dict]):
    """Render metrics row showing task counts by status category."""
    # Count by status category
    todo_count = sum(1 for t in tasks if t['status_category'] == 'To Do')
    in_progress_count = sum(1 for t in tasks if t['status_category'] == 'In Progress')
    done_count = sum(1 for t in tasks if t['status_category'] == 'Done')
    total = len(tasks)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Tasks", total)
    with col2:
        st.metric("📋 To Do", todo_count)
    with col3:
        st.metric("🔄 In Progress", in_progress_count)
    with col4:
        st.metric("✅ Done", done_count)


def main():
    """Main application entry point."""
    
    # Header
    st.title("📋 Jira Weekly Tasks Dashboard")
    
    # Calculate and display week range
    monday = get_monday_of_current_week()
    today = datetime.now()
    st.markdown(
        f'<p class="week-header">Showing tasks from <strong>{monday.strftime("%B %d, %Y")}</strong> '
        f'to <strong>{today.strftime("%B %d, %Y %H:%M")}</strong></p>',
        unsafe_allow_html=True
    )
    
    # Sidebar for credentials
    with st.sidebar:
        st.header("🔐 Jira Connection")
        
        jira_domain = st.text_input(
            "Jira Domain",
            value="yourcompany.atlassian.net",
            placeholder="yourcompany.atlassian.net",
            help="Your Jira Cloud domain"
        )
        
        jira_email = st.text_input(
            "Email",
            placeholder="your.email@company.com",
            help="Your Atlassian account email"
        )
        
        jira_token = st.text_input(
            "API Token",
            type="password",
            placeholder="Your Atlassian API token",
            help="Generate at: https://id.atlassian.com/manage-profile/security/api-tokens"
        )
        
        fetch_button = st.button("🔄 Fetch Tasks", use_container_width=True, type="primary")
        
        st.divider()
        st.markdown("### ℹ️ How to get an API Token")
        st.markdown("""
        1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
        2. Click **Create API token**
        3. Give it a label and copy the token
        """)
    
    # Initialize session state
    if 'tasks' not in st.session_state:
        st.session_state.tasks = None
    if 'error' not in st.session_state:
        st.session_state.error = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    # Fetch tasks when button is clicked
    if fetch_button:
        if not jira_domain or not jira_email or not jira_token:
            st.error("Please fill in all credential fields.")
        else:
            with st.spinner("Connecting to Jira and fetching tasks..."):
                try:
                    client = JiraClient(jira_domain, jira_email, jira_token)
                    
                    # Test connection
                    user_info = client.test_connection()
                    st.session_state.user_info = user_info
                    
                    # Fetch tasks
                    tasks = client.get_weekly_tasks()
                    st.session_state.tasks = tasks
                    st.session_state.error = None
                    
                    st.success(f"✅ Connected as {user_info.get('displayName', 'User')}. Found {len(tasks)} tasks.")
                    
                except Exception as e:
                    st.session_state.error = str(e)
                    st.session_state.tasks = None
                    st.error(f"❌ Error connecting to Jira: {str(e)}")
    
    # Display tasks if available
    if st.session_state.tasks is not None:
        tasks = st.session_state.tasks
        
        if len(tasks) == 0:
            st.info("🎉 No tasks found for this week. Enjoy your free time!")
        else:
            # Search/filter bar
            st.divider()
            search_query = st.text_input(
                "🔍 Search tasks",
                placeholder="Search by key, summary, or project...",
                help="Filter tasks by typing keywords"
            )
            
            # Filter tasks
            filtered_tasks = filter_tasks(tasks, search_query)
            
            # Render metrics
            render_metrics(filtered_tasks)
            
            st.divider()
            
            if len(filtered_tasks) == 0:
                st.warning("No tasks match your search criteria.")
            else:
                # Group tasks by status
                grouped = group_tasks_by_status(filtered_tasks)
                
                # Sort groups by status category order
                sorted_statuses = sorted(
                    grouped.keys(),
                    key=lambda s: (
                        get_status_category_order(
                            next((t['status_category'] for t in grouped[s]), 'In Progress')
                        ),
                        s
                    )
                )
                
                # Render each status group
                for status in sorted_statuses:
                    status_tasks = grouped[status]
                    status_badge = render_status_badge(status)
                    
                    st.markdown(
                        f"### {status_badge} <span style='font-size: 16px; color: #6B778C;'>({len(status_tasks)} tasks)</span>",
                        unsafe_allow_html=True
                    )
                    
                    for task in status_tasks:
                        render_task_card(task)
                    
                    st.markdown("")  # Spacing
    
    elif st.session_state.error:
        st.error(f"❌ {st.session_state.error}")
    
    else:
        # Welcome message when no tasks loaded
        st.info("👈 Enter your Jira credentials in the sidebar and click **Fetch Tasks** to get started.")
        
        # Show sample UI
        st.markdown("---")
        st.markdown("### 📖 What you'll see:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **📊 Metrics Overview**
            - Total task count
            - Tasks by status category
            """)
        with col2:
            st.markdown("""
            **🔍 Search & Filter**
            - Filter by task key
            - Search by summary
            - Filter by project
            """)
        with col3:
            st.markdown("""
            **📋 Task Details**
            - Expandable task cards
            - Priority indicators
            - Direct links to Jira
            """)


if __name__ == "__main__":
    main()
