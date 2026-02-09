from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8505361939:AAEn8IiRk5oOeTdW8pC-76_MIHRS8GpG6s4"
SUPPORT_GROUP_ID = -1003883601919

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [["💰 Deposit Issue", "🏦 Withdrawal Issue"], ["❓ Other Issue"]],
        resize_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🦁 *Welcome to Lion Club Support!*\n\n"
        "We’re glad to have you here. Our support team is available 24/7 to assist you.\n\n"
        "Please select your issue type using the buttons below. After that, send all required details in one single message.\n\n"
        "Thank you for choosing Lion Club 🤝",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text or ""

    if text in ["💰 Deposit Issue", "🏦 Withdrawal Issue", "❓ Other Issue"]:
        context.user_data["category"] = text
        context.user_data["submitted"] = False

        if text == "💰 Deposit Issue":
            await update.message.reply_text(
                "💰 *Deposit Issue Selected*\n\n"
                "Please provide the following details:\n"
                "1️⃣ Your UID\n"
                "2️⃣ Payment Screenshot\n"
                "3️⃣ In-game Deposit Screenshot\n\n"
                "Please send all the information in one single message, including your UID and screenshots.",
                parse_mode="Markdown"
            )

        elif text == "🏦 Withdrawal Issue":
            await update.message.reply_text(
                "🏦 *Withdrawal Issue Selected*\n\n"
                "Please provide the following details:\n"
                "1️⃣ Your UID\n"
                "2️⃣ Withdrawal Screenshot\n\n"
                "Please send all the information in one single message, including your UID and screenshot.",
                parse_mode="Markdown"
            )

        else:
            await update.message.reply_text(
                "❓ *Other Issue Selected*\n\n"
                "Please describe your issue clearly and attach any relevant screenshots.\n\n"
                "Please send all the information in one single message.",
                parse_mode="Markdown"
            )
        return

    category = context.user_data.get("category")

    if not category:
        await update.message.reply_text(
            "⚠️ Please first select your issue type using the buttons below.",
            reply_markup=main_menu_keyboard()
        )
        return

    if context.user_data.get("submitted"):
        await update.message.reply_text(
            "⏳ Please be patient. Our support team is already working on your issue and will resolve it as quickly as possible."
        )
        return

    context.user_data["submitted"] = True

    full_name = user.full_name
    username = f"@{user.username}" if user.username else "No username"
    user_id = user.id

    group_text = (
        f"📩 *New Support Message*\n\n"
        f"👤 Name: {full_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 Telegram ID: {user_id}\n"
        f"📂 Issue Type: {category}\n\n"
        f"💬 Message:\n{text if text else '(Media / Screenshot sent)'}"
    )

    sent_msg = None

    if update.message.photo:
        photo = update.message.photo[-1].file_id
        sent_msg = await context.bot.send_photo(
            chat_id=SUPPORT_GROUP_ID,
            photo=photo,
            caption=group_text,
            parse_mode="Markdown"
        )
    elif update.message.document:
        doc = update.message.document.file_id
        sent_msg = await context.bot.send_document(
            chat_id=SUPPORT_GROUP_ID,
            document=doc,
            caption=group_text,
            parse_mode="Markdown"
        )
    else:
        sent_msg = await context.bot.send_message(
            chat_id=SUPPORT_GROUP_ID,
            text=group_text,
            parse_mode="Markdown"
        )

    context.application.bot_data[sent_msg.message_id] = {
        "user_id": user_id
    }

    await update.message.reply_text(
        "Please be patient. Our support team is working on your issue and will resolve it as quickly as possible.\n\n"
        "Thank you for being a part of the Lion Club family."
    )

async def handle_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != SUPPORT_GROUP_ID:
        return
    if not update.message.reply_to_message:
        return

    replied_msg_id = update.message.reply_to_message.message_id
    if replied_msg_id not in context.application.bot_data:
        return

    user_chat_id = context.application.bot_data[replied_msg_id]["user_id"]
    reply_text = update.message.text or ""

    await context.bot.send_message(
        chat_id=user_chat_id,
        text=reply_text
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.ALL, handle_user_message))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.REPLY, handle_group_reply))
    print("🤖 Lion Club Support Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
