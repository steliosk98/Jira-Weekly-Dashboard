# 📋 Jira Weekly Dashboard

A modern Streamlit web application for visualizing and managing your Jira Cloud weekly tasks. Connect with your Jira instance to get a personalized dashboard showing all tasks assigned to you this week, organized by status with powerful filtering and search capabilities.

## 🌟 Features

- **Weekly Task Overview**: Automatically fetches all tasks assigned to you since the start of the current week (Monday)
- **Status Organization**: Tasks grouped and sorted by status (To Do → In Progress → Done)
- **Priority Indicators**: Color-coded priority badges with visual icons (🔴 Highest to ⚪ Lowest)
- **Real-time Metrics**: Dashboard shows total tasks, breakdown by status category at a glance
- **Advanced Search**: Filter tasks by:
  - Task key/ID (e.g., PROJ-123)
  - Task summary/title
  - Project name
- **Expandable Task Cards**: Click to reveal full task details:
  - Complete description
  - Creation and update timestamps
  - Issue type
  - Project information
  - Direct link to Jira
- **Custom Styling**: Professional Jira-inspired UI with color-coded status badges
- **Secure Credential Handling**: Enter credentials directly in the app sidebar (credentials are not saved)
- **Real-time Connection**: Tests connection to Jira before fetching tasks

## 📋 Project Structure

```
Jira-Weekly-Dashboard/
├── app.py                 # Main Streamlit web application
├── jira_client.py         # Jira Cloud API client
├── requirement.txt        # Python dependencies
└── README.md             # This file
```

### Core Components

**`app.py`**
- Streamlit UI implementation with page layout and styling
- Sidebar for credential input and API token instructions
- Task rendering with custom HTML badges and expandable cards
- Search/filter logic
- Metrics display
- Session state management for maintaining tasks across interactions

**`jira_client.py`**
- `JiraClient` class: Manages authentication and API communication with Jira Cloud
- JQL query builder for fetching weekly tasks
- Issue parser: Converts raw Jira API responses to clean dictionaries
- Atlassian Document Format (ADF) text extraction
- Pagination support for large task lists
- Helper functions for date formatting and week calculation

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A Jira Cloud account (www.atlassian.net)
- Jira API token (instructions provided in-app)
- `pip` package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/steliosk98/Jira-Weekly-Dashboard.git
   cd Jira-Weekly-Dashboard
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirement.txt
   ```

### Running the Application

Start the Streamlit app with:
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 🔑 Authentication

### How to Get Your API Token

1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Give your token a descriptive label (e.g., "Jira Weekly Dashboard")
4. Copy the generated token
5. Paste it into the app's sidebar

### Required Credentials

The app requires three pieces of information:

- **Jira Domain**: Your Jira Cloud domain (e.g., `yourcompany.atlassian.net`)
- **Email**: Your Atlassian account email
- **API Token**: Your generated Atlassian API token (treated as a password field in the UI)

## 📊 Usage Guide

### Initial Setup
1. Enter your Jira domain in the sidebar input
2. Enter your email address
3. Paste your API token
4. Click **🔄 Fetch Tasks** button
5. The app will test the connection and fetch your weekly tasks

### Viewing Tasks
- **Metrics Dashboard**: Shows total tasks and breakdown by status
- **Task Cards**: Click to expand and view full details
- **Status Grouping**: Tasks automatically organized by their current status
- **Priority Icons**: Quickly identify high-priority items at a glance

### Filtering and Searching
- Use the search box to filter tasks by:
  - Task key (e.g., "PROJ-123")
  - Keywords in task summary
  - Project name
- Results update in real-time as you type

### Opening in Jira
- Each task card has a **🔗 Open in Jira** button
- Clicking it opens the task in your Jira instance in a new tab

## 🎨 Status & Priority System

### Status Categories

| Status | Meaning |
|--------|---------|
| **To Do** | Task not yet started (includes Open, Backlog) |
| **In Progress** | Task currently being worked on |
| **Done** | Task completed (includes Closed, Complete) |
| **Other** | Custom statuses (e.g., Review, Testing) |

### Priority Levels

| Priority | Icon | Color |
|----------|------|-------|
| **Highest** | 🔴 | Red |
| **High** | 🟠 | Orange |
| **Medium** | 🟡 | Yellow |
| **Low** | 🟢 | Green |
| **Lowest** | ⚪ | Grey |

## 🔧 Technical Details

### JQL Query
The app uses JQL (Jira Query Language) to fetch tasks:
```
assignee = currentUser() AND updated >= "YYYY-MM-DD" ORDER BY status ASC, updated DESC
```

This fetches all tasks:
- Assigned to the current user
- Updated since Monday of the current week
- Sorted by status, then by most recently updated

### Data Processing

1. **Authentication**: HTTP Basic Auth with email and API token
2. **API Endpoint**: Jira Cloud REST API v3 (`/rest/api/3/search/jql`)
3. **Pagination**: Handles large task lists with `nextPageToken`
4. **Description Parsing**: Converts Atlassian Document Format (ADF) to plain text
5. **Session State**: Caches tasks in Streamlit session to avoid re-fetching

### Supported Jira Cloud Fields

- Key & Summary
- Status (with category)
- Priority
- Issue Type
- Project (name & key)
- Created & Updated timestamps
- Description (full text extraction from ADF)

## 📦 Dependencies

- **streamlit** (≥1.28.0): Web app framework and UI components
- **requests** (≥2.31.0): HTTP client for Jira API calls
- **python-dateutil** (≥2.8.2): Date/time manipulation utilities

## 🛠️ Customization

### Styling
Edit the CSS in the `<style>` section of `app.py` to customize:
- Status badge colors
- Priority colors
- Card layouts
- Font sizes and spacing

### JQL Query
Modify the `build_weekly_tasks_jql()` function in `jira_client.py` to change the task filtering logic (e.g., include/exclude certain projects, statuses, or date ranges)

### Task Card Display
Edit the `render_task_card()` function to add or remove fields displayed in the expandable task cards

## 🐛 Troubleshooting

### Connection Errors
- **Invalid credentials**: Verify your email, domain, and API token
- **API token expired**: Generate a new token from Atlassian settings
- **Domain format**: Try both with and without the "https://" prefix

### No Tasks Appear
- Check that you have tasks assigned to you in Jira
- Verify the tasks were updated since Monday of the current week
- Try adjusting the JQL query in `build_weekly_tasks_jql()`

### Description Not Showing
- Some custom fields or rich formatting may not be parsed correctly
- The app extracts text from Atlassian Document Format (ADF)
- If a description appears as "No description", check the original task in Jira

### Search Not Working
- Search is case-insensitive
- Searches across key, summary, and project name
- Try shortened keywords if exact matches don't work

## 🔒 Security Notes

- **Credentials are not saved**: Your email and API token are only used during the session
- **Use API tokens, not passwords**: Never paste your Jira password into the app
- **Keep tokens private**: Regenerate your API token if compromised
- **Local execution recommended**: Run locally rather than on public servers if possible

## 📝 Future Enhancements

Potential improvements for future versions:
- Export to CSV/Excel
- Task filtering by custom JQL
- Create new tasks from the dashboard
- Add time tracking visualization
- Undo/multi-select operations
- Saved search filters
- Dark mode toggle
- Sprint view
- Burndown charts

## 💬 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your Jira API token is correct
3. Ensure your Jira account has the necessary permissions
4. Check the Streamlit logs for detailed error messages

## 📄 License

This project is provided as-is for personal use. Modify and distribute as needed.

## 👤 Author

Created by [steliosk98](https://github.com/steliosk98)

---

**Last Updated**: March 2026
**Version**: 1.0
