"""
Jira API Client for fetching weekly tasks.
"""
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


def get_monday_of_current_week() -> datetime:
    """
    Get the most recent Monday at 00:00:00.
    If today is Monday, returns today at 00:00:00.
    """
    today = datetime.now()
    days_since_monday = today.weekday()  # Monday = 0
    monday = today - timedelta(days=days_since_monday)
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def format_date_for_jql(dt: datetime) -> str:
    """Format datetime for JQL query (YYYY-MM-DD)."""
    return dt.strftime("%Y-%m-%d")


def build_weekly_tasks_jql(monday_date: datetime) -> str:
    """
    Build JQL query to fetch tasks assigned to current user
    that were updated since the given Monday.
    """
    date_str = format_date_for_jql(monday_date)
    jql = f'assignee = currentUser() AND updated >= "{date_str}" ORDER BY status ASC, updated DESC'
    return jql


class JiraClient:
    """Client for interacting with Jira Cloud REST API."""
    
    def __init__(self, domain: str, email: str, api_token: str):
        """
        Initialize Jira client.
        
        Args:
            domain: Jira domain (e.g., 'yourcompany.atlassian.net')
            email: User email for authentication
            api_token: Atlassian API token
        """
        self.domain = domain.rstrip('/')
        if not self.domain.startswith('https://'):
            self.domain = f'https://{self.domain}'
        self.email = email
        self.api_token = api_token
        self.base_url = f'{self.domain}/rest/api/3'
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection by fetching current user info.
        
        Returns:
            User info dict or raises exception on failure.
        """
        url = f'{self.base_url}/myself'
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def search_issues(self, jql: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search for issues using JQL with pagination support.
        Uses the /jql endpoint as required by current Jira Cloud API.
        
        Args:
            jql: JQL query string
            max_results: Maximum results per page
            
        Returns:
            List of issue dictionaries
        """
        url = f'{self.base_url}/search/jql'
        all_issues = []
        next_page_token = None
        
        while True:
            params = {
                'jql': jql,
                'maxResults': max_results,
                'fields': 'summary,status,priority,created,updated,description,issuetype,project'
            }
            
            if next_page_token:
                params['nextPageToken'] = next_page_token
            
            response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            issues = data.get('issues', [])
            all_issues.extend(issues)
            
            # Check if we have more pages using nextPageToken
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
        
        return all_issues
    
    def get_weekly_tasks(self) -> List[Dict[str, Any]]:
        """
        Fetch all tasks assigned to current user for the current week.
        
        Returns:
            List of parsed task dictionaries
        """
        monday = get_monday_of_current_week()
        jql = build_weekly_tasks_jql(monday)
        raw_issues = self.search_issues(jql)
        return [self._parse_issue(issue) for issue in raw_issues]
    
    def _parse_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw Jira issue into a cleaner format.
        
        Args:
            issue: Raw issue from Jira API
            
        Returns:
            Parsed issue dictionary
        """
        fields = issue.get('fields', {})
        
        # Extract description text from Atlassian Document Format (ADF)
        description = self._extract_text_from_adf(fields.get('description'))
        
        # Get status details
        status = fields.get('status', {})
        status_name = status.get('name', 'Unknown')
        status_category = status.get('statusCategory', {}).get('name', 'Unknown')
        
        # Get priority
        priority = fields.get('priority', {})
        priority_name = priority.get('name', 'None')
        
        # Get issue type
        issue_type = fields.get('issuetype', {})
        issue_type_name = issue_type.get('name', 'Task')
        
        # Get project
        project = fields.get('project', {})
        project_key = project.get('key', '')
        project_name = project.get('name', '')
        
        return {
            'key': issue.get('key', ''),
            'summary': fields.get('summary', 'No summary'),
            'status': status_name,
            'status_category': status_category,
            'priority': priority_name,
            'issue_type': issue_type_name,
            'project_key': project_key,
            'project_name': project_name,
            'created': fields.get('created', ''),
            'updated': fields.get('updated', ''),
            'description': description,
            'url': f"{self.domain}/browse/{issue.get('key', '')}"
        }
    
    def _extract_text_from_adf(self, adf: Optional[Dict]) -> str:
        """
        Extract plain text from Atlassian Document Format.
        
        Args:
            adf: ADF document dict
            
        Returns:
            Plain text string
        """
        if not adf:
            return 'No description'
        
        if isinstance(adf, str):
            return adf
        
        text_parts = []
        
        def extract_text(node):
            if isinstance(node, dict):
                if node.get('type') == 'text':
                    text_parts.append(node.get('text', ''))
                for child in node.get('content', []):
                    extract_text(child)
            elif isinstance(node, list):
                for item in node:
                    extract_text(item)
        
        extract_text(adf)
        return ' '.join(text_parts) if text_parts else 'No description'
