import os
import threading
from flask import Flask

# ========== وب‌سرور برای Render ==========
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running", 200

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ========== اجرای ربات در پس‌زمینه ==========
def run_bot():
    from main import main as bot_main
    bot_main()

if __name__ == "__main__":
    # وب‌سرور رو توی یک ترد جداگانه اجرا کن
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # ربات رو اجرا کن (این خط بلاک می‌کنه و ربات روشن می‌مونه)
    run_bot()