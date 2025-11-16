# send to Slack API
# slack_sender.py
from slack_bolt import App
from ..output_config import config

class SlackSender:

    app = App(token=config.slack_bot_token)

    @staticmethod
    def send_message(text: str):
        SlackSender.app.client.chat_postMessage(
            channel=config.slack_channel,
            text=text
        )

