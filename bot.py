# bot.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# 🔴 Configuration
BOT_TOKEN = "8252550418:AAFR5FJ2h3zFsmOfcqF-j8D_3KyM-tc2_II"  # ⚠️ Replace with your bot token
SUPPORT_GROUP_ID = -1003883601919  # ⚠️ Replace with your support group ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🔹 Language & Issue Buttons
def language_keyboard():
    keyboard = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("हिंदी 🇮🇳", callback_data="lang_hi")],
        [InlineKeyboardButton("Hinglish 📝", callback_data="lang_hin")],
    ]
    return InlineKeyboardMarkup(keyboard)

def issue_keyboard(lang="en"):
    if lang == "hi":
        keyboard = [
            [InlineKeyboardButton("💰 डिपॉज़िट समस्या", callback_data="Deposit")],
            [InlineKeyboardButton("🏦 विदड्रॉवल समस्या", callback_data="Withdrawal")],
            [InlineKeyboardButton("❓ अन्य समस्या", callback_data="Other")],
        ]
    elif lang == "hin":
        keyboard = [
            [InlineKeyboardButton("💰 Deposit Issue", callback_data="Deposit")],
            [InlineKeyboardButton("🏦 Withdrawal Issue", callback_data="Withdrawal")],
            [InlineKeyboardButton("❓ Other Issue", callback_data="Other")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("💰 Deposit Issue", callback_data="Deposit")],
            [InlineKeyboardButton("🏦 Withdrawal Issue", callback_data="Withdrawal")],
            [InlineKeyboardButton("❓ Other Issue", callback_data="Other")],
        ]
    return InlineKeyboardMarkup(keyboard)

# 🔹 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Welcome to Lion Club Support!\nPlease choose your preferred language:",
        reply_markup=language_keyboard()
    )

# 🔹 Language selection handler
async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_choice = query.data.replace("lang_", "")
    context.user_data["lang"] = lang_choice
    await query.message.reply_text(
        "Please select your issue:" if lang_choice == "en" else
        "कृपया अपनी समस्या चुनें:" if lang_choice == "hi" else
        "Kripya apni problem choose karein:",
        reply_markup=issue_keyboard(lang_choice)
    )

# 🔹 Issue selection handler
async def issue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    issue_type = query.data
    context.user_data["issue_type"] = issue_type
    lang = context.user_data.get("lang", "en")

    # 🔹 Full welcome & instruction messages (as guided by you)
    messages = {
        "Deposit": {
            "en": (
                "💰 Deposit Issue Selected.\n"
                "Send UID + Payment Screenshot + In-game Deposit Screenshot in one message.\n\n"
                "This helps our support team process your request faster. 😊"
            ),
            "hi": (
                "💰 डिपॉज़िट समस्या चुनी गई है।\n"
                "कृपया एक ही मैसेज में निम्नलिखित भेजें:\n"
                "- 🆔 आपका यूज़र आईडी (UID)\n"
                "- 💳 पेमेंट की स्क्रीनशॉट\n"
                "- 🕹️ इन-गेम डिपॉज़िट की स्क्रीनशॉट\n\n"
                "इससे हमारी सपोर्ट टीम आपकी मदद जल्दी कर पाएगी। 😊"
            ),
            "hin": (
                "💰 Deposit Issue Selected.\n"
                "Kripya ek hi message mein yeh sab bhejein:\n"
                "- 🆔 Aapka User ID (UID)\n"
                "- 💳 Payment ki screenshot\n"
                "- 🕹️ In-game deposit ki screenshot\n\n"
                "Isse hamari support team aapki madad jaldi kar sakegi. 😊"
            )
        },
        "Withdrawal": {
            "en": (
                "🏦 Withdrawal Issue Selected.\n"
                "Send UID + Withdrawal Screenshot in one message.\n\n"
                "Our team will handle your withdrawal request quickly. 😊"
            ),
            "hi": (
                "🏦 विदड्रॉवल समस्या चुनी गई है।\n"
                "कृपया एक ही मैसेज में निम्नलिखित भेजें:\n"
                "- 🆔 आपका यूज़र आईडी (UID)\n"
                "- 📸 विदड्रॉवल स्क्रीनशॉट\n\n"
                "हमारी टीम आपकी विदड्रॉवल रिक्वेस्ट जल्दी प्रोसेस करेगी। 😊"
            ),
            "hin": (
                "🏦 Withdrawal Issue Selected.\n"
                "Kripya ek hi message mein yeh sab bhejein:\n"
                "- 🆔 Aapka User ID (UID)\n"
                "- 📸 Withdrawal ki screenshot\n\n"
                "Hamari team aapki withdrawal request jaldi process karegi. 😊"
            )
        },
        "Other": {
            "en": (
                "❓ Other Issue Selected.\n"
                "Describe your issue clearly with screenshots in one message.\n\n"
                "Our team will respond as soon as possible. 😊"
            ),
            "hi": (
                "❓ अन्य समस्या चुनी गई है।\n"
                "कृपया अपनी समस्या विस्तार से और स्क्रीनशॉट के साथ भेजें।\n\n"
                "हमारी टीम जल्द ही आपसे संपर्क करेगी। 😊"
            ),
            "hin": (
                "❓ Other Issue Selected.\n"
                "Kripya apni problem detail mein batayein aur screenshots ek hi message mein bhejein.\n\n"
                "Hamari team jald hi aapse contact karegi. 😊"
            )
        }
    }

    await query.message.reply_text(messages[issue_type][lang])

# 🔹 Forward user messages to support group
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    issue_type = context.user_data.get("issue_type")
    lang = context.user_data.get("lang", "en")

    if not issue_type:
        await update.message.reply_text(
            "❗ Please select an issue first using /start." if lang=="en" else
            "❗ कृपया पहले अपनी समस्या चुनें।" if lang=="hi" else
            "❗ Kripya pehle problem choose karein."
        )
        return

    header = (
        f"📩 New Support Request\n\n"
        f"👤 Name: {user.first_name or ''} {user.last_name or ''}\n"
        f"🔗 Username: @{user.username or 'Not available'}\n"
        f"🆔 User ID: {user.id}\n"
        f"📌 Issue Type: {issue_type}\n\n"
        f"📝 User Message:"
    )

    try:
        if update.message.text:
            sent_msg = await context.bot.send_message(
                chat_id=SUPPORT_GROUP_ID,
                text=f"{header}\n{update.message.text}"
            )
        else:
            sent_msg = await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=header)
            await update.message.forward(chat_id=SUPPORT_GROUP_ID)

        # 🔹 Store mapping: group_message_id -> user_id
        context.bot_data[sent_msg.message_id] = user.id

    except Exception as e:
        logging.error(f"Error forwarding message: {e}")

    context.user_data.pop("issue_type", None)

    thanks_msg = {
        "en": "🙏 Thank you! Your request has been forwarded. Our team will contact you soon. 😊",
        "hi": "🙏 धन्यवाद! आपकी रिक्वेस्ट भेज दी गई है। हमारी टीम जल्द ही आपसे संपर्क करेगी। 😊",
        "hin": "🙏 Thank you! Aapki request forward kar di gayi hai. Hamari team jald hi aapse contact karegi. 😊"
    }
    await update.message.reply_text(thanks_msg[lang])

# 🔹 Forward agent replies to user (Swipe-to-reply works!)
async def reply_from_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != SUPPORT_GROUP_ID:
        return

    reply = update.message.reply_to_message
    if not reply:
        return  # Only process replies

    user_id = context.bot_data.get(reply.message_id)
    if not user_id:
        return  # Could not find mapping

    try:
        if update.message.text:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"💬 Support Reply:\n{update.message.text}"
            )
        else:
            await update.message.forward(chat_id=user_id)
    except Exception as e:
        logging.error(f"Error forwarding agent reply: {e}")

# 🔹 Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_handler, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(issue_handler, pattern="^(Deposit|Withdrawal|Other)$"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_message))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, reply_from_group))  # Swipe-to-reply

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()