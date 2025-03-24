# GitHub Setup Instructions

After creating a GitHub repository, connect your local repository with these commands:

```powershell
# Connect your local repository to the GitHub remote (replace with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/colliloqui-auto-rig-mcp.git

# Verify the remote was added
git remote -v

# Push your code to GitHub
git push -u origin master
```

You'll need to replace `YOUR_USERNAME` with your actual GitHub username.

## Alternative: GitHub CLI

If you have the GitHub CLI installed, you can create and set up the repository with:

```powershell
# Install GitHub CLI (if not already installed)
# Via winget
winget install --id GitHub.cli

# Or via Scoop
scoop install gh

# Login to GitHub


# Create a new repository and push your code
gh repo create colliloqui-auto-rig-mcp --public --source=. --push
```

This will create the repository, add it as a remote, and push your code in one step. 

If you want to clone the repository to your local machine, you can use the following command:

```
git clone https://github.com/Emmanuelekpeh/colliloqui-auto-rig-mcp.git
``` 