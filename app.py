import yaml, os, logging
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

app = Flask(__name__)

# Configure the logging system
logging.basicConfig(
    level=logging.os.getenv("LOG_LEVEL"),
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Load the YAML configuration
def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


# Send a message to a Slack channel using the Slack API and a Bot Token
def send_to_slack(bot_token, slack_channel, message):
    slack_url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {bot_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": slack_channel,
        "text": message
    }
    
    response = requests.post(slack_url, headers=headers, json=payload)
    
    if response.status_code != 200 or not response.json().get('ok', False):
        logging.info(f"Error sending message to Slack: {response.text}")
    return response.status_code == 200

# Function to match text and find the correct Slack channel
# Fallback to #sre-alerts if no match is found
def determine_slack_channel(monitor_message, config):
    for team in config.get('teams', []):
        logging.info(f"Processing Team {team} config")
        for keyword in team.get('keywords', []):
            logging.debug(f"The keyword is {keyword.lower()} The Message is: {monitor_message.lower()}") 
            if keyword.lower() in monitor_message.lower():  # Basic substring match
                logging.info(f"Match found: `{keyword}  --  Routing alert to team {team}")
                return team.get('slack')
    
    # Fallback to SRE team if no keyword matches
    logging.info("No matches found so falling back to fallback channel")
    return config.get('fallback_channel')

# Route to handle incoming Datadog monitor webhooks
@app.route('/alert', methods=['POST'])
def datadog_webhook():
    # Load environment variables from the .env file
    load_dotenv()

    # Get the bot token from environment variables
    bot_token = os.getenv("SLACK_BOT_TOKEN")    
    data = request.json
    if not data or 'body' not in data:
        return jsonify({"error": "Invalid payload"}), 400

    monitor_message = data['body']['text']

    # Load YAML configuration (adjust the path as necessary)
    config = load_yaml_config('config.yml')

    # Route to Slack channel based on keyword matching or fallback
    slack_channel = determine_slack_channel(monitor_message, config)

    # Send the message to the appropriate Slack channel
    success = send_to_slack(bot_token, slack_channel, monitor_message)
    if success:
        return jsonify({"status": f"Message routed to {slack_channel}"}), 200
    else:
        return jsonify({"error": "Failed to send message to Slack"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
