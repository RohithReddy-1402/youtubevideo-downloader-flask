from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import pickle

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads/'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

COOKIES_FILE = 'youtube_cookies.pkl'

def load_cookies(cookies_path):
    with open(cookies_path, "rb") as file:
        return pickle.load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')
    download_type = request.args.get('type')
    resolution = request.args.get('resolution')

    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'cookiesfrombrowser': ('chrome', COOKIES_FILE),
        }

        if download_type == 'video':
            ydl_opts['format'] = f'bestvideo[height<={resolution}]+bestaudio/best'
        elif download_type == 'audio':
            audio_quality = request.args.get('audio_quality', '192kbps')
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality.replace('kbps', ''),
            }]
        else:
            return jsonify({"error": "Invalid download type"}), 400

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            return send_file(filename, as_attachment=True, download_name=filename.split("/")[-1])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
