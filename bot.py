import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# 🔴 Apna Bot Token aur Support Group ID yahan dalen
BOT_TOKEN = "8252550418:AAFan7HSixpwH3kv0xbCziu0ahTSikXmj0A"
SUPPORT_GROUP_ID = -1003883601919  # Example: -1001234567890

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🔹 /start command
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💰 Deposit Issue", callback_data="Deposit")],
        [InlineKeyboardButton("🏦 Withdrawal Issue", callback_data="Withdrawal")],
        [InlineKeyboardButton("❓ Other Issue", callback_data="Other")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("👋 Welcome to Lion Club Support!\nPlease select your issue:", reply_markup=reply_markup)

# 🔹 Button click handler
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    issue_type = query.data
    context.user_data["issue_type"] = issue_type

    messages = {
        "Deposit": "💰 Deposit Issue Selected\nSend your UID + Payment Screenshot + In-game Deposit Screenshot in one message.",
        "Withdrawal": "🏦 Withdrawal Issue Selected\nSend your UID + Withdrawal Screenshot in one message.",
        "Other": "❓ Other Issue Selected\nDescribe your issue clearly and attach any relevant screenshots in one message.",
    }

    query.message.reply_text(messages[issue_type])

# 🔹 Forward user messages to support group
def handle_user_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    issue_type = context.user_data.get("issue_type", "Not selected")

    header = (
        f"📩 New Support Request\n\n"
        f"👤 Name: {user.first_name} {user.last_name or ''}\n"
        f"🔗 Username: @{user.username or 'Not available'}\n"
        f"🆔 User ID: {user.id}\n"
        f"📌 Issue Type: {issue_type}\n\n"
        f"📝 User Message:"
    )

    # Text message
    if update.message.text:
        context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=f"{header}\n{update.message.text}")
    # Media or other
    else:
        context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=header)
        update.message.forward(chat_id=SUPPORT_GROUP_ID)

    # Reply to user
    update.message.reply_text("🙏 Thank you! Our support team will contact you soon.")

# 🔹 Main function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.all & ~Filters.command, handle_user_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()