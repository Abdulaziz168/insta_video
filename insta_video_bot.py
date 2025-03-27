import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from yt_dlp import YoutubeDL

# === /start komandasi ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Video havolasini yuboring (TikTok, Instagram, YouTube yoki boshqalar).")

# === Havola kelganda ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = update.message.text
    user_id = update.message.from_user.id
    message_id = update.message.message_id
    filename = f"{user_id}_video.mp4"

    # ⏬ Yuklanmoqda xabari (keyin o‘chiramiz)
    loading_msg = await update.message.reply_text("⏬ Video yuklanmoqda, iltimos kuting...")

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': filename,
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_size = os.path.getsize(filename)

        # Yuklanganidan keyin "yuklanmoqda" xabarini o‘chirish
        await loading_msg.delete()

        if file_size < 50 * 1024 * 1024:
            with open(filename, 'rb') as f:
                await update.message.reply_document(f)
            await update.message.reply_text("✅ Tayyor!")

            # Asl havolani ham o‘chiramiz
            try:
                await update.message.delete()
            except Exception as del_err:
                print(f"Xabarni o‘chirishda xatolik: {del_err}")
        else:
            await update.message.reply_text("⚠️ Kechirasiz, bu video 50MB hajmdan katta.")

        os.remove(filename)

    except Exception as e:
        # Xatolik yuz bersa ham yuklanmoqda xabarini o‘chirish
        try:
            await loading_msg.delete()
        except:
            pass

        await update.message.reply_text(f"❌ Yuklab olishda xatolik:\n`{str(e)}`", parse_mode="Markdown")

# === Botni ishga tushirish ===
def main():
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
