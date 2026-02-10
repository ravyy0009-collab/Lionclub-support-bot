# bot.py
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from random import randint

API_TOKEN = "8252550418:AAGknB7OFHtGisQBoGFEvfPWiW3uWB-4gcE"
SUPPORT_GROUP_ID = -1003883601919  # Your updated support group ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ---------------- STATES ----------------
class SupportState(StatesGroup):
    language = State()
    issue_type = State()
    details = State()

# ---------------- START ----------------
@dp.message()
async def start_command(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("English 🇺🇸", callback_data="lang_en"),
        InlineKeyboardButton("Hindi 🇮🇳", callback_data="lang_hi"),
        InlineKeyboardButton("Hinglish 🇮🇳🇬🇧", callback_data="lang_hinglish")
    )
    await message.answer("👋 Hello! Welcome to Line Club Support Bot!\nPlease choose your language:", reply_markup=keyboard)
    await state.set_state(SupportState.language)

# ---------------- LANGUAGE SELECTION ----------------
@dp.callback_query(SupportState.language)
async def process_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(selected_lang=lang)

    # Issue buttons
    keyboard = InlineKeyboardMarkup(row_width=1)
    if lang == "hi":
        issues = ["डिपॉजिट समस्या", "विड्रॉल समस्या", "अन्य"]
        text = "कृपया अपनी समस्या चुनें:"
    elif lang == "hinglish":
        issues = ["Deposit ki problem", "Withdrawal ki problem", "Other"]
        text = "Apni problem select karein:"
    else:
        issues = ["Deposit Problem", "Withdrawal Problem", "Other"]
        text = "Please select your issue:"

    for issue in issues:
        keyboard.add(InlineKeyboardButton(issue, callback_data=f"issue_{issue}"))

    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(SupportState.issue_type)

# ---------------- ISSUE SELECTION ----------------
@dp.callback_query(SupportState.issue_type)
async def process_issue(callback: types.CallbackQuery, state: FSMContext):
    issue = callback.data.split("_")[1]
    data = await state.get_data()
    lang = data.get("selected_lang")
    await state.update_data(selected_issue=issue)

    # Step-by-step instructions
    if lang == "hi":
        prompt = "कृपया सब चीज़ें **एक ही मेसेज में** भेजें:\n1️⃣ UID\n2️⃣ Payment / Withdrawal screenshot\n3️⃣ Game screenshot (agar applicable ho)"
    elif lang == "hinglish":
        prompt = "Plz sab cheezein **ek hi message me** bhejein:\n1️⃣ UID\n2️⃣ Payment / Withdrawal screenshot\n3️⃣ Game screenshot (agar applicable ho)"
    else:
        prompt = "Please send all things **in a single message**:\n1️⃣ UID\n2️⃣ Payment / Withdrawal screenshot\n3️⃣ Game screenshot (if applicable)"

    await bot.send_message(callback.from_user.id, prompt)
    await state.set_state(SupportState.details)

# ---------------- FORWARD MEDIA + TEXT ----------------
ticket_user_map = {}  # ticket_number -> user_id

@dp.message(SupportState.details)
async def process_details(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("selected_lang")
    issue = data.get("selected_issue")

    # Generate ticket number
    ticket_number = randint(1000, 9999)
    ticket_user_map[ticket_number] = message.from_user.id

    # Forward all media together
    media_group = []
    if message.photo:
        for p in message.photo:
            media_group.append(types.InputMediaPhoto(media=p.file_id))
    elif message.document:
        media_group.append(types.InputMediaDocument(media=message.document.file_id))

    if media_group:
        await bot.send_media_group(SUPPORT_GROUP_ID, media_group)

    # Send text with user info
    username = message.from_user.username or "N/A"
    fullname = message.from_user.full_name or "N/A"
    text = f"🆕 New Ticket #{ticket_number}\n👤 User: @{username}\n📝 Full Name: {fullname}\nIssue: {issue}\nMessage: {message.text or 'Media Sent'}"
    
    # Reply + Resolved buttons
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Reply 💬", callback_data=f"reply_{ticket_number}"),
        InlineKeyboardButton("Resolved ✅", callback_data=f"resolved_{ticket_number}")
    )

    await bot.send_message(SUPPORT_GROUP_ID, text, reply_markup=keyboard)

    # Auto acknowledgement to user
    if lang == "hi":
        ack = f"🙏 आपका ticket #{ticket_number} receive हो गया है। हमारी टीम जल्दी ही आपका issue resolve करेगी।"
    elif lang == "hinglish":
        ack = f"🙏 Apka ticket #{ticket_number} receive ho gaya hai. Hamari team jaldi aapka issue resolve karegi."
    else:
        ack = f"🙏 Your ticket #{ticket_number} has been received. Our team will resolve it soon."

    await message.reply(ack)
    await state.clear()

# ---------------- GROUP REPLY ----------------
@dp.callback_query()
async def group_reply_resolve(callback: types.CallbackQuery):
    data = callback.data
    if data.startswith("reply_"):
        ticket = int(data.split("_")[1])
        user_id = ticket_user_map.get(ticket)
        if user_id:
            # send message back to user
            await bot.send_message(user_id, f"💬 Support Reply for Ticket #{ticket}")
            await callback.answer("Reply sent to user!")
    elif data.startswith("resolved_"):
        ticket = int(data.split("_")[1])
        await callback.message.edit_text(callback.message.text + "\n✅ Ticket resolved")
        await callback.answer("Ticket marked as resolved!")

# ---------------- RUN BOT ----------------
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))