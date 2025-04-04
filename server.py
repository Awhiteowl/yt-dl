from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import threading

app = Flask(__name__)

BOT_TOKEN = "7302488189:AAHQ8U6-KhChTwBf8_szHXzFq3k-C36iZy0"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
DOWNLOAD_DIR = "downloads"

# اطمینان از اینکه پوشه دانلود وجود دارد
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    video_url = data.get("url")
    chat_id = data.get("chat_id")

    if not video_url or not chat_id:
        return jsonify({"error": "No URL or chat_id provided"}), 400

    # تنظیمات yt-dlp برای دانلود ویدیو
    ydl_opts = {
        "format": "best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get("title", "video")
            video_ext = info_dict.get("ext", "mp4")
            video_filename = f"{video_title}.{video_ext}"
            video_path = os.path.join(DOWNLOAD_DIR, video_filename)

            # ساخت لینک HTTP برای دسترسی Worker به فایل
            video_url = f"https://{request.host}/files/{video_filename}"

            return jsonify({"message": "Download successful", "file_url": video_url, "chat_id": chat_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files/<filename>", methods=["GET"])
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, threaded=True)
