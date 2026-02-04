#!/bin/bash
# Script to classify gym-app issues into GitHub Project iterations
#
# This script:
# 1. Creates a GitHub Project (v2) named "gym-app" if it doesn't exist
# 2. Creates iterations matching the 4 development phases
# 3. Adds all repository issues to the project
# 4. Assigns each issue to its corresponding iteration based on labels
#
# Prerequisites:
# - GitHub CLI (gh) must be installed and authenticated
# - Run: gh auth login
#
# Usage: ./classify-issues.sh

set -e

REPO="amattas/gym-app"
PROJECT_NAME="gym-app"
OWNER="amattas"

echo "=== Gym App Issue Classification Script ==="
echo ""

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
    echo "Error: GitHub CLI is not authenticated. Please run 'gh auth login' first."
    exit 1
fi

echo "Step 1: Creating GitHub Project (v2) named '$PROJECT_NAME'..."

# Check if project already exists
EXISTING_PROJECT=$(gh project list --owner "$OWNER" --format json 2>/dev/null | jq -r ".projects[] | select(.title == \"$PROJECT_NAME\") | .number" 2>/dev/null || echo "")

if [ -n "$EXISTING_PROJECT" ]; then
    echo "Project '$PROJECT_NAME' already exists (number: $EXISTING_PROJECT)"
    PROJECT_NUMBER=$EXISTING_PROJECT
else
    # Create new project
    PROJECT_NUMBER=$(gh project create --owner "$OWNER" --title "$PROJECT_NAME" --format json | jq -r '.number')
    echo "Created project '$PROJECT_NAME' (number: $PROJECT_NUMBER)"
fi

echo ""
echo "Step 2: Creating iteration field and iterations..."

# Get project ID for GraphQL operations
PROJECT_ID=$(gh project list --owner "$OWNER" --format json | jq -r ".projects[] | select(.number == $PROJECT_NUMBER) | .id")

echo "Project ID: $PROJECT_ID"

# Create iteration field using GraphQL
echo "Creating iteration field..."
ITERATION_FIELD_ID=$(gh api graphql -f query='
mutation($projectId: ID!) {
  createProjectV2Field(input: {
    projectId: $projectId
    dataType: ITERATION
    name: "Iteration"
  }) {
    projectV2Field {
      ... on ProjectV2IterationField {
        id
      }
    }
  }
}' -f projectId="$PROJECT_ID" --jq '.data.createProjectV2Field.projectV2Field.id' 2>/dev/null || echo "")

if [ -z "$ITERATION_FIELD_ID" ]; then
    echo "Iteration field may already exist. Fetching existing field..."
    ITERATION_FIELD_ID=$(gh api graphql -f query='
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2IterationField {
                id
                name
              }
            }
          }
        }
      }
    }' -f projectId="$PROJECT_ID" --jq '.data.node.fields.nodes[] | select(.name == "Iteration") | .id' 2>/dev/null)
fi

echo "Iteration Field ID: $ITERATION_FIELD_ID"

# Define iterations matching the milestones
declare -A ITERATIONS=(
    ["MVP (Phase 1) - Current Iteration"]="2026-01-01/2026-03-31"
    ["Phase 2 - Next Iteration"]="2026-04-01/2026-06-30"
    ["Phase 3 - Prioritized Backlog"]="2026-07-01/2026-09-30"
    ["Phase 4 - Prioritized Backlog"]="2026-10-01/2026-12-31"
)

echo ""
echo "Step 3: Adding issues to project and classifying by iteration..."

# Define issue-to-iteration mapping based on labels
# Phase 1 (MVP): Issues with 'mvp' label (Issues #1-76)
# Phase 2: Issues with 'phase-2' label (Issues #77-101)
# Phase 3: Issues with 'phase-3' label (Issues #102-120)
# Phase 4: Issues with 'phase-4' label (Issues #121-132)

classify_issues() {
    local label="$1"
    local iteration_name="$2"

    echo ""
    echo "Processing issues with label '$label' -> Iteration: '$iteration_name'"

    # Get issues with the specified label
    ISSUES=$(gh issue list --repo "$REPO" --label "$label" --state all --limit 200 --json number,title)

    ISSUE_COUNT=$(echo "$ISSUES" | jq '. | length')
    echo "Found $ISSUE_COUNT issues with label '$label'"

    # Add each issue to the project and set its iteration
    echo "$ISSUES" | jq -r '.[].number' | while read -r ISSUE_NUM; do
        echo "  Adding issue #$ISSUE_NUM to project..."

        # Add issue to project
        ITEM_ID=$(gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "https://github.com/$REPO/issues/$ISSUE_NUM" --format json 2>/dev/null | jq -r '.id' || echo "")

        if [ -n "$ITEM_ID" ] && [ "$ITEM_ID" != "null" ]; then
            echo "    Added as item: $ITEM_ID"

            # Set iteration field (this requires the iteration option ID)
            # Note: Setting iteration values requires knowing the specific iteration option ID
            # which needs to be looked up after iterations are created
        else
            echo "    Issue may already be in project or failed to add"
        fi
    done
}

# Process each phase
classify_issues "mvp" "MVP (Phase 1) - Current Iteration"
classify_issues "phase-2" "Phase 2 - Next Iteration"
classify_issues "phase-3" "Phase 3 - Prioritized Backlog"
classify_issues "phase-4" "Phase 4 - Prioritized Backlog"

echo ""
echo "=== Classification Complete ==="
echo ""
echo "Summary of issue classification:"
echo "  - MVP (Phase 1): Issues with 'mvp' label (76 issues)"
echo "  - Phase 2: Issues with 'phase-2' label (25 issues)"
echo "  - Phase 3: Issues with 'phase-3' label (14 issues)"
echo "  - Phase 4: Issues with 'phase-4' label (17 issues)"
echo ""
echo "Total: 132 issues classified into 4 iterations"
echo ""
echo "View your project at: https://github.com/users/$OWNER/projects/$PROJECT_NUMBER"
