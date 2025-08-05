import json
import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Slack client
slack_client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))

# Load maintainers configuration
def load_maintainers_config():
    """Load maintainer configuration from JSON file"""
    try:
        with open('maintainers.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("maintainers.json not found. Using default config.")
        return {
            "projects": {
                "default": {
                    "docs_url": "https://github.com/intervlab/docs",
                    "github_url": "https://github.com/intervlab/docs",
                    "maintainers": ["andy"]
                }
            }
        }
    except json.JSONDecodeError:
        logger.error("Invalid JSON in maintainers.json")
        return {"projects": {}}

def get_project_info(project_key="default"):
    """Get project information for a specific project"""
    config = load_maintainers_config()
    return config.get("projects", {}).get(project_key, config.get("projects", {}).get("default", {}))

def format_maintainers(maintainers_list):
    """Format maintainers list for display"""
    if not maintainers_list:
        return "No maintainers assigned"
    
    # Join maintainers with commas, don't add @ if already present
    formatted = []
    for maintainer in maintainers_list:
        if maintainer.startswith('@'):
            formatted.append(maintainer)
        else:
            formatted.append(f"@{maintainer}")
    
    return ", ".join(formatted)

def create_response_message(username, project_info, command_type="contribute"):
    """Create dynamic response message with improved formatting"""
    project_name = project_info.get('project_name', 'KubeStellar')
    docs_url = project_info.get('docs_url', 'https://docs.kubestellar.io')
    github_url = project_info.get('github_url', 'https://github.com/kubestellar/kubestellar')
    description = project_info.get('description', 'Open source multi-cluster configuration management')
    maintainers = format_maintainers(project_info.get('maintainers', ['Andy']))
    
    # Load organization info
    config = load_maintainers_config()
    org_info = config.get('organization', {})
    org_name = org_info.get('name', 'KubeStellar')
    
    message = f"""🎉 Hi <@{username}>! Welcome to **{org_name}**! 

> 🤖 **I'm the KubeStellar bot** - here to help you get started with contributing to our open source projects!

## 🚀 **{project_name}**
> *{description}*

### 📚 **Resources**
• **Documentation:** {docs_url}
• **GitHub Repository:** {github_url}
• **Main Website:** {org_info.get('website', 'https://kubestellar.io')}

### 🤝 **Getting Help**
> **New to open source?** No worries! We're here to help you make your first contribution.
> 
> **Have questions about this project?** Tag: {maintainers}

### 💡 **Quick Start**
```
/help           → View all available commands
/contribute     → General contribution guidelines  
/kubeflex       → KubeFlex project info
/ui             → KubeStellar UI project info
/a2a            → App-to-App project info
```

**Happy Coding!** 🚀 We're excited to have you in our community! 🌟"""
    
    return message

@app.route('/slack/commands', methods=['POST'])
def handle_slash_commands():
    """Handle all slash commands"""
    try:
        # Verify the request is from Slack
        if not verify_slack_request(request):
            return jsonify({"error": "Invalid request"}), 403
        
        # Parse form data
        command = request.form.get('command', '').strip()
        user_id = request.form.get('user_id')
        username = request.form.get('user_name')
        channel_id = request.form.get('channel_id')
        
        logger.info(f"Received command: {command} from user: {username}")
        
        # Handle different commands
        if command == '/contribute':
            project_info = get_project_info("default")
            message = create_response_message(user_id, project_info, "contribute")
            
        # Handle different commands
        if command == '/contribute':
            project_info = get_project_info("default")
            message = create_response_message(user_id, project_info, "contribute")
            
        elif command == '/kubeflex':
            project_info = get_project_info("kubeflex")
            message = create_response_message(user_id, project_info, "kubeflex")
            
        elif command == '/ui':
            project_info = get_project_info("ui")
            message = create_response_message(user_id, project_info, "ui")
            
        elif command == '/a2a':
            project_info = get_project_info("a2a")
            message = create_response_message(user_id, project_info, "a2a")
            
        elif command == '/know-about-internship':
            project_info = get_project_info("default")
            config = load_maintainers_config()
            org_info = config.get('organization', {})
            
            message = f"""🎯 Hi <@{user_id}>! **Interested in Contributing to KubeStellar?**

> 🌟 **Welcome to our open source community!** We're excited you want to get involved.

## 🚀 **Getting Started with Open Source Contributions**

### 📋 **Available Projects**
> Choose a project that matches your interests and skills:

• **KubeStellar Core** - Multi-cluster Kubernetes management
• **KubeFlex** - Flexible cluster management tools  
• **KubeStellar UI** - Web interface and dashboards
• **App-to-App (A2A)** - Communication framework

### 📚 **Essential Resources**
• **Main Documentation:** {org_info.get('docs', 'https://docs.kubestellar.io')}
• **GitHub Organization:** {org_info.get('github', 'https://github.com/kubestellar')}
• **Community Website:** {org_info.get('website', 'https://kubestellar.io')}

### 🤝 **Need Help?**
> **New to open source?** Perfect! We love helping first-time contributors.
> 
> **Questions or need guidance?** Tag: {format_maintainers(project_info.get('maintainers', ['Andy']))}

### 💡 **Next Steps**
```
1. Pick a project that interests you
2. Check out the GitHub repository
3. Look for "good first issue" labels
4. Join our community discussions
5. Don't hesitate to ask questions!
```

**Let's build something amazing together!** 🚀✨"""
            
        elif command == '/help':
            config = load_maintainers_config()
            projects = config.get("projects", {})
            org_info = config.get('organization', {})
            
            help_message = f"""🤖 **KubeStellar Bot - Command Center**

> Your guide to contributing to KubeStellar open source projects!

## 📋 **Available Commands**

### 🚀 **Project Commands**
```
/contribute     → KubeStellar Core project info
/kubeflex       → KubeFlex project contribution guide
/ui             → KubeStellar UI project details  
/a2a            → App-to-App (A2A) project info
```

### 🔧 **Utility Commands**
```
/know-about-internship → Open source contribution guidance
/help                  → This help menu
```

## 👥 **Project Maintainers & Contacts**

> **Need help with a specific project?** Tag the right people:
"""
            
            for project_key, project_data in projects.items():
                maintainers = format_maintainers(project_data.get('maintainers', []))
                project_name = project_data.get('project_name', project_key.replace('_', ' ').title())
                help_message += f"\n• **{project_name}:** {maintainers}"
            
            help_message += f"""

## 🌟 **Quick Links**
• **Website:** {org_info.get('website', 'https://kubestellar.io')}
• **Documentation:** {org_info.get('docs', 'https://docs.kubestellar.io')}
• **GitHub Org:** {org_info.get('github', 'https://github.com/kubestellar')}

> 💡 **Pro Tip:** Start with `/contribute` to get familiar with our main project, then explore specific components!

**Welcome to the KubeStellar community!** 🚀"""
            message = help_message
            
        else:
            message = f"Unknown command: {command}. Type `/help` to see available commands."
        
        # Send response back to Slack
        return jsonify({
            "response_type": "in_channel",
            "text": message
        })
        
    except Exception as e:
        logger.error(f"Error handling slash command: {str(e)}")
        return jsonify({
            "response_type": "ephemeral",
            "text": "Sorry, something went wrong. Please try again later."
        }), 500

@app.route('/slack/events', methods=['POST'])
def handle_events():
    """Handle Slack Events API callbacks"""
    try:
        data = request.json
        
        # Handle URL verification challenge
        if data.get('type') == 'url_verification':
            return jsonify({'challenge': data.get('challenge')})
        
        # Handle actual events
        event = data.get('event', {})
        event_type = event.get('type')
        
        if event_type == 'team_join':
            # New user joined the workspace
            user_info = event.get('user', {})
            user_id = user_info.get('id')
            
            if user_id:
                send_welcome_dm(user_id)
        
        elif event_type == 'member_joined_channel':
            # User joined a specific channel
            user_id = event.get('user')
            channel_id = event.get('channel')
            
            # You can customize this to send welcome messages for specific channels
            # For now, we'll just log it
            logger.info(f"User {user_id} joined channel {channel_id}")
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Error handling event: {str(e)}")
        return jsonify({'status': 'error'}), 500

def send_welcome_dm(user_id):
    """Send welcome direct message to new user"""
    try:
        config = load_maintainers_config()
        org_info = config.get('organization', {})
        default_project = config.get("projects", {}).get("default", {})
        
        welcome_message = f"""🎉 **Hey <@{user_id}>, welcome to KubeStellar!** 

> 🌟 **Welcome to our open source community!** We're thrilled to have you here.

## 🚀 **Getting Started Guide**

### 📋 **Explore Our Projects**
> Choose what interests you most:
```
/contribute → KubeStellar Core (multi-cluster management)
/kubeflex   → KubeFlex (flexible cluster tools)
/ui         → KubeStellar UI (web interfaces)
/a2a        → App-to-App communication framework
```

### 📚 **Essential Resources**
• **Documentation:** {org_info.get('docs', 'https://docs.kubestellar.io')}
• **GitHub Organization:** {org_info.get('github', 'https://github.com/kubestellar')}
• **Community Website:** {org_info.get('website', 'https://kubestellar.io')}

### 🤝 **Need Help?**
> **New to open source?** Perfect! We're here to guide you.
> 
> **Have questions?** Use `/help` to see all commands and find the right maintainers to tag.

### 💡 **Pro Tips for New Contributors**
```
1. Start with /contribute to understand our main project
2. Look for "good first issue" labels on GitHub
3. Join our community discussions
4. Don't hesitate to ask questions - we're friendly! 😊
```

**Ready to make an impact?** Let's build the future of Kubernetes together! 🚀✨

*Happy coding!* 🧰"""
        
        # Send DM using chat.postMessage
        response = slack_client.chat_postMessage(
            channel=f"@{user_id}",  # DM channel
            text=welcome_message,
            username="KubeStellar Bot",
            icon_emoji=":rocket:"
        )
        
        logger.info(f"Welcome DM sent to user {user_id}")
        
    except SlackApiError as e:
        logger.error(f"Error sending welcome DM: {e.response['error']}")
    except Exception as e:
        logger.error(f"Unexpected error sending welcome DM: {str(e)}")

def verify_slack_request(request):
    """Verify that the request is from Slack (simplified version)"""
    # In production, you should implement proper request verification
    # using Slack's signing secret. For now, we'll do basic validation.
    
    required_fields = ['command', 'user_id', 'user_name']
    form_data = request.form
    
    return all(field in form_data for field in required_fields)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "IntervLab Slack Bot is running!",
        "endpoints": {
            "/slack/commands": "POST - Handle slash commands",
            "/slack/events": "POST - Handle Slack events",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    # Check for required environment variables
    if not os.environ.get('SLACK_BOT_TOKEN'):
        logger.error("SLACK_BOT_TOKEN environment variable is required")
        exit(1)
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')
