import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command

BOT_TOKEN = "8658587944:AAGx_gs1LyUQ62V64zAup9CrdkXAii7LhFo"
GROUP_ID = -1003792957294

FIRMALAR = ["Firma 1", "Firma 2", "Firma 3", "Firma 4"]
LAVOZIMLAR = ["Ish boshqaruvchi", "Sotuvchi", "Yuklovchi", "Haydovchi", "Usta"]

logging.basicConfig(level=logging.INFO)

class Anketa(StatesGroup):
    firma = State()
    lavozim = State()
    ism = State()
    yosh = State()
    telefon = State()
    manzil = State()
    tajriba = State()
    oldingi_ish = State()
    sabab = State()
    rasm = State()

def firma_keyboard():
    buttons = [[KeyboardButton(text=f)] for f in FIRMALAR]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

def lavozim_keyboard():
    buttons = [[KeyboardButton(text=l)] for l in LAVOZIMLAR]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(Anketa.firma)
    await message.answer(
        "👋 Xush kelibsiz! HR Anketa Botiga!\n\nQaysi firmaga murojaat qilmoqchisiz?",
        reply_markup=firma_keyboard()
    )

@dp.message(Anketa.firma)
async def get_firma(message: Message, state: FSMContext):
    if message.text not in FIRMALAR:
        await message.answer("Iltimos, quyidagi firmalardan birini tanlang:", reply_markup=firma_keyboard())
        return
    await state.update_data(firma=message.text)
    await state.set_state(Anketa.lavozim)
    await message.answer(
        f"✅ {message.text} tanlandi!\n\nQaysi lavozimga murojaat qilmoqchisiz?",
        reply_markup=lavozim_keyboard()
    )

@dp.message(Anketa.lavozim)
async def get_lavozim(message: Message, state: FSMContext):
    if message.text not in LAVOZIMLAR:
        await message.answer("Iltimos, quyidagi lavozimlardan birini tanlang:", reply_markup=lavozim_keyboard())
        return
    await state.update_data(lavozim=message.text)
    await state.set_state(Anketa.ism)
    await message.answer("📝 Anketa boshlanadi!\n\n1️⃣ Ism va Familiyangizni kiriting:", reply_markup=ReplyKeyboardRemove())

@dp.message(Anketa.ism)
async def get_ism(message: Message, state: FSMContext):
    await state.update_data(ism=message.text)
    await state.set_state(Anketa.yosh)
    await message.answer("2️⃣ Yoshingizni kiriting:")

@dp.message(Anketa.yosh)
async def get_yosh(message: Message, state: FSMContext):
    await state.update_data(yosh=message.text)
    await state.set_state(Anketa.telefon)
    await message.answer("3️⃣ Telefon raqamingizni kiriting (+998XXXXXXXXX):")

@dp.message(Anketa.telefon)
async def get_telefon(message: Message, state: FSMContext):
    await state.update_data(telefon=message.text)
    await state.set_state(Anketa.manzil)
    await message.answer("4️⃣ Yashash manzilingizni kiriting (Shahar, tuman):")

@dp.message(Anketa.manzil)
async def get_manzil(message: Message, state: FSMContext):
    await state.update_data(manzil=message.text)
    await state.set_state(Anketa.tajriba)
    await message.answer("5️⃣ Ish tajribangiz necha yil?")

@dp.message(Anketa.tajriba)
async def get_tajriba(message: Message, state: FSMContext):
    await state.update_data(tajriba=message.text)
    await state.set_state(Anketa.oldingi_ish)
    await message.answer("6️⃣ Oldingi ish joyingiz qayer edi?")

@dp.message(Anketa.oldingi_ish)
async def get_oldingi_ish(message: Message, state: FSMContext):
    await state.update_data(oldingi_ish=message.text)
    await state.set_state(Anketa.sabab)
    await message.answer("7️⃣ Nega aynan shu lavozimga murojaat qilmoqdasiz?")

@dp.message(Anketa.sabab)
async def get_sabab(message: Message, state: FSMContext):
    await state.update_data(sabab=message.text)
    await state.set_state(Anketa.rasm)
    await message.answer("8️⃣ Rasmingizni yuboring (selfie yoki passport foto):")

@dp.message(Anketa.rasm, F.photo)
async def get_rasm(message: Message, state: FSMContext):
    d = await state.get_data()
    photo = message.photo[-1]

    caption = (
        f"📋 *YANGI ANKETA*\n\n"
        f"🏢 *Firma:* {d.get('firma', '-')}\n"
        f"💼 *Lavozim:* {d.get('lavozim', '-')}\n\n"
        f"👤 *Ism Familiya:* {d.get('ism', '-')}\n"
        f"🎂 *Yosh:* {d.get('yosh', '-')}\n"
        f"📞 *Telefon:* {d.get('telefon', '-')}\n"
        f"📍 *Manzil:* {d.get('manzil', '-')}\n"
        f"🗓 *Tajriba:* {d.get('tajriba', '-')} yil\n"
        f"🏭 *Oldingi ish joyi:* {d.get('oldingi_ish', '-')}\n"
        f"💬 *Murojaat sababi:* {d.get('sabab', '-')}\n"
    )

    await bot.send_photo(chat_id=GROUP_ID, photo=photo.file_id, caption=caption, parse_mode="Markdown")
    await message.answer(
        "✅ Anketangiz muvaffaqiyatli yuborildi!\n\nSiz bilan tez orada bog'lanamiz. Rahmat! 🙏",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

@dp.message(Anketa.rasm)
async def rasm_xato(message: Message):
    await message.answer("Iltimos, rasm yuboring (faqat rasm qabul qilinadi):")

async def main():
    logging.info("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
