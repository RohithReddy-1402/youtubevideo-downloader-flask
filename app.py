from flask import Flask, render_template, request, send_file
import yt_dlp
import os
app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads/'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
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
            'outtmpl': DOWNLOAD_FOLDER + '%(title)s.%(ext)s',
            'format': 'bestaudio/best',
        }
        if download_type == 'video':
            ydl_opts['format'] = f'bestvideo[height<={resolution}]'

        elif download_type == 'audio':
            audio_quality = request.args.get('audio_quality', '192kbps')
            if download_type == 'audio':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegAudioConvertor',
                    'preferredcodec': 'mp3',
                    'preferredquality': audio_quality.replace('kbps', ''),
                }]

        else:
            return "Invalid download type.", 400

        # Download video using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            return send_file(filename, as_attachment=True, download_name=filename.split("/")[-1])

    except Exception as e:
        return f"Error: {str(e)}", 500
