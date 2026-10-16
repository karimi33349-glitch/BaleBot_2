import os
import time
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def run_bot():
    while True:
        try:
            from main import main as bot_main
            bot_main()
        except Exception as e:
            print(f"❌ ربات کرش کرد: {e}")
            print("⏳ ۱۰ ثانیه صبر و تلاش مجدد...")
            time.sleep(10)

if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    run_bot()