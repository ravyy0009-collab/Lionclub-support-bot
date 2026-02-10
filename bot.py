# bot.py
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- CONFIG ---
API_TOKEN = os.getenv("8252550418:AAGknB7OFHtGisQBoGFEvfPWiW3uWB-4gcE")  # Set in Railway Environment
SUPPORT_GROUP_ID = -1003883601919

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- STATES ---
class SupportState(StatesGroup):
    language = State()
    issue_type = State()
    details = State()

# --- START COMMAND ---
@dp.message(Command(commands=["start"]))
async def start_cmd(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("English 🇺🇸", callback_data="lang_en")],
        [InlineKeyboardButton("Hindi 🇮🇳", callback_data="lang_hi")],
        [InlineKeyboardButton("Hinglish 📝", callback_data="lang_hinglish")]
    ])
    await message.answer("👋 Welcome! Please select your language:", reply_markup=keyboard)
    await state.set_state(SupportState.language)

# --- LANGUAGE SELECTION ---
@dp.callback_query(SupportState.language)
async def language_selected(query: CallbackQuery, state: FSMContext):
    lang = query.data.split("_")[1]
    await state.update_data(selected_lang=lang)

    if lang == "en":
        buttons = ["Withdrawal Problem", "Deposit Problem", "Other"]
        text = "Please select your issue:"
    elif lang == "hi":
        buttons = ["विथड्रॉल समस्या", "डिपॉजिट समस्या", "अन्य"]
        text = "कृपया अपनी समस्या चुनें:"
    else:
        buttons = ["Withdrawal Problem", "Deposit Problem", "Other"]
        text = "Plz select kar apni problem:"

    keyboard = InlineKeyboardMarkup(row_width=1)
    for b in buttons:
        keyboard.add(InlineKeyboardButton(b, callback_data=f"issue_{b}"))

    await query.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(SupportState.issue_type)

# --- ISSUE SELECTION ---
@dp.callback_query(SupportState.issue_type)
async def issue_selected(query: CallbackQuery, state: FSMContext):
    issue = query.data.split("_")[1]
    data = await state.get_data()
    lang = data.get("selected_lang")
    await state.update_data(selected_issue=issue)

    if lang == "en":
        if "Withdrawal" in issue:
            msg = "Step 1️⃣: Send your UID\nStep 2️⃣: Send Withdrawal Screenshot\n⚠️ Please send all details in one message."
        elif "Deposit" in issue:
            msg = "Step 1️⃣: Send your UID\nStep 2️⃣: Send Payment Screenshot\nStep 3️⃣: Send In-game Deposit Screenshot\n⚠️ Please send all details in one message."
        else:
            msg = "Please describe your issue in detail.\n⚠️ Send all media + text in ONE message."
    elif lang == "hi":
        if "विथड्रॉल" in issue:
            msg = "स्टेप 1️⃣: अपना UID भेजें\nस्टेप 2️⃣: विथड्रॉल स्क्रीनशॉट भेजें\n⚠️ कृपया सभी चीजें एक ही मैसेज में भेजें।"
        elif "डिपॉजिट" in issue:
            msg = "स्टेप 1️⃣: अपना UID भेजें\nस्टेप 2️⃣: पेमेंट स्क्रीनशॉट भेजें\nस्टेप 3️⃣: इन-गेम डिपॉजिट स्क्रीनशॉट भेजें\n⚠️ सभी चीजें एक ही मैसेज में भेजें।"
        else:
            msg = "कृपया विस्तार से अपनी समस्या बताएं।\n⚠️ सभी मीडिया + टेक्स्ट एक ही मैसेज में भेजें।"
    else:  # Hinglish
        msg = "Step 1️⃣: Apna UID bhejo\nStep 2️⃣: Screenshots bhejo\n⚠️ Sab ek hi message me bhejna."

    await query.message.answer(msg)
    await state.set_state(SupportState.details)

# --- FORWARD TO SUPPORT GROUP ---
@dp.message(SupportState.details)
async def forward_to_support(message: types.Message, state: FSMContext):
    data = await state.get_data()
    issue = data.get("selected_issue")
    lang = data.get("selected_lang")
    
    # Forward media + text
    media_group = []
    if message.media_group_id:
        async for m in bot.get_media_group(chat_id=message.chat.id, message_id=message.message_id):
            media_group.append(m)
    else:
        media_group.append(message)
    
    username = message.from_user.username or "NoUsername"
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    
    # Send initial ticket info
    ticket_text = f"🆕 New Ticket\nUser: @{username}\nFull Name: {full_name}\nIssue: {issue}"
    
    # Reply + Resolved buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Reply 💬", callback_data=f"reply_{message.from_user.id}")],
        [InlineKeyboardButton("Resolved ✅", callback_data=f"resolve_{message.from_user.id}")]
    ])
    
    await bot.send_message(SUPPORT_GROUP_ID, ticket_text, reply_markup=keyboard)
    
    # Forward media + text
    for m in media_group:
        await m.forward(SUPPORT_GROUP_ID)
    
    # Confirmation to user
    if lang == "en":
        reply = "✅ Your ticket has been received. Our team will resolve it ASAP. Please be patient!"
    elif lang == "hi":
        reply = "✅ आपकी टिकट रिसीव हो गई है। हमारी टीम इसे जल्द हल करेगी। कृपया धैर्य रखें।"
    else:
        reply = "✅ Ticket receive ho gaya! Team soon solve karegi, plz wait."

    await message.answer(reply)
    await state.clear()

# --- SUPPORT GROUP BUTTONS ---
@dp.callback_query(lambda c: c.data.startswith("reply_"))
async def admin_reply(query: CallbackQuery):
    user_id = int(query.data.split("_")[1])
    msg = query.message.reply_to_message
    if msg:
        await bot.send_message(user_id, f"💬 Reply from Support:\n{msg.text or ''}")

@dp.callback_query(lambda c: c.data.startswith("resolve_"))
async def admin_resolve(query: CallbackQuery):
    user_id = int(query.data.split("_")[1])
    await bot.send_message(user_id, "✅ Your issue has been marked as resolved. Thank you for contacting Line Club Bot!")

# --- RUN BOT ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())