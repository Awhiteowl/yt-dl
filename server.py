from flask import Flask, request, jsonify
import yt_dlp
import os
import requests

app = Flask(__name__)

# اطلاعات بات تلگرام
BOT_TOKEN = "7302488189:AAHQ8U6-KhChTwBf8_szHXzFq3k-C36iZy0"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"

@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    video_url = data.get("url")
    chat_id = data.get("chat_id")  # چت آی‌دی را از ورکر می‌گیریم

    if not video_url or not chat_id:
        return jsonify({"error": "No URL or chat_id provided"}), 400

    # تنظیمات yt-dlp
    ydl_opts = {
        "format": "best",
        "outtmpl": "video.mp4"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # بررسی اینکه فایل دانلود شده وجود دارد
        if not os.path.exists("video.mp4"):
            return jsonify({"error": "Download failed"}), 500

        # ارسال فایل به تلگرام
        with open("video.mp4", "rb") as video_file:
            files = {"video": video_file}
            data = {"chat_id": chat_id}
            response = requests.post(TELEGRAM_API_URL, data=data, files=files)

        # بررسی موفقیت‌آمیز بودن ارسال
        if response.status_code == 200:
            return jsonify({"message": "Video sent to Telegram!", "status": "success"}), 200
        else:
            return jsonify({"error": "Failed to send video to Telegram"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
