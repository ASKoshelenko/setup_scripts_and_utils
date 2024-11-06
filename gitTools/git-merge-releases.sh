#!/bin/bash

###################
### DOCUMENTATION #
###################
# Script: git-merge-releases.sh
# Purpose: Automates the process of merging release and hotfix branches while preserving the latest releases
# Usage: ./git-merge-releases.sh
#
# The script will:
# 1. Create a backup of the current state
# 2. Create a new master branch from initial commit
# 3. Automatically detect and merge all release/hotfix branches in chronological order
# 4. Preserve the specified number of latest releases
# 5. Create version tags for each merged branch
#
# Configuration variables are at the top of the script and can be modified as needed.
#
# Requirements:
# - Git 2.0 or higher
# - Write access to the repository
# - Branch naming format: release/X.X.X or hotfix/X.X.X

###################
### CONFIGURATION #
###################

# Repository specific configuration
INITIAL_COMMIT="9e38cb7"                    # First commit to start from
MASTER_BRANCH="master"                      # Name of the target branch
BACKUP_PREFIX="backup"                      # Prefix for backup tags
REMOTE_NAME="origin"                        # Remote repository name
PRESERVE_COUNT=3                            # Number of latest releases to preserve
LOG_FILE="git-merge-releases.log"           # Log file name

# Git configuration
GIT_MERGE_STRATEGY="theirs"                 # Merge strategy to use
PUSH_FLAGS="--force"                        # Flags for git push

# Messaging configuration
VERBOSE=true                                # Enable/disable detailed output
INTERACTIVE=true                            # Enable/disable interactive prompts

###################
### FUNCTIONS #####
###################

# Function to log messages
log_message() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# Function to check git availability and version
check_git_version() {
    if ! command -v git >/dev/null 2>&1; then
        log_message "ERROR: Git is not installed"
        exit 1
    fi
    
    local git_version=$(git --version | cut -d' ' -f3)
    log_message "Git version: $git_version"
}

# Function to get all release and hotfix branches
get_all_branches() {
    git fetch --all
    git for-each-ref --sort=creatordate --format="%(refname:short)" refs/remotes/$REMOTE_NAME/ | \
        grep -E "^$REMOTE_NAME/(release|hotfix)/" | \
        sed "s|$REMOTE_NAME/||"
}

# Function to get branches to preserve (latest N releases)
get_preserve_branches() {
    git for-each-ref --sort=-version:refname --format="%(refname:short)" refs/remotes/$REMOTE_NAME/ | \
        grep -E "^$REMOTE_NAME/(release|hotfix)/" | \
        sed "s|$REMOTE_NAME/||" | \
        head -n $PRESERVE_COUNT
}

# Function to get branches to merge (all except preserved)
get_merge_branches() {
    local all_branches=$(get_all_branches)
    local preserve_branches=$(get_preserve_branches)
    local merge_branches=()
    
    while read -r branch; do
        local should_preserve=false
        for preserve in $preserve_branches; do
            if [[ "$branch" == "$preserve" ]]; then
                should_preserve=true
                break
            fi
        done
        if [[ "$should_preserve" == "false" ]]; then
            merge_branches+=("$branch")
        fi
    done <<< "$all_branches"
    
    echo "${merge_branches[@]}"
}

# Create backup of current state
create_backup() {
    local BACKUP_TAG="${BACKUP_PREFIX}-$(date +%Y%m%d-%H%M%S)"
    log_message "Creating backup tag: $BACKUP_TAG"
    
    git tag -a "$BACKUP_TAG" -m "Backup before release consolidation" || {
        log_message "ERROR: Failed to create backup tag"
        exit 1
    }
    git push $REMOTE_NAME "$BACKUP_TAG" || {
        log_message "ERROR: Failed to push backup tag"
        exit 1
    }
    
    log_message "Backup created successfully: $BACKUP_TAG"
}

# Initialize master branch from the first commit
init_master() {
    log_message "Initializing $MASTER_BRANCH branch from commit $INITIAL_COMMIT"
    
    git checkout --orphan $MASTER_BRANCH $INITIAL_COMMIT || {
        log_message "ERROR: Failed to create $MASTER_BRANCH branch"
        exit 1
    }
    git reset --hard $INITIAL_COMMIT || {
        log_message "ERROR: Failed to reset $MASTER_BRANCH to initial commit"
        exit 1
    }
    git push $PUSH_FLAGS $REMOTE_NAME $MASTER_BRANCH || {
        log_message "ERROR: Failed to push $MASTER_BRANCH branch"
        exit 1
    }
}

# Function to merge a branch into master
merge_branch() {
    local BRANCH_NAME=$1
    local TAG=$(echo "$BRANCH_NAME" | sed 's/.*\///')
    
    log_message "Processing branch: $BRANCH_NAME with tag: $TAG"
    
    # Create temporary tag for potential rollback
    local TEMP_TAG="pre-merge-$TAG-$(date +%s)"
    git tag "$TEMP_TAG" || {
        log_message "ERROR: Failed to create temporary tag"
        return 1
    }
    
    # Ensure we're on master
    git checkout $MASTER_BRANCH || {
        log_message "ERROR: Failed to checkout $MASTER_BRANCH"
        git tag -d "$TEMP_TAG"
        return 1
    }
    
    # Merge the branch
    if ! git merge -X $GIT_MERGE_STRATEGY "$REMOTE_NAME/$BRANCH_NAME" -m "Merge branch '$BRANCH_NAME' into $MASTER_BRANCH"; then
        log_message "ERROR: Merge failed! Rolling back to $TEMP_TAG"
        git reset --hard "$TEMP_TAG"
        git tag -d "$TEMP_TAG"
        return 1
    fi
    
    # Create version tag
    if ! git tag -a "$TAG" -m "Version $TAG"; then
        log_message "ERROR: Failed to create version tag! Rolling back"
        git reset --hard "$TEMP_TAG"
        git tag -d "$TEMP_TAG"
        return 1
    fi
    
    # Push changes
    if ! git push $REMOTE_NAME $MASTER_BRANCH && git push $REMOTE_NAME "$TAG"; then
        log_message "ERROR: Failed to push changes! Rolling back"
        git reset --hard "$TEMP_TAG"
        git tag -d "$TAG"
        git tag -d "$TEMP_TAG"
        return 1
    fi
    
    # Clean up
    git tag -d "$TEMP_TAG"
    
    return 0
}

# Function to verify branch existence
verify_branches() {
    local missing_branches=0
    local all_branches=$(git branch -r)
    
    for branch in "$@"; do
        if ! echo "$all_branches" | grep -q "$REMOTE_NAME/$branch"; then
            log_message "WARNING: Branch $branch not found"
            missing_branches=$((missing_branches + 1))
        fi
    done
    
    if [ $missing_branches -gt 0 ]; then
        log_message "WARNING: $missing_branches branch(es) are missing"
        return 1
    fi
    return 0
}

###################
### MAIN SCRIPT ###
###################

# Initialize log file
echo "=== Git Merge Releases Script Started at $(date) ===" > "$LOG_FILE"

# Check git version
check_git_version

# Get branches
log_message "Detecting branches..."
PRESERVE_BRANCHES=($(get_preserve_branches))
MERGE_BRANCHES=($(get_merge_branches))

# Verify and display detected branches
log_message "Branches to preserve (${#PRESERVE_BRANCHES[@]}):"
for branch in "${PRESERVE_BRANCHES[@]}"; do
    log_message "  * $branch"
done

log_message "Branches to merge (${#MERGE_BRANCHES[@]}):"
for branch in "${MERGE_BRANCHES[@]}"; do
    log_message "  * $branch"
done

# Verify branches exist
if ! verify_branches "${MERGE_BRANCHES[@]}" "${PRESERVE_BRANCHES[@]}"; then
    if [[ "$INTERACTIVE" == "true" ]]; then
        read -p "Some branches are missing. Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_message "Operation cancelled by user due to missing branches"
            exit 1
        fi
    fi
fi

# Create backup
create_backup

# Confirm continuation
if [[ "$INTERACTIVE" == "true" ]]; then
    read -p "Ready to proceed with branch consolidation. Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_message "Operation cancelled by user"
        exit 1
    fi
fi

# Initialize master branch
init_master

# Process each branch
for branch in "${MERGE_BRANCHES[@]}"; do
    if ! merge_branch "$branch"; then
        log_message "ERROR: Failed to process $branch"
        if [[ "$INTERACTIVE" == "true" ]]; then
            read -p "Continue with next branch? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_message "Operation cancelled by user"
                exit 1
            fi
        else
            log_message "Operation cancelled due to merge failure"
            exit 1
        fi
    fi
done

# Final report
log_message "Branch consolidation completed successfully!"
log_message "Summary:"
log_message "- Merged ${#MERGE_BRANCHES[@]} branches"
log_message "- Preserved ${#PRESERVE_BRANCHES[@]} branches"
log_message "- Created backup tag (use 'git tag -l \"$BACKUP_PREFIX-*\"' to find it)"
log_message "- Log file: $LOG_FILE"

echo "Done! Check $LOG_FILE for detailed log"
