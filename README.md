# Switch Import Bot

Tg to Switch is a Python bot designed to copy messages from Telegram channels. It supports handling file uploads and downloads and can manage multiple bot instances concurrently.

## Setup

Follow these steps to set up and run the Telegram Copy Bot on your system.

### Prerequisites

- Python 3.10 or higher
- [Telethon](https://github.com/LonamiWebs/Telethon) library
- Switch Bot token
- Telegram API credentials (API ID, API Hash)
- Telegram bot token(s)

### Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/hummingbird28/SwitchImport.git
   ```

2. Navigate to the project directory:

   ```bash
   cd SwitchImport
   ```

3. Install the required Python packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Obtain Telegram API credentials:
   - Go to [Telegram's website](https://my.telegram.org/auth) and log in with your Telegram account.
   - Create a new application and obtain your API ID and API Hash.

2. Create a `config.py` file in the project directory with the following content:

   ```python
   # telegram api id/hash
   API_ID = 'your_api_id'
   API_HASH = 'your_api_hash'

   # switch bot token
   BOT_TOKEN = 'your_bot_token'
   ```

   Replace `'your_api_id'`, `'your_api_hash'`, and `'your_bot_token'` with your actual API ID, API Hash, and bot token respectively.

3. Create a `bot_tokens.txt` file in the project directory containing one or more bot tokens, each on a new line.
(add telegram bot tokens)

### Usage

Run the bot using the following command:

```bash
python main.py
```

The bot will now start and listen for commands in your Switch channels.

## Commands

- `/start`: Get the start message.
- `/copy channel_username startMsgId-endMsgId`: Copy messages from the specified channel. Replace `channel_username` with the target channel's username and `startMsgId-endMsgId` with the range of message IDs you want to copy.

- `/cancel`: Cancel ongoing tasks in the current chat.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
