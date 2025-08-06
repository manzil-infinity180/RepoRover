
<div align="center">
<p align="center">
<img align="center" alt="repoRover" width="800" src="https://github.com/user-attachments/assets/451c96aa-9ff7-48a6-aa76-41b5519951e1">
<!--   <img width="250" align="center" alt="dfc-ui" src="https://github.com/user-attachments/assets/96e29a8a-b55f-4d93-b1af-a2d66071c272" /> -->
</p>
<p align="center">

<p align="center">A friendly Slack bot that helps new contributors explore repositories in one <code>/command</code></p>
</p>
</div>

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- A Slack workspace with admin permissions
- ngrok (for local development) or a server for hosting

### 2. Installation

```bash
# Clone or create your project directory
mkdir RepoRover-slack-bot
cd RepoRover-slack-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in your project root:

```sh
export SLACK_BOT_TOKEN="xoxb-your-bot-token-here"
```

```bash
# Slack App Credentials (keep this for reference)
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
# SLACK_SIGNING_SECRET=your-signing-secret-here

# App Configuration
PORT=3000
DEBUG=True
```

### 4. File Structure

```
intervlab-slack-bot/
├── app.py                 # Main Flask application
├── maintainers.json       # Project maintainers config # I am using hardcoded in app.py
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── README.md             # This file
└── .gitignore            # Git ignore file
```

## 🔧 Slack App Configuration

### Step 1: Create a Slack App

1. Go to [Slack API](https://api.slack.com/apps)
2. Click **"Create New App"**
3. Choose **"From scratch"**
4. Name your app: `RepoRover Bot`
5. Select your workspace

### Step 2: Configure OAuth & Permissions

1. In your app settings, go to **"OAuth & Permissions"**
2. Add the following **Bot Token Scopes**:
   ```
   chat:write          # Send messages
   <!-- chat:write.public   # Send messages to channels bot isn't in -->
   commands            # Use slash commands
   users:read          # Read basic user info
   channels:read       # Read public channel info
   groups:read         # Read private channel info
   ```

3. **Install App to Workspace**
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### Step 3: Configure Slash Commands

1. Go to **"Slash Commands"** in your app settings
2. Create each command:

#### /contribute
- **Command**: `/contribute`
- **Request URL**: `https://your-domain.com/slack/commands`
- **Short Description**: `Get general contribution information`

#### /ui
- **Command**: `/ui`
- **Request URL**: `https://your-domain.com/slack/commands`
- **Short Description**: `Get UI project contribution info`

#### /kubestellar
- **Command**: `/kubestellar`
- **Request URL**: `https://your-domain.com/slack/commands`
- **Short Description**: `Get Kubestellar project contribution info`

#### /kubeflex
- **Command**: `/kubeflex`
- **Request URL**: `https://your-domain.com/slack/commands`
- **Short Description**: `Get Kubeflex project contribution info`

#### /meeting
- **Command**: `/meeting`
- **Request URL**: `https://your-domain.com/slack/commands`
- **Short Description**: `Get Kubestellar Community Meeting Info`

#### /know-about-internship
- **Command**: `/know-about-internship`
- **Request URL**: `https://your-domain.com/slack/commands`
- **Short Description**: `Learn about IntervLab internship program`

#### /help
- **Command**: `/help`
- **Request URL**: `https://your-domain.com/slack/commands`
- **Short Description**: `Show available commands and maintainers`

### Step 4: Configure Event Subscriptions

1. Go to **"Event Subscriptions"**
2. **Enable Events**: Toggle ON
3. **Request URL**: `https://your-domain.com/slack/events`
4. **Subscribe to bot events**:
   ```
   team_join           # When someone joins the workspace
   member_joined_channel # When someone joins a channel
   ```

### Step 5: Get Signing Secret

1. Go to **"Basic Information"**
2. Find **"App Credentials"**
3. Copy the **Signing Secret**

## 🌐 Deployment Options

### Option 1: Local Development with ngrok

```bash
# Install ngrok (if not installed)
# Download from https://ngrok.com/

# Start your Flask app
python app.py

# In another terminal, expose your local server
ngrok http 3000

# Use the ngrok URL (e.g., https://abc123.ngrok.io) in your Slack app configuration
```

### Option 2: Deploy to Heroku

```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set SLACK_BOT_TOKEN=xoxb-your-token
heroku config:set SLACK_SIGNING_SECRET=your-secret

# Deploy
git add .
git commit -m "Deploy IntervLab Slack Bot"
git push heroku main
```

### Option 3: Deploy to Railway/Render/DigitalOcean

Similar process - just make sure to:
1. Set environment variables
2. Use the deployed URL in your Slack app configuration

## 🧪 Testing Your Bot

### 1. Test Slash Commands

In any Slack channel, try:
```
/contribute
/kubeflex
/kubestellar
/contribute-ui
/contribute-xyz
/know-about-internship
/help
```

### 2. Test Welcome Messages

1. Invite a new user to your workspace
2. They should receive a welcome DM automatically

### 3. Health Check

Visit: `https://your-domain.com/health`

## 🔧 Customization

### Adding New Projects

Edit `maintainers.json`:

```json
{
  "projects": {
    "default": { ... },
    "new-project": {
      "docs_url": "https://github.com/intervlab/new-project",
      "github_url": "https://github.com/intervlab/new-project",
      "maintainers": ["maintainer1", "maintainer2"]
    }
   ...
  }
}
```

<p align="center">
<img width="450" height="450" alt="image" src="https://github.com/user-attachments/assets/92fe17a5-bffe-469d-beb3-0769bb85d4a5" />
</p>

## Author

Built with 💙 by **Rahul Vishwakarma** 
