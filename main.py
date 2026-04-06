import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# --- SOZLAMALAR ---
BOT_TOKEN = "8596961288:AAH3rs6FUdz7Ig-5Jjzhp2aaoVL0tZZvy_U"
GROUP_ID = -1003792957294

# --- FIRMALAR VA LAVOZIMLAR ---
FIRMALAR = ["Firma 1", "Firma 2", "Firma 3", "Firma 4"]
LAVOZIMLAR = ["Ish boshqaruvchi", "Sotuvchi", "Yuklovchi", "Haydovchi", "Usta"]

# --- BOSQICHLAR ---
(
    FIRMA,
    LAVOZIM,
    ISM,
    YOSH,
    TELEFON,
    MANZIL,
    TAJRIBA,
    OLDINGI_ISH,
    SABAB,
    RASM,
) = range(10)

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[f] for f in FIRMALAR]
    await update.message.reply_text(
        "👋 Xush kelibsiz! HR Anketa Botiga!\n\nQaysi firmaga murojaat qilmoqchisiz?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return FIRMA


async def firma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text not in FIRMALAR:
        await update.message.reply_text("Iltimos, quyidagi firmalardan birini tanlang:")
        return FIRMA
    context.user_data["firma"] = text
    keyboard = [[l] for l in LAVOZIMLAR]
    await update.message.reply_text(
        f"✅ {text} tanlandi!\n\nQaysi lavozimga murojaat qilmoqchisiz?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return LAVOZIM


async def lavozim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text not in LAVOZIMLAR:
        await update.message.reply_text("Iltimos, quyidagi lavozimlardan birini tanlang:")
        return LAVOZIM
    context.user_data["lavozim"] = text
    await update.message.reply_text(
        "📝 Anketa boshlanadi!\n\n1️⃣ Ism va Familiyangizni kiriting:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ISM


async def ism(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ism"] = update.message.text
    await update.message.reply_text("2️⃣ Yoshingizni kiriting:")
    return YOSH


async def yosh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["yosh"] = update.message.text
    await update.message.reply_text("3️⃣ Telefon raqamingizni kiriting (+998XXXXXXXXX):")
    return TELEFON


async def telefon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["telefon"] = update.message.text
    await update.message.reply_text("4️⃣ Yashash manzilingizni kiriting (Shahar, tuman):")
    return MANZIL


async def manzil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["manzil"] = update.message.text
    await update.message.reply_text("5️⃣ Ish tajribangiz necha yil?")
    return TAJRIBA


async def tajriba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tajriba"] = update.message.text
    await update.message.reply_text("6️⃣ Oldingi ish joyingiz qayer edi?")
    return OLDINGI_ISH


async def oldingi_ish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["oldingi_ish"] = update.message.text
    await update.message.reply_text("7️⃣ Nega aynan shu lavozimga murojaat qilmoqdasiz?")
    return SABAB


async def sabab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sabab"] = update.message.text
    await update.message.reply_text("8️⃣ Rasmingizni yuboring (selfie yoki passport foto):")
    return RASM


async def rasm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Iltimos, rasm yuboring:")
        return RASM

    photo = update.message.photo[-1]
    d = context.user_data

    caption = (
        f"📋 *YANGI ANKETA*\n\n"
        f"🏢 *Firma:* {d.get('firma')}\n"
        f"💼 *Lavozim:* {d.get('lavozim')}\n\n"
        f"👤 *Ism Familiya:* {d.get('ism')}\n"
        f"🎂 *Yosh:* {d.get('yosh')}\n"
        f"📞 *Telefon:* {d.get('telefon')}\n"
        f"📍 *Manzil:* {d.get('manzil')}\n"
        f"🗓 *Tajriba:* {d.get('tajriba')} yil\n"
        f"🏭 *Oldingi ish joyi:* {d.get('oldingi_ish')}\n"
        f"💬 *Murojaat sababi:* {d.get('sabab')}\n"
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


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, firma)],
            LAVOZIM: [MessageHandler(filters.TEXT & ~filters.COMMAND, lavozim)],
            ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ism)],
            YOSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, yosh)],
            TELEFON: [MessageHandler(filters.TEXT & ~filters.COMMAND, telefon)],
            MANZIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, manzil)],
            TAJRIBA: [MessageHandler(filters.TEXT & ~filters.COMMAND, tajriba)],
            OLDINGI_ISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, oldingi_ish)],
            SABAB: [MessageHandler(filters.TEXT & ~filters.COMMAND, sabab)],
            RASM: [MessageHandler(filters.PHOTO, rasm), MessageHandler(filters.TEXT & ~filters.COMMAND, rasm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
