# bot.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# 🔴 Config
BOT_TOKEN = "8252550418:AAFR5FJ2h3zFsmOfcqF-j8D_3KyM-tc2_II"  # Replace with your token
SUPPORT_GROUP_ID = -1003883601919  # Replace with your support group ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🔹 Language buttons
def language_keyboard():
    keyboard = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("हिंदी 🇮🇳", callback_data="lang_hi")],
        [InlineKeyboardButton("Hinglish 📝", callback_data="lang_hin")],
    ]
    return InlineKeyboardMarkup(keyboard)

# 🔹 Issue buttons
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

# 🔹 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Welcome to Lion Club Support!\nPlease choose your preferred language:",
        reply_markup=language_keyboard()
    )

# 🔹 Language selection
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

# 🔹 Issue selection
async def issue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    issue_type = query.data
    context.user_data["issue_type"] = issue_type
    lang = context.user_data.get("lang", "en")

    messages = {
        "Deposit": {
            "en": "💰 Deposit Issue Selected.\nSend UID + Payment Screenshot + In-game Deposit Screenshot in one message.\nThis helps our support team process your request faster. 😊",
            "hi": "💰 डिपॉज़िट समस्या चुनी गई है।\nकृपया एक ही मैसेज में निम्नलिखित भेजें:\n- 🆔 आपका यूज़र आईडी (UID)\n- 💳 पेमेंट की स्क्रीनशॉट\n- 🕹️ इन-गेम डिपॉज़िट की स्क्रीनशॉट\nइससे हमारी सपोर्ट टीम आपकी मदद जल्दी कर पाएगी। 😊",
            "hin": "💰 Deposit Issue Selected.\nKripya ek hi message mein yeh sab bhejein:\n- 🆔 Aapka User ID (UID)\n- 💳 Payment ki screenshot\n- 🕹️ In-game deposit ki screenshot\nIsse hamari support team aapki madad jaldi kar sakegi. 😊"
        },
        "Withdrawal": {
            "en": "🏦 Withdrawal Issue Selected.\nSend UID + Withdrawal Screenshot in one message.\nOur team will handle your withdrawal request quickly. 😊",
            "hi": "🏦 विदड्रॉवल समस्या चुनी गई है।\nकृपया एक ही मैसेज में निम्नलिखित भेजें:\n- 🆔 आपका यूज़र आईडी (UID)\n- 📸 विदड्रॉवल स्क्रीनशॉट\nहमारी टीम आपकी विदड्रॉवल रिक्वेस्ट जल्दी प्रोसेस करेगी। 😊",
            "hin": "🏦 Withdrawal Issue Selected.\nKripya ek hi message mein yeh sab bhejein:\n- 🆔 Aapka User ID (UID)\n- 📸 Withdrawal ki screenshot\nHamari team aapki withdrawal request jaldi process karegi. 😊"
        },
        "Other": {
            "en": "❓ Other Issue Selected.\nDescribe your issue clearly with screenshots in one message.\nOur team will respond as soon as possible. 😊",
            "hi": "❓ अन्य समस्या चुनी गई है।\nकृपया अपनी समस्या विस्तार से और स्क्रीनशॉट के साथ भेजें।\nहमारी टीम जल्द ही आपसे संपर्क करेगी। 😊",
            "hin": "❓ Other Issue Selected.\nKripya apni problem detail mein batayein aur screenshots ek hi message mein bhejein.\nHamari team jald hi aapse contact karegi. 😊"
        }
    }

    await query.message.reply_text(messages[issue_type][lang])

# 🔹 Forward user messages + add Reply button
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = context.user_data.get("lang", "en")
    issue_type = context.user_data.get("issue_type", "Not selected")

    header = (
        f"📩 New Support Request\n\n"
        f"👤 Name: {user.first_name or ''} {user.last_name or ''}\n"
        f"🔗 Username: @{user.username or 'Not available'}\n"
        f"🆔 User ID: {user.id}\n"
        f"📌 Issue Type: {issue_type}\n\n"
        f"📝 User Message:"
    )

    text = header
    if update.message.text:
        text += f"\n{update.message.text}"

    # Inline Reply button
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("💬 Reply to User", callback_data=f"reply_{user.id}")]]
    )

    sent_msg = await context.bot.send_message(
        chat_id=SUPPORT_GROUP_ID,
        text=text,
        reply_markup=keyboard
    )

    # Store mapping
    context.bot_data[sent_msg.message_id] = user.id

    # Clear issue_type
    context.user_data.pop("issue_type", None)

    thanks_msg = {
        "en": "🙏 Thank you! Your request has been forwarded. Our team will contact you soon. 😊",
        "hi": "🙏 धन्यवाद! आपकी रिक्वेस्ट भेज दी गई है। हमारी टीम जल्द ही आपसे संपर्क करेगी। 😊",
        "hin": "🙏 Thank you! Aapki request forward kar di gayi hai. Hamari team jald hi aapse contact karegi. 😊"
    }
    await update.message.reply_text(thanks_msg[lang])

# 🔹 Handle Reply button click
async def reply_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.replace("reply_", ""))
    context.user_data["reply_to_user"] = user_id
    await query.message.reply_text("📝 Please type your reply to the user now:")

# 🔹 Send agent reply to user
async def send_reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get("reply_to_user")
    if not user_id:
        return
    try:
        if update.message.text:
            await context.bot.send_message(chat_id=user_id, text=f"💬 Support Reply:\n{update.message.text}")
        else:
            await update.message.forward(chat_id=user_id)
    except Exception as e:
        logging.error(f"Error sending agent reply: {e}")

    context.user_data.pop("reply_to_user", None)
    await update.message.reply_text("✅ Reply sent to user successfully!")

# 🔹 Main
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_handler, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(issue_handler, pattern="^(Deposit|Withdrawal|Other)$"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_message))
    app.add_handler(CallbackQueryHandler(reply_button_handler, pattern="^reply_"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, send_reply_to_user))

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()