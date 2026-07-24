from flask import Flask, request, render_template_string, jsonify
import urllib.request
import json
import os

app = Flask(__name__)

# সম্পূর্ণ বিজ্ঞাপন-মুক্ত চমৎকার ডার্ক থিম ইন্টারফেস
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Personal YT Downloader</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #ffffff;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .container {
            width: 100%;
            max-width: 500px;
            background-color: #1e1e1e;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            text-align: center;
            box-sizing: border-box;
        }
        h2 {
            margin-bottom: 20px;
            color: #ff0000;
        }
        p {
            font-size: 14px;
            color: #aaaaaa;
            margin-bottom: 25px;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #333;
            border-radius: 8px;
            background-color: #2c2c2c;
            color: #ffffff;
            font-size: 16px;
            margin-bottom: 20px;
            outline: none;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }
        input[type="text"]:focus {
            border-color: #ff0000;
        }
        button {
            width: 100%;
            padding: 12px;
            background-color: #ff0000;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
            box-sizing: border-box;
        }
        button:hover {
            background-color: #cc0000;
        }
        .result {
            margin-top: 25px;
            display: none;
            background-color: #282828;
            padding: 15px;
            border-radius: 8px;
            text-align: left;
        }
        .download-btn {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        }
    </style>
</head>
<body>

<div class="container">
    <h2>আমার নিজস্ব ভিডিও ডাউনলোডার</h2>
    <p>লিংক দিন এবং বিজ্ঞাপন ছাড়া সরাসরি নিজের ফোনে ডাউনলোড করুন।</p>
    
    <input type="text" id="ytUrl" placeholder="ইউটিউব ভিডিওর লিংক এখানে দিন...">
    <br>
    <button onclick="getLink()">ডাউনলোড লিংক তৈরি করুন</button>
    
    <div class="result" id="resultBox">
        <p id="videoTitle" style="font-weight: bold; color: #fff;"></p>
        <a id="downloadLink" class="download-btn" href="#" target="_blank">ডাউনলোড শুরু করুন</a>
    </div>
</div>

<script>
    async function getLink() {
        const urlInput = document.getElementById('ytUrl').value.trim();
        const resultBox = document.getElementById('resultBox');
        const videoTitle = document.getElementById('videoTitle');
        const downloadLink = document.getElementById('downloadLink');
        
        if (urlInput === "") {
            alert("দয়া করে লিংক দিন!");
            return;
        }
        
        videoTitle.innerText = "লিংক তৈরি হচ্ছে... অনুগ্রহ করে একটু অপেক্ষা করুন।";
        resultBox.style.display = "block";
        downloadLink.style.display = "none";
        
        try {
            const response = await fetch('/api/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: urlInput })
            });
            const data = await response.json();
            
            if (data.success) {
                videoTitle.innerText = data.title;
                downloadLink.href = data.download_url;
                downloadLink.style.display = "inline-block";
            } else {
                videoTitle.innerText = "ত্রুটি: " + data.error;
            }
        } catch (e) {
            videoTitle.innerText = "সার্ভারে সংযোগ করা যাচ্ছে না!";
        }
    }
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/extract', methods=['POST'])
def extract():
    try:
        data = request.get_json(silent=True) or {}
        video_url = data.get('url')
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400

    if not video_url:
        return jsonify({'success': False, 'error': 'No URL provided'}), 400

    try:
        # কোবাল্ট এপিআই-এর জন্য ডেটা প্রস্তুত করা হচ্ছে
        req_payload = json.dumps({
            'url': video_url,
            'vQuality': '720' # স্ট্যান্ডার্ড ৭২০পি কোয়ালিটি লিংক নেবে
        }).encode('utf-8')
        
        # প্রক্সি এপিআই-এর কাছে রিকোয়েস্ট পাঠানো হচ্ছে
        req = urllib.request.Request(
            'https://api.cobalt.tools/api/json',
            data=req_payload,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            
            if res_data.get('status') in ['stream', 'redirect', 'success'] and 'url' in res_data:
                title = res_data.get('text', 'ভিডিও ডাউনলোড লিংক প্রস্তুত!')
                # টাইটেলটি যদি বড় কোনো ইউআরএল হয়, তবে টেক্সট ডিফল্ট রাখা হচ্ছে
                if len(title) > 100 or 'http' in title:
                    title = 'ভিডিও ডাউনলোড লিংক প্রস্তুত!'
                return jsonify({
                    'success': True,
                    'title': title,
                    'download_url': res_data['url']
                })
            else:
                error_msg = res_data.get('text', 'ইউটিউব সিকিউরিটি বাইপাস করা যায়নি!')
                return jsonify({'success': False, 'error': error_msg})
                
    except Exception as e:
        return jsonify({'success': False, 'error': 'ইউটিউব সিকিউরিটি বাইপাস করা যাচ্ছে না, অন্য ভিডিও চেষ্টা করুন।'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
