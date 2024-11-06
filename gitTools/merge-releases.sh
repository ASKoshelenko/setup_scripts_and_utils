#!/bin/bash

# Create backup of current state
create_backup() {
    local BACKUP_TAG="backup-$(date +%Y%m%d-%H%M%S)"
    echo "Creating backup tag: $BACKUP_TAG"
    git tag -a "$BACKUP_TAG" -m "Backup before release consolidation" || {
        echo "Failed to create backup tag"
        exit 1
    }
    git push origin "$BACKUP_TAG" || {
        echo "Failed to push backup tag"
        exit 1
    }
    echo "Backup created successfully: $BACKUP_TAG"
    echo "To restore this backup later, use: git reset --hard $BACKUP_TAG"
}

# Initialize master branch from the first commit
init_master() {
    echo "Initializing master branch from first commit..."
    git checkout --orphan master 9e38cb7 || {
        echo "Failed to create master branch"
        exit 1
    }
    git reset --hard 9e38cb7 || {
        echo "Failed to reset master to initial commit"
        exit 1
    }
    git push -f origin master || {
        echo "Failed to push master branch"
        exit 1
    }
}

# Function to check if branch exists
check_branch() {
    local BRANCH_NAME=$1
    git rev-parse --verify "origin/$BRANCH_NAME" >/dev/null 2>&1
    return $?
}

# Function to merge a branch into master
merge_branch() {
    local BRANCH_NAME=$1
    local TAG=$(echo "$BRANCH_NAME" | sed 's/.*\///')
    
    echo "Processing branch: $BRANCH_NAME with tag: $TAG"
    
    # Check if branch exists
    if ! check_branch "$BRANCH_NAME"; then
        echo "Branch $BRANCH_NAME does not exist! Skipping..."
        return 1
    fi
    
    # Create temporary tag before merge for potential rollback
    local TEMP_TAG="pre-merge-$TAG-$(date +%s)"
    git tag "$TEMP_TAG" || {
        echo "Failed to create temporary tag"
        return 1
    }
    
    # Ensure we're on master
    echo "Checking out master..."
    git checkout master || {
        echo "Failed to checkout master"
        git tag -d "$TEMP_TAG"
        return 1
    }
    
    # Merge the release branch
    echo "Merging $BRANCH_NAME into master..."
    if ! git merge -X theirs "origin/$BRANCH_NAME" -m "Merge branch '$BRANCH_NAME' into master"; then
        echo "Merge failed! Rolling back to $TEMP_TAG..."
        git reset --hard "$TEMP_TAG"
        git tag -d "$TEMP_TAG"
        return 1
    fi
    
    # Create and push version tag
    echo "Creating tag $TAG..."
    if ! git tag -a "$TAG" -m "Version $TAG"; then
        echo "Failed to create version tag! Rolling back..."
        git reset --hard "$TEMP_TAG"
        git tag -d "$TEMP_TAG"
        return 1
    fi
    
    # Push changes
    if ! git push origin master && git push origin "$TAG"; then
        echo "Failed to push changes! Rolling back..."
        git reset --hard "$TEMP_TAG"
        git tag -d "$TAG"
        git tag -d "$TEMP_TAG"
        return 1
    fi
    
    # Clean up temporary tag
    git tag -d "$TEMP_TAG"
    
    # Delete remote branch only if everything succeeded
    echo "Deleting remote branch $BRANCH_NAME..."
    git push origin --delete "$BRANCH_NAME" || echo "Warning: Failed to delete remote branch $BRANCH_NAME"
    
    return 0
}

# Main execution
echo "Starting release branch consolidation process..."

# Create backup first
create_backup

# Confirm continuation
read -p "Backup created. Do you want to continue with the consolidation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled by user"
    exit 1
fi

# Initialize master branch
init_master

# Array of branches in correct order
BRANCHES=(
    "release/0.0.1"
    "hotfix/0.0.2"
    "release/1.2.0"
    "release/1.3.0"
    "release/1.4.0"
    "release/1.5.0"
    "release/1.6.0"
    "release/1.7.0"
    "release/1.8.0"
    "release/1.9.0"
    "release/1.10.0"
    "release/1.11.0"
    # "release/1.12.0"
    # "release/1.13.0"
    # "release/1.14.0"
)

# Process each branch in order
for branch in "${BRANCHES[@]}"; do
    echo "Processing $branch..."
    if ! merge_branch "$branch"; then
        echo "Failed to process $branch"
        echo "You can restore to the backup tag or continue with the next branch"
        read -p "Continue with next branch? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Operation cancelled by user"
            exit 1
        fi
    fi
done

echo "Branch consolidation completed successfully!"
echo "A backup tag was created at the start of this process."
echo "If you need to rollback the entire operation, use git tag -l 'backup-*' to find the backup tag"
echo "and then use: git reset --hard <backup-tag>"