import discord
from discord.ext import commands
from flask import Flask, render_template, request
import threading
import asyncio
import os

# --- Flask Setup ---
app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/send_dm', methods=['POST'])
def send_dm():
    user_id = request.form.get('user_id')
    message = request.form.get('message')
    
    try:
        user_id = int(user_id)
    except ValueError:
        return "Invalid User ID. Must be a number."

    # Send the async task to the Discord bot's event loop
    asyncio.run_coroutine_threadsafe(trigger_dm(user_id, message), bot.loop)
    return "Message queued! <br><a href='/'>Go back</a>"

@app.route('/keep_alive')
def keep_alive():
    return "Bot is alive!"

def run_flask():
    # Render assigns a port dynamically via the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# --- Discord Bot Setup ---
# Server Members intent is necessary to fetch users properly
intents = discord.Intents.default()
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

async def trigger_dm(user_id, message):
    """Async function to actually send the DM via Discord API"""
    try:
        user = await bot.fetch_user(user_id)
        await user.send(message)
        print(f"Successfully sent DM to {user_id}")
    except discord.Forbidden:
        print(f"Failed: User {user_id} has DMs disabled.")
    except discord.NotFound:
        print(f"Failed: User {user_id} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

if __name__ == "__main__":
    # Start Flask in a background thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start the Discord Bot (This blocks the main thread)
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set.")
    else:
        bot.run(token)
