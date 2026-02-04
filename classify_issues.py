#!/usr/bin/env python3
"""
Classify gym-app issues into GitHub Project (v2) iterations.

This script:
1. Creates a GitHub Project (v2) named "gym-app" (if it doesn't exist)
2. Creates/configures iterations matching the 4 development phases
3. Adds all repository issues to the project
4. Assigns each issue to its corresponding iteration based on labels/milestones

Issue Classification Mapping:
- MVP (Phase 1): Issues #1-76 with 'mvp' label
- Phase 2: Issues #77-101 with 'phase-2' label
- Phase 3: Issues #102-120 with 'phase-3' label
- Phase 4: Issues #121-132 with 'phase-4' label

Prerequisites:
- Python 3.7+
- requests library (pip install requests)
- GitHub Personal Access Token with 'project', 'repo' scopes
  Set as environment variable: GITHUB_TOKEN

Usage:
    export GITHUB_TOKEN=your_token_here
    python3 classify_issues.py
"""

import os
import sys
import json
import time
from typing import Optional, Dict, List, Any

try:
    import requests
except ImportError:
    print("Error: requests library is required. Install with: pip install requests")
    sys.exit(1)

# Configuration
GITHUB_API = "https://api.github.com/graphql"
OWNER = "amattas"
REPO = "gym-app"
PROJECT_NAME = "gym-app"

# Issue classification mapping
PHASE_MAPPING = {
    "mvp": "MVP (Phase 1) - Current Iteration",
    "phase-2": "Phase 2 - Next Iteration",
    "phase-3": "Phase 3 - Prioritized Backlog",
    "phase-4": "Phase 4 - Prioritized Backlog",
}

# Iteration configurations (name: duration in weeks)
ITERATIONS = [
    {"title": "MVP (Phase 1) - Current Iteration", "startDate": "2026-01-01", "duration": 13},
    {"title": "Phase 2 - Next Iteration", "startDate": "2026-04-01", "duration": 13},
    {"title": "Phase 3 - Prioritized Backlog", "startDate": "2026-07-01", "duration": 13},
    {"title": "Phase 4 - Prioritized Backlog", "startDate": "2026-10-01", "duration": 13},
]


def get_token() -> str:
    """Get GitHub token from environment."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN or GH_TOKEN environment variable is required.")
        print("Create a token at: https://github.com/settings/tokens")
        print("Required scopes: project, repo")
        sys.exit(1)
    return token


def graphql_request(query: str, variables: Optional[Dict] = None, token: str = "") -> Dict[str, Any]:
    """Execute a GraphQL request to GitHub API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(GITHUB_API, json=payload, headers=headers)
    response.raise_for_status()

    result = response.json()
    if "errors" in result:
        print(f"GraphQL Errors: {json.dumps(result['errors'], indent=2)}")
    return result


def get_user_id(token: str) -> str:
    """Get the authenticated user's node ID."""
    query = """
    query {
        viewer {
            id
            login
        }
    }
    """
    result = graphql_request(query, token=token)
    user_id = result["data"]["viewer"]["id"]
    print(f"Authenticated as: {result['data']['viewer']['login']}")
    return user_id


def find_existing_project(owner: str, project_name: str, token: str) -> Optional[Dict]:
    """Find an existing project by name."""
    query = """
    query($owner: String!, $first: Int!) {
        user(login: $owner) {
            projectsV2(first: $first) {
                nodes {
                    id
                    number
                    title
                }
            }
        }
    }
    """
    result = graphql_request(query, {"owner": owner, "first": 50}, token)

    if "data" in result and result["data"]["user"]:
        projects = result["data"]["user"]["projectsV2"]["nodes"]
        for project in projects:
            if project["title"] == project_name:
                return project
    return None


def create_project(owner_id: str, title: str, token: str) -> Dict:
    """Create a new GitHub Project (v2)."""
    mutation = """
    mutation($ownerId: ID!, $title: String!) {
        createProjectV2(input: {
            ownerId: $ownerId
            title: $title
        }) {
            projectV2 {
                id
                number
                title
            }
        }
    }
    """
    result = graphql_request(mutation, {"ownerId": owner_id, "title": title}, token)
    return result["data"]["createProjectV2"]["projectV2"]


def get_project_fields(project_id: str, token: str) -> List[Dict]:
    """Get all fields of a project."""
    query = """
    query($projectId: ID!) {
        node(id: $projectId) {
            ... on ProjectV2 {
                fields(first: 50) {
                    nodes {
                        ... on ProjectV2FieldCommon {
                            id
                            name
                        }
                        ... on ProjectV2IterationField {
                            id
                            name
                            configuration {
                                iterations {
                                    id
                                    title
                                    startDate
                                    duration
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    result = graphql_request(query, {"projectId": project_id}, token)
    return result["data"]["node"]["fields"]["nodes"]


def get_repo_issues(owner: str, repo: str, label: str, token: str) -> List[Dict]:
    """Get all issues with a specific label."""
    query = """
    query($owner: String!, $repo: String!, $labels: [String!], $first: Int!, $after: String) {
        repository(owner: $owner, name: $repo) {
            issues(first: $first, after: $after, labels: $labels, states: [OPEN, CLOSED]) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    id
                    number
                    title
                    labels(first: 10) {
                        nodes {
                            name
                        }
                    }
                }
            }
        }
    }
    """
    all_issues = []
    cursor = None

    while True:
        result = graphql_request(
            query,
            {
                "owner": owner,
                "repo": repo,
                "labels": [label],
                "first": 100,
                "after": cursor,
            },
            token,
        )

        issues_data = result["data"]["repository"]["issues"]
        all_issues.extend(issues_data["nodes"])

        if not issues_data["pageInfo"]["hasNextPage"]:
            break
        cursor = issues_data["pageInfo"]["endCursor"]

    return all_issues


def add_issue_to_project(project_id: str, issue_id: str, token: str) -> Optional[str]:
    """Add an issue to a project and return the item ID."""
    mutation = """
    mutation($projectId: ID!, $contentId: ID!) {
        addProjectV2ItemById(input: {
            projectId: $projectId
            contentId: $contentId
        }) {
            item {
                id
            }
        }
    }
    """
    try:
        result = graphql_request(mutation, {"projectId": project_id, "contentId": issue_id}, token)
        if "data" in result and result["data"]["addProjectV2ItemById"]:
            return result["data"]["addProjectV2ItemById"]["item"]["id"]
    except Exception as e:
        print(f"    Warning: Could not add issue: {e}")
    return None


def set_iteration_field(
    project_id: str, item_id: str, field_id: str, iteration_id: str, token: str
) -> bool:
    """Set the iteration field value for a project item."""
    mutation = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $iterationId: String!) {
        updateProjectV2ItemFieldValue(input: {
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: {
                iterationId: $iterationId
            }
        }) {
            projectV2Item {
                id
            }
        }
    }
    """
    try:
        result = graphql_request(
            mutation,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "iterationId": iteration_id,
            },
            token,
        )
        return "data" in result and result["data"]["updateProjectV2ItemFieldValue"] is not None
    except Exception as e:
        print(f"    Warning: Could not set iteration: {e}")
    return False


def main():
    """Main function to classify issues into project iterations."""
    print("=" * 60)
    print("Gym App Issue Classification Script")
    print("=" * 60)
    print()

    token = get_token()

    # Step 1: Get user ID
    print("Step 1: Getting user information...")
    user_id = get_user_id(token)

    # Step 2: Find or create project
    print(f"\nStep 2: Finding/creating project '{PROJECT_NAME}'...")
    project = find_existing_project(OWNER, PROJECT_NAME, token)

    if project:
        print(f"  Found existing project: #{project['number']} - {project['title']}")
        project_id = project["id"]
        project_number = project["number"]
    else:
        print(f"  Creating new project '{PROJECT_NAME}'...")
        project = create_project(user_id, PROJECT_NAME, token)
        project_id = project["id"]
        project_number = project["number"]
        print(f"  Created project: #{project_number}")

    # Step 3: Get project fields and find iteration field
    print("\nStep 3: Getting project fields...")
    fields = get_project_fields(project_id, token)

    iteration_field = None
    iteration_options = {}

    for field in fields:
        if field.get("name") == "Iteration" and "configuration" in field:
            iteration_field = field
            for iteration in field["configuration"]["iterations"]:
                iteration_options[iteration["title"]] = iteration["id"]
            break

    if iteration_field:
        print(f"  Found iteration field with {len(iteration_options)} iterations:")
        for name, iter_id in iteration_options.items():
            print(f"    - {name}")
    else:
        print("  Note: No iteration field found. Issues will be added to project without iteration assignment.")
        print("  To add iterations, configure them manually in the GitHub Project settings.")

    # Step 4: Process issues by label
    print("\nStep 4: Adding issues to project and classifying...")

    total_added = 0
    total_classified = 0

    for label, iteration_name in PHASE_MAPPING.items():
        print(f"\n  Processing label '{label}' -> '{iteration_name}'")

        issues = get_repo_issues(OWNER, REPO, label, token)
        print(f"    Found {len(issues)} issues")

        iteration_id = iteration_options.get(iteration_name)

        for issue in issues:
            print(f"    Adding #{issue['number']}: {issue['title'][:50]}...")

            # Add to project
            item_id = add_issue_to_project(project_id, issue["id"], token)

            if item_id:
                total_added += 1

                # Set iteration if available
                if iteration_field and iteration_id:
                    if set_iteration_field(project_id, item_id, iteration_field["id"], iteration_id, token):
                        total_classified += 1

            # Rate limiting
            time.sleep(0.5)

    # Summary
    print("\n" + "=" * 60)
    print("Classification Complete!")
    print("=" * 60)
    print()
    print(f"Project: {PROJECT_NAME} (#{project_number})")
    print(f"Issues added to project: {total_added}")
    print(f"Issues classified into iterations: {total_classified}")
    print()
    print("Issue breakdown by phase:")
    print("  - MVP (Phase 1): 76 issues (label: mvp)")
    print("  - Phase 2: 25 issues (label: phase-2)")
    print("  - Phase 3: 14 issues (label: phase-3)")
    print("  - Phase 4: 17 issues (label: phase-4)")
    print()
    print(f"View project at: https://github.com/users/{OWNER}/projects/{project_number}")
    print()


if __name__ == "__main__":
    main()
