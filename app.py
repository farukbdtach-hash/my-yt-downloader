import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

@app.route('/api/extract', methods=['GET'])
def extract_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL প্রয়োজন'}), 400

    # ইউটিউবের লিংক হলে সরাসরি আটকে দিয়ে সুন্দর মেসেজ দেখাবে
    if "youtube.com" in url or "youtu.be" in url:
        return jsonify({'error': 'দুঃখিত, ইউটিউব বাদে অন্য যেকোনো সাইটের (Facebook, TikTok, Instagram ইত্যাদি) লিংক দিন।'}), 400

    # অন্য যেকোনো সাইটের জন্য সাধারণ কনফিগারেশন
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': HEADERS,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                info = info['entries'][0]

            return jsonify({
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail', ''),
                'url': info.get('url', '')
            })
    except Exception as e:
        # কোনো সমস্যা হলে তার সহজ বিবরণ দেখাবে
        return jsonify({'error': f'ভিডিও লিংক তৈরি করা যায়নি। বিস্তারিত: {str(e)}'}), 500

@app.route('/api/download', methods=['GET'])
def download_proxy():
    video_url = request.args.get('url')
    if not video_url:
        return "URL Missing", 400

    try:
        r = requests.get(video_url, stream=True, headers=HEADERS, timeout=30)
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
