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
    audio_quality = request.args.get('audio_quality', '192kbps')  

    if not video_url or not download_type:
        return "Error: Missing URL or download type", 400

    try:
        if "youtube.com/shorts" in video_url:
            video_url = video_url.replace("https://youtube.com/shorts/", "https://youtube.com/watch?v=")
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        }

        if download_type == 'video':
            if resolution:
                ydl_opts['format'] = f'bestvideo[height<={resolution}]'
            else:
                ydl_opts['format'] = 'bestvideo'

        elif download_type == 'audio':
            ydl_opts['format'] = 'bestaudio/best' 
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegAudioConvertor',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality.replace('kbps', ''),
            }]
        else:
            return "Invalid download type.", 400
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            return send_file(filename, as_attachment=True, download_name=os.path.basename(filename))

    except yt_dlp.DownloadError as e:
        print(f"YT-DLP Download Error: {str(e)}") 
        return f"Download Error: {str(e)}", 500
    except Exception as e:
        print(f"General Error: {str(e)}") 
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  
    app.run(host='0.0.0.0', port=port, debug=True)
