import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8252550418:AAGzXJ9czrw-G9gtNse5kUy8esML7L_vgW8"  # Replace with your Bot Token
SUPPORT_GROUP_ID = -1003883601919  # Replace with your support group ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Inline buttons
def issue_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 Deposit Issue", callback_data="Deposit")],
        [InlineKeyboardButton("🏦 Withdrawal Issue", callback_data="Withdrawal")],
        [InlineKeyboardButton("❓ Other Issue", callback_data="Other")],
    ]
    return InlineKeyboardMarkup(keyboard)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Lion Club Support!\nPlease select your issue:",
        reply_markup=issue_keyboard()
    )

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    issue_type = query.data
    context.user_data["issue_type"] = issue_type

    messages = {
        "Deposit": "💰 Deposit Issue Selected\nSend UID + Payment Screenshot + In-game Deposit Screenshot in one message.",
        "Withdrawal": "🏦 Withdrawal Issue Selected\nSend UID + Withdrawal Screenshot in one message.",
        "Other": "❓ Other Issue Selected\nDescribe your issue clearly with screenshots in one message.",
    }
    await query.message.reply_text(messages[issue_type])

# Forward messages to support group
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    issue_type = context.user_data.get("issue_type", "Not selected")

    header = (
        f"📩 New Support Request\n\n"
        f"👤 Name: {user.first_name or ''} {user.last_name or ''}\n"
        f"🔗 Username: @{user.username or 'Not available'}\n"
        f"🆔 User ID: {user.id}\n"
        f"📌 Issue Type: {issue_type}\n\n"
        f"📝 User Message:"
    )

    if update.message.text:
        await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=f"{header}\n{update.message.text}")
    else:
        await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=header)
        await update.message.forward(chat_id=SUPPORT_GROUP_ID)

    await update.message.reply_text("🙏 Thank you! Our support team will contact you soon.")

# Main
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_user_message))
    app.run_polling()

if __name__ == "__main__":
    main()