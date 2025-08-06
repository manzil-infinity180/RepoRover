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
slack_client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))


# Load maintainers configuration
def load_maintainers_config():
    """Load maintainer configuration from JSON file"""
    try:
        with open("maintainers.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("maintainers.json not found. Using default config.")
        return {
            "projects": {
                "default": {
                    "docs_url": "https://docs.kubestellar.io/",
                    "github_url": "https://github.com/kubestellar/kubestellar",
                    "maintainers": ["Andy Anderson"],
                }
            }
        }
    except json.JSONDecodeError:
        logger.error("Invalid JSON in maintainers.json")
        return {"projects": {}}


def get_project_info(project_key="default"):
    """Get project information for a specific project"""
    config = load_maintainers_config()
    return config.get("projects", {}).get(
        project_key, config.get("projects", {}).get("default", {})
    )


def format_maintainers(maintainers_list):
    """Format maintainers list for display"""
    if not maintainers_list:
        return "No maintainers assigned"

    # Join maintainers with commas, don't add @ if already present
    formatted = []
    for maintainer in maintainers_list:
        if maintainer.startswith("@"):
            formatted.append(maintainer)
        else:
            formatted.append(f"@{maintainer}")

    return ", ".join(formatted)


def create_project_blocks(username, project_info, command_type="contribute"):
    """Create Slack Block Kit formatted message"""
    project_name = project_info.get("project_name", "KubeStellar")
    docs_url = project_info.get("docs_url", "https://docs.kubestellar.io")
    github_url = project_info.get(
        "github_url", "https://github.com/kubestellar/kubestellar"
    )
    description = project_info.get(
        "description", "A flexible solution for multi-cluster configuration management for edge, multi-cloud, and hybrid cloud."
    )
    maintainers = format_maintainers(project_info.get("maintainers", ["Andy"]))

    # Load organization info
    config = load_maintainers_config()
    org_info = config.get("organization", {})
    org_name = org_info.get("name", "KubeStellar")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🎉 Welcome to {org_name}!"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Hi <@{username}>! 🤖 *I'm the KubeStellar bot* - here to help you get started with contributing to our open source projects!"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🚀 *{project_name}*\n_{description}_"
            },
            "accessory": {
                "type": "image",
                "image_url": "https://avatars.githubusercontent.com/u/134407106?s=200&v=4",
                "alt_text": "KubeStellar logo"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "📚 *Essential Resources*"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*📖 Documentation*\n<{docs_url}|View Docs>"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*🔗 GitHub Repository*\n<{github_url}|View Code>"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🌐 Main Website*\n<{org_info.get('website', 'https://kubestellar.io')}|Visit KubeStellar.io>"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🤝 *Getting Help*\n*New to open source?* No worries! We're here to help you make your first contribution.\n\n*Have questions about this project?* Tag: {https://github.com/clubanderson}|Andy>"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "💡 *Quick Start Commands*"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "`/help`\nView all available commands"
                },
                {
                    "type": "mrkdwn",
                    "text": "`/contribute`\nGeneral contribution guidelines"
                },
                {
                    "type": "mrkdwn",
                    "text": "`/kubeflex`\nKubeFlex project info"
                },
                {
                    "type": "mrkdwn",
                    "text": "`/ui`\nKubeStellar UI project info"
                },
                {
                    "type": "mrkdwn",
                    "text": "`/know-about-internship`\nKubeStellar Internship(IFOS) info"
                }
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📖 View Documentation"
                    },
                    "style": "primary",
                    "url": docs_url
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔗 GitHub Repository"
                    },
                    "url": github_url
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🌐 Website"
                    },
                    "url": org_info.get('website', 'https://kubestellar.io')
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🚀 *Happy Coding!* We're excited to have you in our community! 🌟"
                }
            ]
        }
    ]

    return blocks


def create_help_blocks(user_id):
    """Create help message blocks"""
    config = load_maintainers_config()
    projects = config.get("projects", {})
    org_info = config.get("organization", {})

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🤖 KubeStellar Bot"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Your guide to contributing to KubeStellar open source projects!"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🚀 *Project Commands*"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "`/contribute` or `/kubeStellar`\nKubeStellar Core project info"
                },
                {
                    "type": "mrkdwn",
                    "text": "`/kubeflex`\nKubeFlex project contribution guide"
                },
                {
                    "type": "mrkdwn",
                    "text": "`/ui`\nKubeStellar UI project details"
                },
                {
                    "type": "mrkdwn",
                    "text": "`/a2a`\nApp-to-App (A2A) project info"
                }

            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🔧 *Utility Commands*"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "`/know-about-internship`\nOpen source contribution guidance"
                },
                {
                    "type": "mrkdwn",
                    "text": "`/help`\nThis help menu"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "👥 *Project Maintainers & Contacts*\n\nNeed help with a specific project? Tag the right people:"
                # https://github.com/kubestellar/kubestellar/blob/main/OWNERS
            }
        }
    ]

    # Add maintainers for each project
    for project_key, project_data in projects.items():
        maintainers = format_maintainers(project_data.get("maintainers", []))
        project_name = project_data.get(
            "project_name", project_key.replace("_", " ").title()
        )
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{project_name}:* {maintainers}"
            }
        })

    # Add quick links section
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🌟 *Quick Links*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🌐 Website"
                    },
                    "style": "primary",
                    "url": org_info.get('website', 'https://kubestellar.io')
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📖 Documentation"
                    },
                    "url": org_info.get('docs', 'https://docs.kubestellar.io')
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔗 GitHub Org"
                    },
                    "url": org_info.get('github', 'https://github.com/kubestellar')
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "✨ Join Us"
                    },
                    "url": org_info.get('github', 'http://kubestellar.io/join_us')
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "💡 *Pro Tip:* Start with `/contribute` to get familiar with our main project, then explore specific components!"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🚀 *Welcome to the KubeStellar community!*"
                }
            ]
        }
    ])

    return blocks

def create_meeting_blocks(user_id):
    """Create meeting message blocks"""
    config = load_maintainers_config()
    projects = config.get("projects", {})
    org_info = config.get("organization", {})

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎯 Interested in Joining KubeStellar Community Meeting?"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Hi <@{user_id}>! 🌟 *Welcome to our open source community!* We're excited you want to get involved."
            }
        },
        {
            "type": "divider"
        },        
    ]

    # Add maintainers for each project
    for project_key, project_data in projects.items():
        maintainers = format_maintainers(project_data.get("maintainers", []))
        project_name = project_data.get(
            "project_name", project_key.replace("_", " ").title()
        )
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{project_name}:* {maintainers}"
            }
        })

        blocks.extend([
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*📅 Community Meeting Info*\n"
                    "<http://kubestellar.io/join_us|👉 Get an invite by joining our Google Group>\n\n"
                    "*📝 Agenda & Meeting Notes*\n"
                    "<https://docs.google.com/document/d/1XppfxSOD7AOX1lVVVIPWjpFkrxakfBfVzcybRg17-PM/|View Document>"
                )
            }
        },
        {
            "type": "divider"
        }
    ])

    # Add quick links section
    blocks.extend([
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🌟 *Quick Links*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🌐 Website"
                    },
                    "style": "primary",
                    "url": org_info.get('website', 'https://kubestellar.io')
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📖 Documentation"
                    },
                    "url": org_info.get('docs', 'https://docs.kubestellar.io')
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔗 GitHub Org"
                    },
                    "url": org_info.get('github', 'https://github.com/kubestellar')
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "💡 *Pro Tip:* Start with `/contribute` to get familiar with our main project, then explore specific components!"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🚀 *Welcome to the KubeStellar community!*"
                }
            ]
        }
    ])

    return blocks


def create_internship_blocks(user_id):
    """Create internship/contribution guidance blocks"""
    project_info = get_project_info("default")
    config = load_maintainers_config()
    org_info = config.get("organization", {})

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎯 Interested in Contributing to KubeStellar?"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Hi <@{user_id}>! 🌟 *Welcome to our open source community!* We're excited you want to get involved."
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🚀 *Getting Started with Open Source Contributions*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "📋 *Available Projects*\nChoose a project that matches your interests and skills:"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*KubeStellar Core*\nMulti-cluster Kubernetes management"
                },
                {
                    "type": "mrkdwn",
                    "text": "*KubeFlex*\nFlexible cluster management tools"
                },
                {
                    "type": "mrkdwn",
                    "text": "*KubeStellar UI*\nWeb interface and dashboards"
                },
                {
                    "type": "mrkdwn",
                    "text": "*App-to-App (A2A)*\nCommunication framework"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "📚 *Essential Resources*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📖 Documentation"
                    },
                    "style": "primary",
                    "url": org_info.get('docs', 'https://docs.kubestellar.io')
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔗 GitHub Organization"
                    },
                    "url": org_info.get('github', 'https://github.com/kubestellar')
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🌐 Community Website"
                    },
                    "url": org_info.get('website', 'https://kubestellar.io')
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                # "text": f"🤝 *Need Help?*\n*New to open source?* Perfect! We love helping first-time contributors.\n\n*Questions or need guidance?* Tag: {format_maintainers(project_info.get('maintainers', ['Andy']))}"
                "text": f"🤝 *Need Help?*\n*New to open source?* Perfect! We love helping first-time contributors.\n\n*Questions or need guidance?* Tag: Andy Anderson"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "💡 *Next Steps*\n1. Pick a project that interests you\n2. Check out the GitHub repository\n3. Look for \"good first issue\" labels\n4. Join our community discussions\n5. Don't hesitate to ask questions!"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🚀✨ *Let's build something amazing together!*"
                }
            ]
        }
    ]

    return blocks


@app.route("/slack/commands", methods=["POST"])
def handle_slash_commands():
    """Handle all slash commands"""
    try:
        # Verify the request is from Slack
        if not verify_slack_request(request):
            return jsonify({"error": "Invalid request"}), 403

        # Parse form data
        command = request.form.get("command", "").strip()
        user_id = request.form.get("user_id")
        username = request.form.get("user_name")
        channel_id = request.form.get("channel_id")

        logger.info(f"Received command: {command} from user: {username}")

        # Handle different commands
        if command == "/contribute":
            project_info = get_project_info("default")
            blocks = create_project_blocks(user_id, project_info, "contribute")

        if command == "/kubestellar":
            project_info = get_project_info("kubestellar")
            blocks = create_project_blocks(user_id, project_info, "kubestellar")

        elif command == "/kubeflex":
            project_info = get_project_info("kubeflex")
            blocks = create_project_blocks(user_id, project_info, "kubeflex")

        elif command == "/ui":
            project_info = get_project_info("ui")
            blocks = create_project_blocks(user_id, project_info, "ui")

        elif command == "/a2a":
            project_info = get_project_info("a2a")
            blocks = create_project_blocks(user_id, project_info, "a2a")

        elif command == "/know-about-internship":
            blocks = create_internship_blocks(user_id)

        elif command == "/help":
            blocks = create_help_blocks(user_id)

        elif command == "/meeting":
            blocks = create_meeting_blocks(user_id)

        else:
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"❌ Unknown command: `{command}`\n\nType `/help` to see available commands."
                    }
                }
            ]

        # Send response back to Slack with blocks
        return jsonify({
            "response_type": "in_channel",
            "blocks": blocks
        })

    except Exception as e:
        logger.error(f"Error handling slash command: {str(e)}")
        return (
            jsonify({
                "response_type": "ephemeral",
                "text": "Sorry, something went wrong. Please try again later.",
            }),
            500,
        )


@app.route("/slack/events", methods=["POST"])
def handle_events():
    """Handle Slack Events API callbacks"""
    try:
        data = request.json

        # Handle URL verification challenge
        if data.get("type") == "url_verification":
            return jsonify({"challenge": data.get("challenge")})

        # Handle actual events
        event = data.get("event", {})
        event_type = event.get("type")

        if event_type == "team_join":
            # New user joined the workspace
            user_info = event.get("user", {})
            user_id = user_info.get("id")

            if user_id:
                send_welcome_dm(user_id)

        elif event_type == "member_joined_channel":
            # User joined a specific channel
            user_id = event.get("user")
            channel_id = event.get("channel")

            # You can customize this to send welcome messages for specific channels
            # For now, we'll just log it
            logger.info(f"User {user_id} joined channel {channel_id}")

        return jsonify({"status": "ok"})

    except Exception as e:
        logger.error(f"Error handling event: {str(e)}")
        return jsonify({"status": "error"}), 500


def send_welcome_dm(user_id):
    """Send welcome direct message to new user with blocks"""
    try:
        config = load_maintainers_config()
        org_info = config.get("organization", {})
        default_project = config.get("projects", {}).get("default", {})

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎉 Hey there, welcome to KubeStellar!"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hi <@{user_id}>! 🌟 *Welcome to our open source community!* We're thrilled to have you here."
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🚀 *Getting Started Guide*\n\n📋 *Explore Our Projects*\nChoose what interests you most:"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "`/contribute`\nKubeStellar Core (multi-cluster management)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "`/kubeflex`\nKubeFlex (flexible cluster tools)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "`/ui`\nKubeStellar UI (web interfaces)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "`/a2a`\nApp-to-App communication framework"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📖 Documentation"
                        },
                        "style": "primary",
                        "url": org_info.get('docs', 'https://docs.kubestellar.io')
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔗 GitHub Organization"
                        },
                        "url": org_info.get('github', 'https://github.com/kubestellar')
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🌐 Community Website"
                        },
                        "url": org_info.get('website', 'https://kubestellar.io')
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🤝 *Need Help?*\n*New to open source?* Perfect! We're here to guide you.\n\n*Have questions?* Use `/help` to see all commands and find the right maintainers to tag."
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "💡 *Pro Tips for New Contributors*\n1. Start with `/contribute` to understand our main project\n2. Look for \"good first issue\" labels on GitHub\n3. Join our community discussions\n4. Don't hesitate to ask questions - we're friendly! 😊"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🚀✨ *Ready to make an impact?* Let's build the future of Kubernetes together!\n\n*Happy coding!* 🧰"
                    }
                ]
            }
        ]

        # Send DM using chat.postMessage with blocks
        response = slack_client.chat_postMessage(
            channel=f"@{user_id}",  # DM channel
            blocks=blocks,
            username="KubeStellar Bot",
            icon_emoji=":rocket:",
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

    required_fields = ["command", "user_id", "user_name"]
    form_data = request.form

    return all(field in form_data for field in required_fields)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }
    )


@app.route("/", methods=["GET"])
def root():
    """Root endpoint"""
    return jsonify(
        {
            "message": "Kubestellar Slack Bot is running!",
            "endpoints": {
                "/slack/commands": "POST - Handle slash commands",
                "/slack/events": "POST - Handle Slack events",
                "/health": "GET - Health check",
            },
        }
    )


if __name__ == "__main__":
    # Check for required environment variables
    if not os.environ.get("SLACK_BOT_TOKEN"):
        logger.error("SLACK_BOT_TOKEN environment variable is required")
        exit(1)

    # Run the Flask app
    port = int(os.environ.get("PORT", 3000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("DEBUG", "False").lower() == "true",
    )