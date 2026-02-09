import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔴 ENTER YOUR DETAILS HERE
BOT_TOKEN = "8252550418:AAFan7HSixpwH3kv0xbCziu0ahTSikXmj0A"  # Replace with your actual bot token
SUPPORT_GROUP_ID = -1003883601919  # Replace with your real support group ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# 🔹 Inline keyboard for issue selection (no KYC button)
def issue_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 Deposit Issue", callback_data="Deposit")],
        [InlineKeyboardButton("🏦 Withdrawal Issue", callback_data="Withdrawal")],
        [InlineKeyboardButton("❓ Other Issue", callback_data="Other")],
    ]
    return InlineKeyboardMarkup(keyboard)

# 🔹 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome to Lion Club Support, {user.first_name}!\n\n"
        "We are here to assist you with any issues related to your account.\n"
        "Please select the type of issue you are facing from the buttons below."
    )
    await update.message.reply_text(welcome_message, reply_markup=issue_keyboard())

# 🔹 Handle button press
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    issue_type = query.data
    context.user_data["issue_type"] = issue_type

    messages = {
        "Deposit": (
            "💰 *Deposit Issue Selected*\n\n"
            "Please send the following details in *one single message*:\n"
            "• Your UID\n"
            "• Payment Screenshot\n"
            "• In-game Deposit Screenshot\n\n"
            "⚠️ Make sure all information and screenshots are in the *same message*."
        ),
        "Withdrawal": (
            "🏦 *Withdrawal Issue Selected*\n\n"
            "Please send the following details in *one single message*:\n"
            "• Your UID\n"
            "• Withdrawal Screenshot\n\n"
            "⚠️ Make sure all information and screenshots are in the *same message*."
        ),
        "Other": (
            "❓ *Other Issue Selected*\n\n"
            "Please describe your issue clearly and send any relevant screenshots in *one single message*."
        ),
    }

    await query.message.reply_text(messages[issue_type], parse_mode="Markdown")

# 🔹 Handle user messages after issue selection
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    issue_type = context.user_data.get("issue_type", "Not selected")

    header = (
        "📩 *New Support Request*\n\n"
        f"👤 Name: {user.first_name or ''} {user.last_name or ''}\n"
        f"🔗 Username: @{user.username if user.username else 'Not available'}\n"
        f"🆔 User ID: {user.id}\n"
        f"📌 Issue Type: {issue_type}\n\n"
        "📝 *User Message:*"
    )

    if update.message.text:
        await context.bot.send_message(
            chat_id=SUPPORT_GROUP_ID,
            text=f"{header}\n{update.message.text}",
            parse_mode="Markdown",
        )
    else:
        await context.bot.send_message(
            chat_id=SUPPORT_GROUP_ID,
            text=header,
            parse_mode="Markdown",
        )
        await update.message.forward(chat_id=SUPPORT_GROUP_ID)

    await update.message.reply_text(
        "🙏 Thank you for contacting Lion Club Support.\n"
        "Our team is reviewing your issue and will assist you shortly.\n"
        "Please be patient — we are working on your problem."
    )

# 🔹 Main function
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, handle_user_message)
    )

    application.run_polling()

if __name__ == "__main__":
    main()