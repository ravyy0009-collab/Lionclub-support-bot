# bot.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# 🔴 Configuration
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

# 🔹 Issue selection handler with step-by-step messages
async def issue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    issue_type = query.data
    context.user_data["issue_type"] = issue_type
    lang = context.user_data.get("lang", "en")

    messages = {
        "Deposit": {
            "en": (
                "💰 Deposit Issue Selected.\n\n"
                "Step 1️⃣: Send your UID.\n"
                "Step 2️⃣: Send Payment Screenshot.\n"
                "Step 3️⃣: Send In-game Deposit Screenshot.\n\n"
                "Our support team will process your request as soon as possible. 😊"
            ),
            "hi": (
                "💰 डिपॉज़िट समस्या चुनी गई है।\n\n"
                "Step 1️⃣: अपना यूज़र आईडी (UID) भेजें।\n"
                "Step 2️⃣: पेमेंट की स्क्रीनशॉट भेजें।\n"
                "Step 3️⃣: इन-गेम डिपॉज़िट की स्क्रीनशॉट भेजें।\n\n"
                "हमारी सपोर्ट टीम आपकी रिक्वेस्ट जल्दी प्रोसेस करेगी। 😊"
            ),
            "hin": (
                "💰 Deposit Issue Selected.\n\n"
                "Step 1️⃣: Apna UID bhejein.\n"
                "Step 2️⃣: Payment ki screenshot bhejein.\n"
                "Step 3️⃣: In-game Deposit ki screenshot bhejein.\n\n"
                "Hamari support team aapki request jaldi process karegi. 😊"
            )
        },
        "Withdrawal": {
            "en": (
                "🏦 Withdrawal Issue Selected.\n\n"
                "Step 1️⃣: Send your UID.\n"
                "Step 2️⃣: Send Withdrawal Screenshot.\n\n"
                "Our support team will process your withdrawal as soon as possible. 😊"
            ),
            "hi": (
                "🏦 विदड्रॉवल समस्या चुनी गई है।\n\n"
                "Step 1️⃣: अपना यूज़र आईडी (UID) भेजें।\n"
                "Step 2️⃣: विदड्रॉवल की स्क्रीनशॉट भेजें।\n\n"
                "हमारी सपोर्ट टीम आपकी रिक्वेस्ट जल्दी प्रोसेस करेगी। 😊"
            ),
            "hin": (
                "🏦 Withdrawal Issue Selected.\n\n"
                "Step 1️⃣: Apna UID bhejein.\n"
                "Step 2️⃣: Withdrawal ki screenshot bhejein.\n\n"
                "Hamari support team aapki request jaldi process karegi. 😊"
            )
        },
        "Other": {
            "en": (
                "❓ Other Issue Selected.\n\n"
                "Step 1️⃣: Describe your issue clearly.\n"
                "Step 2️⃣: Attach any screenshots if needed.\n\n"
                "Our support team will respond as soon as possible. 😊"
            ),
            "hi": (
                "❓ अन्य समस्या चुनी गई है।\n\n"
                "Step 1️⃣: अपनी समस्या विस्तार से बताएं।\n"
                "Step 2️⃣: स्क्रीनशॉट संलग्न करें यदि ज़रूरी हो।\n\n"
                "हमारी टीम जल्द ही आपसे संपर्क करेगी। 😊"
            ),
            "hin": (
                "❓ Other Issue Selected.\n\n"
                "Step 1️⃣: Apni problem clearly batayein.\n"
                "Step 2️⃣: Screenshots attach karein agar zaroori ho.\n\n"
                "Hamari support team jald hi aapse contact karegi. 😊"
            )
        }
    }

    await query.message.reply_text(messages[issue_type][lang])

# 🔹 Forward user message + Reply button
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = context.user_data.get("lang", "en")
    issue_type = context.user_data.get("issue_type")

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

    context.bot_data[sent_msg.message_id] = user.id
    context.user_data.pop("issue_type", None)

    thanks_msg = {
        "en": "🙏 Thank you! Your request has been forwarded. Our team will contact you soon. 😊",
        "hi": "🙏 धन्यवाद! आपकी रिक्वेस्ट भेज दी गई है। हमारी टीम जल्द ही आपसे संपर्क करेगी। 😊",
        "hin": "🙏 Thank you! Aapki request forward kar di gayi hai. Hamari team jald hi aapse contact karegi. 😊"
    }
    await update.message.reply_text(thanks_msg[lang])

# 🔹 Reply button click
async def reply_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.replace("reply_", ""))
    context.user_data["reply_to_user"] = user_id
    await query.message.reply_text("📝 Please type your reply to the user now:")

# 🔹 Agent types reply → send to user only
async def agent_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get("reply_to_user")
    if not user_id:
        return  # Normal messages

    try:
        if update.message.text:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"💬 Support Reply:\n{update.message.text}"
            )
        else:
            await update.message.forward(chat_id=user_id)
    except Exception as e:
        logging.error(f"Error sending reply to user: {e}")

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
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, agent_reply_handler))

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()