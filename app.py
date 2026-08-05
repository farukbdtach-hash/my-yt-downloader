import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/api/extract', methods=['GET'])
def extract_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL প্রয়োজন'}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail', ''),
                'url': info.get('url', '')
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['GET'])
def download_proxy():
    video_url = request.args.get('url')
    if not video_url:
        return "URL Missing", 400

    try:
        r = requests.get(video_url, stream=True)
        return Response(
            r.iter_content(chunk_size=1024 * 1024),
            content_type=r.headers.get('content-type', 'video/mp4'),
            headers={
                "Content-Disposition": "attachment; filename=video.mp4"
            }
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
