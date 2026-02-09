import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔴 ENTER YOUR DETAILS HERE
BOT_TOKEN = "8505361939:AAGz6PM57UYNUcToS5ET62PlmTYW-ZFeFfA"
SUPPORT_GROUP_ID = -1003883601919 # Replace with your real group ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# 🔹 Main Menu Keyboard
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["💰 Deposit Issue", "🏦 Withdrawal Issue"],
            ["🆔 KYC / Aadhaar Issue", "❓ Other Issue"],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

# 🔹 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome to Lion Club Support, {user.first_name}!\n\n"
        "We are here to assist you with any issues related to your account.\n"
        "Please select the type of issue you are facing from the menu below."
    )
    await update.message.reply_text(welcome_message, reply_markup=main_menu_keyboard())

# 🔹 Handle button selection
async def handle_issue_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 Deposit Issue":
        message = (
            "💰 *Deposit Issue Selected*\n\n"
            "Please send the following details in *one single message*:\n"
            "• Your UID\n"
            "• Payment Screenshot\n"
            "• In-game Deposit Screenshot\n\n"
            "⚠️ Make sure all information and screenshots are in the *same message*."
        )
    elif text == "🏦 Withdrawal Issue":
        message = (
            "🏦 *Withdrawal Issue Selected*\n\n"
            "Please send the following details in *one single message*:\n"
            "• Your UID\n"
            "• Withdrawal Screenshot\n\n"
            "⚠️ Make sure all information and screenshots are in the *same message*."
        )
    elif text == "🆔 KYC / Aadhaar Issue":
        message = (
            "🆔 *KYC / Aadhaar Issue Selected*\n\n"
            "Please send the following details in *one single message*:\n"
            "• Your UID\n"
            "• Screenshot of the issue\n"
            "• A short description of the problem\n\n"
            "⚠️ Make sure all information and screenshots are in the *same message*."
        )
    elif text == "❓ Other Issue":
        message = (
            "❓ *Other Issue Selected*\n\n"
            "Please describe your issue clearly and send any relevant screenshots\n"
            "in *one single message*."
        )
    else:
        return

    context.user_data["issue_type"] = text
    await update.message.reply_text(message, parse_mode="Markdown")

# 🔹 Forward user message to support group
async def forward_to_support_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    # Forward text + media
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

    # Polite waiting reply to user
    await update.message.reply_text(
        "🙏 Thank you for contacting Lion Club Support.\n"
        "Our team is reviewing your issue and will assist you shortly.\n"
        "Please be patient — we are working on your problem."
    )

# 🔹 Main function
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_issue_selection)
    )
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_support_group)
    )

    application.run_polling()

if __name__ == "__main__":
    main()   
