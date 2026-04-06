import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# --- SOZLAMALAR ---
BOT_TOKEN = "8658587944:AAGx_gs1LyUQ62V64zAup9CrdkXAii7LhFo"
GROUP_ID = -1003792957294

# --- FIRMALAR VA LAVOZIMLAR ---
FIRMALAR = ["Firma 1", "Firma 2", "Firma 3", "Firma 4"]
LAVOZIMLAR = ["Ish boshqaruvchi", "Sotuvchi", "Yuklovchi", "Haydovchi", "Usta"]

# --- BOSQICHLAR ---
FIRMA, LAVOZIM, ISM, YOSH, TELEFON, MANZIL, TAJRIBA, OLDINGI_ISH, SABAB, RASM = range(10)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[f] for f in FIRMALAR]
    await update.message.reply_text(
        "👋 Xush kelibsiz! HR Anketa Botiga!\n\nQaysi firmaga murojaat qilmoqchisiz?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return FIRMA


async def firma_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text not in FIRMALAR:
        keyboard = [[f] for f in FIRMALAR]
        await update.message.reply_text(
            "Iltimos, quyidagi firmalardan birini tanlang:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
        )
        return FIRMA
    context.user_data["firma"] = text
    keyboard = [[l] for l in LAVOZIMLAR]
    await update.message.reply_text(
        f"✅ {text} tanlandi!\n\nQaysi lavozimga murojaat qilmoqchisiz?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return LAVOZIM


async def lavozim_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text not in LAVOZIMLAR:
        keyboard = [[l] for l in LAVOZIMLAR]
        await update.message.reply_text(
            "Iltimos, quyidagi lavozimlardan birini tanlang:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
        )
        return LAVOZIM
    context.user_data["lavozim"] = text
    await update.message.reply_text(
        "📝 Anketa boshlanadi!\n\n1️⃣ Ism va Familiyangizni kiriting:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ISM


async def ism_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ism"] = update.message.text
    await update.message.reply_text("2️⃣ Yoshingizni kiriting:")
    return YOSH


async def yosh_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["yosh"] = update.message.text
    await update.message.reply_text("3️⃣ Telefon raqamingizni kiriting (+998XXXXXXXXX):")
    return TELEFON


async def telefon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["telefon"] = update.message.text
    await update.message.reply_text("4️⃣ Yashash manzilingizni kiriting (Shahar, tuman):")
    return MANZIL


async def manzil_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["manzil"] = update.message.text
    await update.message.reply_text("5️⃣ Ish tajribangiz necha yil?")
    return TAJRIBA


async def tajriba_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tajriba"] = update.message.text
    await update.message.reply_text("6️⃣ Oldingi ish joyingiz qayer edi?")
    return OLDINGI_ISH


async def oldingi_ish_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["oldingi_ish"] = update.message.text
    await update.message.reply_text("7️⃣ Nega aynan shu lavozimga murojaat qilmoqdasiz?")
    return SABAB


async def sabab_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sabab"] = update.message.text
    await update.message.reply_text("8️⃣ Rasmingizni yuboring (selfie yoki passport foto):")
    return RASM


async def rasm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Iltimos, rasm yuboring (faqat rasm qabul qilinadi):")
        return RASM

    photo = update.message.photo[-1]
    d = context.user_data

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

    await context.bot.send_photo(
        chat_id=GROUP_ID,
        photo=photo.file_id,
        caption=caption,
        parse_mode="Markdown",
    )

    await update.message.reply_text(
        "✅ Anketangiz muvaffaqiyatli yuborildi!\n\nSiz bilan tez orada bog'lanamiz. Rahmat! 🙏",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Anketa bekor qilindi. Qaytadan boshlash uchun /start bosing.",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, firma_handler)],
            LAVOZIM: [MessageHandler(filters.TEXT & ~filters.COMMAND, lavozim_handler)],
            ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ism_handler)],
            YOSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, yosh_handler)],
            TELEFON: [MessageHandler(filters.TEXT & ~filters.COMMAND, telefon_handler)],
            MANZIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, manzil_handler)],
            TAJRIBA: [MessageHandler(filters.TEXT & ~filters.COMMAND, tajriba_handler)],
            OLDINGI_ISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, oldingi_ish_handler)],
            SABAB: [MessageHandler(filters.TEXT & ~filters.COMMAND, sabab_handler)],
            RASM: [
                MessageHandler(filters.PHOTO, rasm_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, rasm_handler),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    logger.info("Bot ishga tushdi...")
    await app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    asyncio.run(main())
