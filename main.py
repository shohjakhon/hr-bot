import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

BOT_TOKEN = "8658587944:AAGx_gs1LyUQ62V64zAup9CrdkXAii7LhFo"
GROUP_ID = -1003792957294

FIRMA_LAVOZIMLAR = {
    "Hisor Mebel": ["Sotuvchi", "Yuklovchi","Haydovchi"],
        "Rayhonda Mazza (Fast food)": ["Kassir","Ish boshqaruvchi"],
        "Rayhon Bog`": ["Ish boshqaruvchi"],
}

VAZIFALAR = {
    "Sotuvchi": (
        "📋 *Sotuvchi vazifalar:*\n\n"
        "• Mijozlarga mahsulot taqdim etish\n"
        "• Kunlik sotuv rejasini bajarish\n"
        "• Kassa va hisob-kitob yuritish\n"
        "• Do'kon tartibini saqlash\n"
        "• Hisobot topshirish\n\n"
        "Shu vazifalarga tayyormisiz?"
    ),
    "Yuklovchi": (
        "📋 *Yuklovchi vazifalar:*\n\n"
        "• Tovarlarni yuklash va tushirish\n"
        "• Omborni tartibda saqlash\n"
        "• Mahsulotlarni saralash\n"
        "• Smenada jismoniy ish bajarish\n\n"
        "Shu vazifalarga tayyormisiz?"
    ),
    "Kassir": (
        "📋 *Kassir vazifalar:*\n\n"
        "• Kassa apparati bilan ishlash\n"
        "• Pul qabul qilish va qaytarish\n"
        "• Kunlik kassa hisobotini yuritish\n"
        "• Mijozlarga xizmat ko'rsatish\n"
        "• Naqd va plastik to'lovlar bilan ishlash\n\n"
        "Shu vazifalarga tayyormisiz?"
    ),
    "Ish boshqaruvchi": (
        "📋 *Ish boshqaruvchi vazifalar:*\n\n"
        "• Xodimlar ishini nazorat qilish\n"
        "• Kunlik vazifalarni taqsimlash\n"
        "• Hisobotlarni tayyorlash\n"
        "• Muammolarni hal qilish\n"
        "• Rahbariyat bilan aloqa\n\n"
        "Shu vazifalarga tayyormisiz?"
    ),
    "Haydovchi": (
        "📋 *Haydovchi vazifalar:*\n\n"
        "• Yuk tashish va yetkazib berish\n"
        "• Avtomobilni tartibda saqlash\n"
        "• Yo'l qoidalariga rioya qilish\n"
        "• Hujjatlar bilan ishlash\n"
        "• Belgilangan marshrutda ishlash\n\n"
        "Shu vazifalarga tayyormisiz?"
    ),
    "Usta": (
        "📋 *Usta vazifalar:*\n\n"
        "• Texnik ishlarni bajarish\n"
        "• Uskunalarni ta'mirlash\n"
        "• Sifat nazoratini amalga oshirish\n"
        "• Yangi xodimlarni o'qitish\n"
        "• Materiallar hisobini yuritish\n\n"
        "Shu vazifalarga tayyormisiz?"
    ),
}

FIRMALAR = list(FIRMA_LAVOZIMLAR.keys())

logging.basicConfig(level=logging.INFO)


class Anketa(StatesGroup):
    firma = State()
    lavozim = State()
    vazifa_tasdiqlash = State()
    ism = State()
    yosh = State()
    telefon = State()
    manzil = State()
    tajriba = State()
    oldingi_ish = State()
    sabab = State()
    rasm = State()
    tasdiqlash = State()


def firma_keyboard():
    buttons = [[KeyboardButton(text=f)] for f in FIRMALAR]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def lavozim_keyboard(firma_nomi):
    lavozimlar = FIRMA_LAVOZIMLAR.get(firma_nomi, [])
    buttons = [[KeyboardButton(text=l)] for l in lavozimlar]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def rozman_keyboard():
    buttons = [
        [KeyboardButton(text="✅ Rozman, davom etaman")],
        [KeyboardButton(text="⬅️ Ortga")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def tasdiqlash_keyboard():
    buttons = [
        [KeyboardButton(text="✅ Tasdiqlash")],
        [KeyboardButton(text="❌ Bekor qilish")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def bosh_sahifa(message: Message, state: FSMContext):
    await state.set_state(Anketa.firma)
    await message.answer(
        "👋 Xush kelibsiz! HR Anketa Botiga!\n\nQaysi firmaga murojaat qilmoqchisiz?",
        reply_markup=firma_keyboard()
    )


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await bosh_sahifa(message, state)


@dp.message(Anketa.firma)
async def get_firma(message: Message, state: FSMContext):
    if message.text not in FIRMALAR:
        await message.answer("Iltimos, quyidagi firmalardan birini tanlang:", reply_markup=firma_keyboard())
        return
    await state.update_data(firma=message.text)
    await state.set_state(Anketa.lavozim)
    await message.answer(
        f"✅ {message.text} tanlandi!\n\nQaysi lavozimga murojaat qilmoqchisiz?",
        reply_markup=lavozim_keyboard(message.text)
    )


@dp.message(Anketa.lavozim)
async def get_lavozim(message: Message, state: FSMContext):
    data = await state.get_data()
    firma_nomi = data.get("firma")
    lavozimlar = FIRMA_LAVOZIMLAR.get(firma_nomi, [])
    if message.text not in lavozimlar:
        await message.answer("Iltimos, quyidagi lavozimlardan birini tanlang:", reply_markup=lavozim_keyboard(firma_nomi))
        return
    await state.update_data(lavozim=message.text)
    vazifa_matni = VAZIFALAR.get(message.text, "📋 Bu lavozim uchun vazifalar belgilanmagan.\n\nDavom etasizmi?")
    await state.set_state(Anketa.vazifa_tasdiqlash)
    await message.answer(vazifa_matni, parse_mode="Markdown", reply_markup=rozman_keyboard())


@dp.message(Anketa.vazifa_tasdiqlash, F.text == "✅ Rozman, davom etaman")
async def vazifa_rozman(message: Message, state: FSMContext):
    await state.set_state(Anketa.ism)
    await message.answer(
        "📝 Anketa boshlanadi!\n\n1️⃣ Ism va Familiyangizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(Anketa.vazifa_tasdiqlash, F.text == "⬅️ Ortga")
async def vazifa_ortga(message: Message, state: FSMContext):
    data = await state.get_data()
    firma_nomi = data.get("firma")
    await state.set_state(Anketa.lavozim)
    await message.answer(
        "Qaysi lavozimga murojaat qilmoqchisiz?",
        reply_markup=lavozim_keyboard(firma_nomi)
    )


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
    await state.update_data(rasm_file_id=message.photo[-1].file_id)
    d = await state.get_data()

    preview = (
        f"📋 *Anketangizni tekshiring:*\n\n"
        f"🏢 *Firma:* {d.get('firma', '-')}\n"
        f"💼 *Lavozim:* {d.get('lavozim', '-')}\n\n"
        f"👤 *Ism Familiya:* {d.get('ism', '-')}\n"
        f"🎂 *Yosh:* {d.get('yosh', '-')}\n"
        f"📞 *Telefon:* {d.get('telefon', '-')}\n"
        f"📍 *Manzil:* {d.get('manzil', '-')}\n"
        f"🗓 *Tajriba:* {d.get('tajriba', '-')} yil\n"
        f"🏭 *Oldingi ish joyi:* {d.get('oldingi_ish', '-')}\n"
        f"💬 *Murojaat sababi:* {d.get('sabab', '-')}\n\n"
        f"‼️ Ma'lumotlar to'g'rimi?"
    )

    await state.set_state(Anketa.tasdiqlash)
    await message.answer(preview, parse_mode="Markdown", reply_markup=tasdiqlash_keyboard())


@dp.message(Anketa.rasm)
async def rasm_xato(message: Message):
    await message.answer("Iltimos, rasm yuboring (faqat rasm qabul qilinadi):")


@dp.message(Anketa.tasdiqlash, F.text == "✅ Tasdiqlash")
async def tasdiqlash_handler(message: Message, state: FSMContext):
    d = await state.get_data()

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

    await bot.send_photo(
        chat_id=GROUP_ID,
        photo=d.get('rasm_file_id'),
        caption=caption,
        parse_mode="Markdown"
    )

    await message.answer(
        "✅ Anketangiz muvaffaqiyatli yuborildi!\n\nSiz bilan tez orada bog'lanamiz. Rahmat! 🙏",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
    await asyncio.sleep(2)
    await bosh_sahifa(message, state)


@dp.message(Anketa.tasdiqlash, F.text == "❌ Bekor qilish")
async def bekor_qilish(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Anketa bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(2)
    await bosh_sahifa(message, state)


async def main():
    logging.info("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
