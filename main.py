import logging
import os
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler, PreCheckoutQueryHandler
import warnings
from telegram.warnings import PTBUserWarning

# ========== تنظیمات اولیه ==========
warnings.filterwarnings("ignore", message=r".*CallbackQueryHandler.*", category=PTBUserWarning)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ========== توکن‌ها ==========
import os
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PROVIDER_TOKEN = "WALLET-TEST-1111111111111111"  # 👈 توکن درگاه پرداخت خود را اینجا وارد کنید
ADMIN_ID = 1972739248  # 👈 آیدی ادمین

# ========== مرحله‌بندی مکالمه ==========
STEP1_NAME, STEP2_MODEL, STEP3_HEIGHT, STEP4_COLOR, STEP5_DELIVERY, STEP6_PHONE, STEP7_NUMBER, STEP8_DESC, STEP9_NEW_ORDER = range(1, 10)

# ========== دیکشنری سراسری برای ذخیره سفارشات ==========
user_orders = {}
# ========== مسیر عکس‌ها ==========
PHOTOS_PATH = {
    'ساده ایرانی': {
        'price': 1500000,
        'path': os.path.join('images', 'ساده_ایرانی.jpg')
    },
    'عربی(جده)': {
        'price': 3000000,
        'path': os.path.join('images', 'جده.jpg')
    },
    'بحرینی': {
        'price': 3000000,
        'path': os.path.join('images', 'بحرینی.jpg')
    },
    'میزبان': {
        'price': 2500000,
        'path': os.path.join('images', 'میزبان.jpg')
    },
    'حسنا ساده': {
        'price': 2500000,
        'path': os.path.join('images', 'حسنا_ساده.jpg')
    },
    'حسنا دراپه': {
        'price': 3000000,
        'path': os.path.join('images', 'حسنا_دراپه.jpg')
    },
    'قجری': {
        'price': 2500000,
        'path': os.path.join('images', 'قجری.jpg')
    },
    'شریفه': {
        'price': 3500000,
        'path': os.path.join('images', 'شریفه.jpg')
    },
    'یاسمین': {
        'price': 3500000,
        'path': os.path.join('images', 'یاسمین.jpg')
    },
    'چادر جشن تکلیف': {
        'price': 2500000,
        'path': os.path.join('images', 'چادر_جشن_تکلیف.jpg')
    },
    'جده آستین سندبادی': {
        'price': 3500000,
        'path': os.path.join('images', 'جده_آستین_سندبادی.jpg')
    },
    'لبنانی صدفی': {
        'price': 3000000,
        'path': os.path.join('images', 'لبنانی_صدفی.jpg')
    },
    'کارمندی دانشجویی خبرنگاری': {
        'price': 2500000,
        'path': os.path.join('images', 'کارمندی_دانشجویی_خبرنگاری.jpg')
    }
}

# ========== تابع شروع ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ID_CHAT'] = update.message.from_user.id
    await update.message.reply_text("سلام👋\nمن بازوی چادر دوزی ام البنین سلام الله علیها هستم")
    await update.message.reply_text("📌برای ثبت سفارش چادر\nابتدا نام و نام خانوادگی خود را وارد نمایید.")
    return STEP1_NAME

# ========== مرحله 1: دریافت نام ==========
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['FULLNAME'] = update.message.text
    await update.message.reply_text(f"✅ نام {context.user_data['FULLNAME']} ثبت شد.\n\n⏳لطفاً کمی صبر کنید...\n یکی از مدل‌های زیر را انتخاب کنید:")

    count = 0
    total = len(PHOTOS_PATH.items())
    status_msg = await update.message.reply_text(f"🔄 در حال بارگذاری {total} مدل...")

    for idx, (model_name, model_info) in enumerate(PHOTOS_PATH.items(), 1):
        price = model_info['price']
        photo_path = model_info['path']

        # نمایش قیمت به تومان (برای زیباتر شدن)
        price_toman = price // 10  # تبدیل ریال به تومان
        keyboard = [[InlineKeyboardButton(f"✅ {model_name}\n💰 {price_toman:,} تومان", callback_data=model_name)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await status_msg.edit_text(f"🔄 در حال بارگذاری مدل‌ها... ({idx}/{total})\n⏳ مدل: {model_name}")

        if os.path.exists(photo_path):
            try:
                with open(photo_path, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=f"📌 {model_name}\n💰 قیمت: {price_toman:,} تومان",
                        reply_markup=reply_markup
                    )
                count += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"خطا در ارسال عکس {model_name}: {e}")
                await update.message.reply_text(
                    f"📌 {model_name}\n💰 قیمت: {price_toman:,} تومان\n(مشکل در نمایش عکس)",
                    reply_markup=reply_markup
                )
        else:
            await update.message.reply_text(
                f"📌 {model_name}\n💰 قیمت: {price_toman:,} تومان\n(عکس موجود نیست)",
                reply_markup=reply_markup
            )
    await status_msg.delete()
    await update.message.reply_text(f"✅ {count} مدل با موفقیت نمایش داده شد.")
    return STEP2_MODEL

# ========== مرحله 2: دریافت مدل ==========
async def get_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['MODEL'] = query.data

    photo_path = PHOTOS_PATH[query.data]['path']
    if photo_path and os.path.exists(photo_path):
        try:
            with open(photo_path, 'rb') as photo:
                await query.message.reply_photo(photo=photo, caption=f"✅ مدل {query.data} انتخاب شد.")
        except:
            await query.message.reply_text(f"✅ مدل {query.data} انتخاب شد.")
    else:
        await query.message.reply_text(f"✅ مدل {query.data} انتخاب شد.")

    await query.message.reply_text("قد مورد نظر خود را به سانتی متر وارد کنید:\n(مثال: 165)")
    return STEP3_HEIGHT

# ========== مرحله 3: دریافت قد ==========
async def get_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید!")
        return STEP3_HEIGHT
    context.user_data['HEIGHT'] = update.message.text

    keyboard = [[InlineKeyboardButton('رنگی', callback_data='رنگی')], [InlineKeyboardButton('مشکی', callback_data='مشکی')]]
    await update.message.reply_text("📌 نوع پارچه را انتخاب نمایید:", reply_markup=InlineKeyboardMarkup(keyboard))
    return STEP4_COLOR

# ========== مرحله 4: دریافت رنگ ==========
async def get_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['COLOR'] = query.data

    keyboard = [[InlineKeyboardButton('حضوری', callback_data='حضوری')], [InlineKeyboardButton('ارسال با پیک', callback_data='ارسال با پیک')]]
    await query.message.reply_text("🧵چطور پارچه را به خیاط تحویل می‌دهید؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return STEP5_DELIVERY

# ========== مرحله 5: دریافت روش تحویل ==========
async def get_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['DELIVERY'] = query.data
    await query.message.reply_text("📞 لطفا شماره تلفن خود را وارد کنید:")
    return STEP6_PHONE

# ========== مرحله 6: دریافت تلفن ==========
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['PHONE_NUMBER'] = update.message.text
    await update.message.reply_text("🔢 چند تا چادر از این نوع می‌خواهید؟")
    return STEP7_NUMBER

# ========== مرحله 7: دریافت تعداد ==========
async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید!")
        return STEP7_NUMBER
    context.user_data['NUMBER'] = update.message.text
    await update.message.reply_text("📝 توضیحات خود را برای خیاط بنویسید:")
    return STEP8_DESC

# ========== ارسال نوتیفیکیشن به ادمین ==========
async def send_notification_to_admin(application, order_text: str, user_id: int):
    """ارسال نوتیفیکیشن به ادمین هنگام ثبت سفارش جدید"""

    # دیگر شرط ادمین را نداریم - برای همه کاربران (حتی ادمین) پیام می‌فرستیم
    keyboard = [
        [InlineKeyboardButton("✅ سفارش آماده شد", callback_data=f"order_ready_{user_id}")],
        [InlineKeyboardButton("💬 چت با مشتری", callback_data=f"chat_{user_id}",url=f'https://web.bale.ai/chat?uid={user_id}')]
    ]

    try:
        await application.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📦 **درخواست جدید از کاربر {user_id}:**\n\n{order_text}",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        print(f"✅ نوتیفیکیشن به ادمین ارسال شد برای کاربر {user_id}")
    except Exception as e:
        print(f"❌ خطا در ارسال نوتیفیکیشن: {e}")

# ========== مرحله 8: دریافت توضیحات و پایان ==========
async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['DESCRIPTION'] = update.message.text

    user_id = update.message.from_user.id

    # دریافت قیمت هر عدد از دیکشنری
    model_name = context.user_data.get('MODEL', 'ساده ایرانی')
    price_per_item = PHOTOS_PATH.get(model_name, {}).get('price', 250000)
    count = int(context.user_data.get('NUMBER', '1'))
    total_price = price_per_item * count

    # ذخیره در دیکشنری سراسری (برای همه کاربران حتی ادمین)
    user_orders[user_id] = {
        'name': context.user_data.get('FULLNAME', '-'),
        'model': model_name,
        'height': context.user_data.get('HEIGHT', '-'),
        'color': context.user_data.get('COLOR', '-'),
        'delivery': context.user_data.get('DELIVERY', '-'),
        'phone': context.user_data.get('PHONE_NUMBER', '-'),
        'number': str(count),
        'description': context.user_data.get('DESCRIPTION', '-'),
        'price': price_per_item,
        'total_price': total_price
    }

    # خلاصه سفارش برای کاربر
    order_text = f"""
📋 خلاصه سفارش شما:

👤 نام: {user_orders[user_id]['name']}
📌 مدل: {user_orders[user_id]['model']}
📏 قد: {user_orders[user_id]['height']} سانتی متر
🎨 پارچه: {user_orders[user_id]['color']}
🚚 تحویل: {user_orders[user_id]['delivery']}
📞 تلفن: {user_orders[user_id]['phone']}
🔢 تعداد: {user_orders[user_id]['number']} عدد
💰 قیمت هر عدد: {price_per_item:,} ریال
💰 قیمت کل: {total_price:,} ریال
📝 توضیحات: {user_orders[user_id]['description']}

✅ سفارش شما با موفقیت ثبت شد!
"""
    keyboard = [[InlineKeyboardButton("🔄 ثبت سفارش جدید", callback_data="again")]]
    await update.message.reply_text(order_text, reply_markup=InlineKeyboardMarkup(keyboard))

    # برای همه کاربران (حتی ادمین) نوتیفیکیشن بفرست
    await send_notification_to_admin(context.application, order_text, user_id)

    return STEP9_NEW_ORDER

# ========== مرحله 9: سفارش جدید ==========
async def new_order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "again":
        for key in ['FULLNAME', 'MODEL', 'HEIGHT', 'COLOR', 'DELIVERY', 'PHONE_NUMBER', 'NUMBER', 'DESCRIPTION']:
            context.user_data[key] = None
        await query.message.reply_text("✅ عالی! بیایید از اول شروع کنیم.\n 👤 لطفاً نام و نام خانوادگی خود را وارد نمایید:")
        return STEP1_NAME
    return ConversationHandler.END

# ========== ارسال فاکتور پرداخت ==========
async def send_payment_invoice(application, user_id: int, order_data: dict):
    """ارسال فاکتور پرداخت به کاربر با استفاده از دیتاهای ذخیره شده"""

    # دریافت اطلاعات از دیکشنری ارسال شده
    model_name = order_data.get('model', 'نامشخص')
    count = int(order_data.get('number', '1'))
    price_per_item = order_data.get('price', 250000)
    total_price = price_per_item * count

    # ارسال فاکتور
    prices = [LabeledPrice(label="هزینه چادر", amount=total_price)]

    await application.bot.send_invoice(
        chat_id=user_id,
        title="🧕 سفارش چادر",
        description=f"📌 مدل: {model_name}\n🔢 تعداد: {count} عدد\n💰 قیمت هر عدد: {price_per_item:,} ریال\n💰 مبلغ کل: {total_price:,} ریال",
        payload=f"payment_{user_id}_{int(asyncio.get_event_loop().time())}",
        provider_token=PROVIDER_TOKEN,
        currency="IRR",
        prices=prices
    )

    # ارسال پیام راهنما
    await application.bot.send_message(
        chat_id=user_id,
        text="💡 **نحوه پرداخت:**\n"
             "1️⃣ روی دکمه پرداخت کلیک کنید\n"
             "2️⃣ اطلاعات کارت را وارد کنید\n"
             "3️⃣ پس از پرداخت موفق، جهت تحویل با شماره **09212364079** تماس بگیرید .\n\n"
    )

# ========== هندلر دکمه‌های ادمین ==========
async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        await query.answer()
    except:
        return

    data = query.data

    if data.startswith("order_ready_"):
        user_id = int(data.replace("order_ready_", ""))

        # بررسی وجود کاربر در دیکشنری
        if user_id not in user_orders:
            await query.message.reply_text(f"❌ اطلاعات سفارش کاربر {user_id} یافت نشد!")
            return

        # دریافت اطلاعات سفارش
        order_data = user_orders[user_id]
        user_name = order_data.get('name', 'کاربر')
        model_name = order_data.get('model', 'نامشخص')
        count = order_data.get('number', '1')
        total_price = order_data.get('total_price', 0)

        await query.message.reply_text(
            f"💰 در حال ارسال درگاه پرداخت به  {user_name}\n"
            f"📌 مدل: {model_name}\n"
            f"🔢 تعداد: {count} عدد\n"
            f"💰 مبلغ: {total_price:,} ریال"
        )

        # ارسال فاکتور با اطلاعات واقعی
        await send_payment_invoice(context.application, user_id, order_data)

        await query.message.reply_text(f"✅ فاکتور پرداخت به  {user_name} ارسال شد.")

# ========== هندلرهای پرداخت ==========
async def pre_checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload.startswith("payment_"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="❌ خطا در اطلاعات سفارش")


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    user_id = update.message.from_user.id

    # پیام به کاربر
    await update.message.reply_text(
        f"✅ **پرداخت شما به مبلغ {payment.total_amount:,} ریال تأیید شد!**\n\n"
        f"📞 جهت هماهنگی تحویل سفارش، لطفاً با شماره **09212364079** تماس بگیرید.\n\n"
        f"🆔 شماره پیگیری: {payment.telegram_payment_charge_id}\n\n"
        f"🙏 از اعتماد شما سپاسگزاریم."
    )

    # اطلاع به ادمین
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"({user_orders[user_id]['name']})💰 **پرداخت جدید از  {user_id}**\nمبلغ: {payment.total_amount:,} ریال\nشماره پیگیری: {payment.telegram_payment_charge_id}"
    )
# ========== لغو ==========
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات لغو شد.\nبرای شروع مجدد، /start را بفرستید.")
    return ConversationHandler.END

# ========== تابع اصلی ==========
def main():
    application = Application.builder().token(TOKEN).base_url('https://tapi.bale.ai/bot').connect_timeout(60).read_timeout(60).write_timeout(60).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STEP1_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            STEP2_MODEL: [CallbackQueryHandler(get_model)],
            STEP3_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_height)],
            STEP4_COLOR: [CallbackQueryHandler(get_color)],
            STEP5_DELIVERY: [CallbackQueryHandler(get_delivery)],
            STEP6_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            STEP7_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_number)],
            STEP8_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            STEP9_NEW_ORDER: [CallbackQueryHandler(new_order_handler, pattern='^again$')],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(admin_button_handler))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_handler))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    print("🤖 ربات روشن شد...")
    application.run_polling()

if __name__ == '__main__':
    main()