import os
import django
import sys

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from asgiref.sync import sync_to_async  # ✅ Needed to call Django ORM inside async

# === Step 1: Set up Django environment ===
sys.path.append('/Users/khushalpatil/TelegramBot/DataBase')  # ✅ Path to project folder with manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DataBase.settings')  # ✅ settings.py inside inner DataBase folder
django.setup()

# === Step 2: Import your models ===
from medical.models import Patient

# === Step 3: Set your Telegram Bot Token ===
BOT_TOKEN = '8114778657:AAFmII2JSKYhME1KOAc9QEzq9T9pUdqdITg'  # 🔒 Replace with your real token (keep it private)

# === Step 4: Create sync-to-async wrapper for DB query ===
@sync_to_async
def fetch_patient_report(email):
    patients = Patient.objects.filter(email=email)
    if not patients.exists():
        return None

    response = ""
    for p in patients:
        response += (
            f"👤 Patient: {p.first_name} {p.last_name}\n"
            f"🧑‍⚕️ Doctor: {p.doctor.first_name} {p.doctor.last_name}\n"
            f"📞 Contact: {p.contact_number}\n"
            f"📅 DOB: {p.date_of_birth}\n"
            f"📋 History: {p.medical_history or 'None'}\n"
            f"💊 Allergies: {p.allergies or 'None'}\n"
            f"🏠 Address: {p.address}\n\n"
        )
    return response

# === Step 5: Telegram Bot Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! Send me your email ID to get your medical report.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip().lower()
    try:
        report = await fetch_patient_report(email)  # ✅ Await the async-safe DB call
        if report:
            await update.message.reply_text(report)
        else:
            await update.message.reply_text("❌ No report found for this email.")
    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("⚠️ Something went wrong. Please try again later.")

# === Step 6: Start the bot ===
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot is running...")
app.run_polling()
