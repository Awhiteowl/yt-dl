from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/download", methods=["GET"])
def download_video():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # اجرای yt-dlp و دانلود ویدیو
        cmd = [
            "yt-dlp",
            "--output", f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            url
        ]
        subprocess.run(cmd, check=True)

        # پیدا کردن فایل دانلود شده
        files = os.listdir(DOWNLOAD_DIR)
        if not files:
            return jsonify({"error": "Download failed"}), 500
        
        return jsonify({"message": "Download successful", "file": files[0]})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
