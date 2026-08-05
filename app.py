from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/api/extract', methods=['POST'])
def extract_video():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({'success': False, 'message': 'ভিডিও URL দিন'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url')
            
            if not download_url and 'requested_formats' in info:
                download_url = info['requested_formats'][0].get('url')

            return jsonify({
                'success': True,
                'title': info.get('title', 'Video'),
                'download_url': download_url
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)