# file: bot.py

import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import datetime

# ---------------- CONFIGURATION ----------------
API_TOKEN = "8252550418:AAGknB7OFHtGisQBoGFEvfPWiW3uWB-4gcE"
SUPPORT_GROUP_ID = -1003883601919  # Replace with your support group ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ---------------- STATES ----------------
class SupportState(StatesGroup):
    language = State()
    issue_type = State()
    details = State()

class AdminReplyState(StatesGroup):
    replying_to_user = State()

# ---------------- TICKET COUNTER ----------------
TICKET_COUNTER = 0
def generate_ticket_id():
    global TICKET_COUNTER
    TICKET_COUNTER += 1
    return f"TICKET-{TICKET_COUNTER:03d}"

# ---------------- HELPER TEXTS ----------------
LANG_TEXTS = {
    "en": {
        "select_issue": "Please select your issue 👇",
        "deposit": "Deposit Problem",
        "withdrawal": "Withdrawal Problem",
        "other": "Other Problem",
        "prompt_deposit": "Step 1️⃣: Send your UID\nStep 2️⃣: Payment screenshot\nStep 3️⃣: In-game deposit screenshot\n⚠️ Please send all files together in single message.",
        "prompt_withdrawal": "Step 1️⃣: Send your UID\nStep 2️⃣: Withdrawal screenshot\n⚠️ Please send all files together in single message.",
        "prompt_other": "Please describe your problem in detail.\n⚠️ Please send all files together in single message.",
        "acknowledge": "🎉 Your ticket {ticket_id} has been received. Our team will resolve your issue as soon as possible. Thank you for contacting Line Club Bot!",
        "resolved_user": "✅ Your issue {ticket_id} is resolved. Thank you for using our support!",
        "welcome": "👋 Welcome! Please choose your language to get started."
    },
    "hinglish": {
        "select_issue": "Kripya apni problem select karein 👇",
        "deposit": "Deposit Ki Problem",
        "withdrawal": "Withdrawal Ki Problem",
        "other": "Other Problem",
        "prompt_deposit": "Step 1️⃣: Apna UID bheje\nStep 2️⃣: Payment screenshot bheje\nStep 3️⃣: In-game deposit screenshot bheje\n⚠️ Kripya sari cheezein ek sath bhejein.",
        "prompt_withdrawal": "Step 1️⃣: Apna UID bheje\nStep 2️⃣: Withdrawal screenshot bheje\n⚠️ Kripya sari cheezein ek sath bhejein.",
        "prompt_other": "Kripya apni problem detail me batayein.\n⚠️ Kripya sari cheezein ek sath bhejein.",
        "acknowledge": "🎉 Aapki ticket {ticket_id} receive ho gayi hai. Humari team aapka issue jaldi solve karegi. Thanks for contacting Line Club Bot!",
        "resolved_user": "✅ Aapka issue {ticket_id} resolve ho gaya. Thank you for using our support!",
        "welcome": "👋 Welcome! Start karne ke liye apni language choose karein."
    },
    "hi": {
        "select_issue": "कृपया अपनी समस्या चुनें 👇",
        "deposit": "डिपॉजिट समस्या",
        "withdrawal": "विथड्रॉल समस्या",
        "other": "अन्य समस्या",
        "prompt_deposit": "स्टेप 1️⃣: अपना UID भेजें\nस्टेप 2️⃣: पेमेंट स्क्रीनशॉट\nस्टेप 3️⃣: गेम में डिपॉजिट स्क्रीनशॉट\n⚠️ कृपया सारी चीज़ें एक साथ भेजें।",
        "prompt_withdrawal": "स्टेप 1️⃣: अपना UID भेजें\nस्टेप 2️⃣: विथड्रॉल स्क्रीनशॉट\n⚠️ कृपया सारी चीज़ें एक साथ भेजें।",
        "prompt_other": "कृपया अपनी समस्या विस्तार से बताएं।\n⚠️ कृपया सारी चीज़ें एक साथ भेजें।",
        "acknowledge": "🎉 आपकी टिकट {ticket_id} receive हो गई है। हमारी टीम आपकी समस्या जल्द हल करेगी। Line Club Bot से संपर्क करने के लिए धन्यवाद!",
        "resolved_user": "✅ आपकी समस्या {ticket_id} resolve हो गई। हमारी सपोर्ट टीम का धन्यवाद!",
        "welcome": "👋 स्वागत है! शुरू करने के लिए अपनी भाषा चुनें।"
    }
}

# ---------------- START ----------------
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("English 🇺🇸", callback_data="lang_en"),
        types.InlineKeyboardButton("Hinglish 🇮🇳", callback_data="lang_hinglish"),
        types.InlineKeyboardButton("हिंदी 🇮🇳", callback_data="lang_hi")
    )
    await message.answer(LANG_TEXTS["en"]["welcome"], reply_markup=keyboard)
    await SupportState.language.set()

# ---------------- LANGUAGE SELECTION ----------------
@dp.callback_query_handler(state=SupportState.language)
async def process_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(selected_lang=lang)

    texts = LANG_TEXTS[lang]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(texts["withdrawal"], callback_data="issue_withdrawal"),
        types.InlineKeyboardButton(texts["deposit"], callback_data="issue_deposit"),
        types.InlineKeyboardButton(texts["other"], callback_data="issue_other")
    )
    await bot.edit_message_text(
        texts["select_issue"], 
        callback.from_user.id, 
        callback.message.message_id, 
        reply_markup=keyboard
    )
    await SupportState.issue_type.set()

# ---------------- ISSUE TYPE ----------------
@dp.callback_query_handler(state=SupportState.issue_type)
async def process_issue(callback: types.CallbackQuery, state: FSMContext):
    issue = callback.data.split("_")[1]
    await state.update_data(selected_issue=issue)

    data = await state.get_data()
    lang = data.get("selected_lang")
    texts = LANG_TEXTS[lang]

    if issue == "deposit":
        prompt = texts["prompt_deposit"]
    elif issue == "withdrawal":
        prompt = texts["prompt_withdrawal"]
    else:
        prompt = texts["prompt_other"]

    await bot.send_message(callback.from_user.id, prompt)
    await SupportState.details.set()

# ---------------- FINAL STEP: FORWARD + TICKET ID ----------------
@dp.message_handler(state=SupportState.details, content_types=types.ContentTypes.ANY)
async def final_step(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("selected_lang")
    issue = data.get("selected_issue")
    texts = LANG_TEXTS[lang]

    # Ticket ID
    ticket_id = generate_ticket_id()

    # User Info
    username = f"@{message.from_user.username}" if message.from_user.username else "No username"
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    user_info = f"🆕 New Ticket: {ticket_id}\nUsername: {username}\nFull Name: {full_name}\nIssue: {issue}\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Group Inline Keyboard
    group_kb = types.InlineKeyboardMarkup(row_width=2)
    group_kb.add(
        types.InlineKeyboardButton("Reply 💬", callback_data=f"group_reply_{message.from_user.id}_{ticket_id}"),
        types.InlineKeyboardButton("Resolved ✅", callback_data=f"group_resolved_{message.from_user.id}_{ticket_id}")
    )

    # MediaGroup handling
    if message.media_group_id:
        media = []
        for msg in await bot.get_media_group(chat_id=message.chat.id, message_id=message.message_id):
            if msg.content_type == "photo":
                media.append(types.InputMediaPhoto(media=msg.photo[-1].file_id, caption=msg.caption))
            elif msg.content_type == "video":
                media.append(types.InputMediaVideo(media=msg.video.file_id, caption=msg.caption))
            elif msg.content_type == "document":
                await bot.send_document(SUPPORT_GROUP_ID, msg.document.file_id, caption=msg.caption)
        if media:
            await bot.send_message(SUPPORT_GROUP_ID, user_info, reply_markup=group_kb)
            await bot.send_media_group(SUPPORT_GROUP_ID, media)
    else:
        await bot.send_message(SUPPORT_GROUP_ID, user_info, reply_markup=group_kb)
        await message.forward(SUPPORT_GROUP_ID)

    # Auto Acknowledgment to user
    await message.reply(texts["acknowledge"].format(ticket_id=ticket_id))
    await state.finish()

# ---------------- ADMIN REPLY ----------------
@dp.callback_query_handler(lambda c: c.data.startswith("group_reply_"))
async def group_reply(callback: types.CallbackQuery):
    _, user_id, ticket_id = callback.data.split("_")[2:]
    user_id = int(user_id)
    state = dp.current_state(chat=callback.from_user.id, user=callback.from_user.id)
    await state.set_state(AdminReplyState.replying_to_user.state)
    await state.update_data(target_user_id=user_id, ticket_id=ticket_id)
    await callback.message.answer(f"✏️ Please type your reply to send to user (Ticket {ticket_id})")
    await callback.answer()

@dp.message_handler(state=AdminReplyState.replying_to_user, content_types=types.ContentTypes.ANY)
async def admin_reply_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    ticket_id = data.get("ticket_id")
    
    # Forward media or text
    if message.media_group_id:
        media = []
        for msg in await bot.get_media_group(chat_id=message.chat.id, message_id=message.message_id):
            if msg.content_type == "photo":
                media.append(types.InputMediaPhoto(media=msg.photo[-1].file_id, caption=msg.caption))
            elif msg.content_type == "video":
                media.append(types.InputMediaVideo(media=msg.video.file_id, caption=msg.caption))
            elif msg.content_type == "document":
                await bot.send_document(target_user_id, msg.document.file_id, caption=msg.caption)
        if media:
            await bot.send_media_group(target_user_id, media)
    else:
        await message.forward(target_user_id)

    # Reply log in group
    await message.reply(f"💬 Admin replied to {ticket_id} ✅")
    await state.finish()

# ---------------- RESOLVED ----------------
@dp.callback_query_handler(lambda c: c.data.startswith("group_resolved_"))
async def group_resolved(callback: types.CallbackQuery):
    _, user_id, ticket_id = callback.data.split("_")[2:]
    user_id = int(user_id)
    # Send resolved message to user
    for lang in LANG_TEXTS:
        text = LANG_TEXTS[lang]["resolved_user"].format(ticket_id=ticket_id)
        break  # Just use one language for resolved, can customize
    await bot.send_message(user_id, text)
    await callback.answer("Marked as resolved.")

# ---------------- RUN ----------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)