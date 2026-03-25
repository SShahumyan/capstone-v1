
# Git Cheat Sheet

## Basic Commands

### Initialize a Git repository
```
git init
```

### Check status of your repository
```
git status
```

### Stage files for commit
```
git add <file>              # Stage a specific file
git add .                   # Stage all files in the current directory
git add -A                  # Stage all files (including deleted and renamed files)
```

### Commit changes
```
git commit -m "Commit message"
```

### Pull changes from a remote repository
```
git pull origin <branch_name>
```

### Push changes to a remote repository
```
git push origin <branch_name>
```

## Branching and Merging

### Create a new branch
```
git checkout -b <branch_name>   # Create and switch to a new branch
```

### Switch between branches
```
git checkout <branch_name>
```
