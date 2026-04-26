import yt_dlp
import time
import json
import re
from datetime import datetime
from zhipuai import ZhipuAI

# ========== CONFIGURATION ==========
AI_API_KEY = "a5a921cb20464dcf80b57af9868ea910.2N9VRx9zcFjgFrBJ"

CHANNELS = [
    {"name": "Andrej Karpathy", "url": "https://www.youtube.com/@AndrejKarpathy"},
    {"name": "Nomadic Samuel", "url": "https://www.youtube.com/@NomadicSamuel"},
    {"name": "Dave Ebbelaar", "url": "https://www.youtube.com/@daveebbelaar"},
]

ai_client = ZhipuAI(api_key=AI_API_KEY)

def get_channel_videos(channel_url, max_results=2):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': max_results,
        'socket_timeout': 10,
        'ignoreerrors': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            if 'entries' in info:
                videos = []
                for entry in info['entries']:
                    if entry is None:
                        continue
                    if entry.get('title') and entry.get('id'):
                        video_id = entry.get('id')
                        if video_id and len(video_id) == 11:
                            videos.append({
                                'title': entry.get('title', 'N/A'),
                                'video_id': video_id,
                                'url': f"https://youtube.com/watch?v={video_id}",
                            })
                        if len(videos) >= max_results:
                            break
                return videos
            return []
    except Exception as e:
        print(f"   Error: {e}")
        return []

def get_transcript(video_id):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        transcript = transcript_list.find_transcript(['en'])
        fetched = transcript.fetch()
        text_parts = [item.text for item in fetched]
        return ' '.join(text_parts)[:800]
    except Exception as e:
        return None

def analyze_video(video_title, transcript, channel_name):
    relations = {
        "Andrej Karpathy": "Deep technical tutorials, builds from scratch",
        "Nomadic Samuel": "Data science and quantitative strategy",
        "Dave Ebbelaar": "AI project practice and deployment"
    }
    
    if not transcript:
        return {
            "speaker": channel_name,
            "main_topic": f"Based on title: {video_title[:50]}",
            "llm_key_points": ["No transcript available", "Analysis based on title only"],
            "relation": relations.get(channel_name, "LLM channel"),
            "has_transcript": False
        }
    
    prompt = f"""Analyze this YouTube video about LLMs/AI based on its transcript.

Title: {video_title}
Channel: {channel_name}
Transcript sample: {transcript[:800]}

Return ONLY valid JSON. Do not include any other text.
The JSON must have these keys: main_topic, key_points, channel_relation

Example:
{{"main_topic": "How to use LLMs effectively", "key_points": ["LLM basics", "Prompt engineering"], "channel_relation": "Educational tutorials"}}"""

    for attempt in range(2):
        try:
            response = ai_client.chat.completions.create(
                model="glm-4-air",
                messages=[
                    {"role": "system", "content": "You are a JSON-only API. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                timeout=30,
            )
            
            content_str = response.choices[0].message.content.strip()
            
            json_match = re.search(r'\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}', content_str, re.DOTALL)
            if json_match:
                content_str = json_match.group()
            
            result = json.loads(content_str)
            
            key_points = result.get("key_points", [])
            if isinstance(key_points, str):
                key_points = [key_points]
            if not key_points:
                key_points = ["LLM related content"]
            
            return {
                "speaker": channel_name,
                "main_topic": result.get("main_topic", "LLM content"),
                "llm_key_points": key_points[:3],
                "relation": result.get("channel_relation", relations.get(channel_name, "LLM channel")),
                "has_transcript": True
            }
            
        except json.JSONDecodeError as e:
            if attempt == 0:
                prompt = prompt + "\n\nIMPORTANT: Return ONLY the JSON object."
        except Exception as e:
            print(f"   AI attempt {attempt + 1} failed: {e}")
    
    return {
        "speaker": channel_name,
        "main_topic": f"LLM content: {video_title[:40]}",
        "llm_key_points": ["Based on transcript", "Educational AI content"],
        "relation": relations.get(channel_name, "LLM channel"),
        "has_transcript": True
    }

def generate_html(results):
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LLM YouTube Watcher - AI Powered</title>
    <meta http-equiv="refresh" content="3600">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: #f5f5f5;
            padding: 40px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px 30px;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 8px;
        }
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        .stats {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }
        .stat-item {
            background: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 14px;
            color: #333;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-weight: bold;
            color: #667eea;
            font-size: 18px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: #4a5568;
            color: white;
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
        }
        td {
            padding: 16px;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: top;
            font-size: 14px;
            line-height: 1.5;
        }
        tr:hover {
            background: #f7fafc;
        }
        .speaker {
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 6px;
        }
        .badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 500;
        }
        .badge-transcript {
            background: #48bb78;
            color: white;
        }
        .badge-title {
            background: #ed8936;
            color: white;
        }
        .video-title {
            font-weight: 500;
            color: #2d3748;
        }
        .video-title a {
            color: #3182ce;
            text-decoration: none;
        }
        .video-title a:hover {
            text-decoration: underline;
        }
        .key-point {
            margin: 6px 0;
            padding-left: 18px;
            position: relative;
        }
        .key-point:before {
            content: "▹";
            position: absolute;
            left: 0;
            color: #667eea;
        }
        .footer {
            background: #f8f9fa;
            padding: 15px 30px;
            text-align: center;
            color: #718096;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
        }
        @media (max-width: 768px) {
            body { padding: 20px; }
            th, td { padding: 10px; }
            .key-point { font-size: 12px; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🤖 LLM YouTube Watcher</h1>
        <p>AI-powered analysis of LLM content from top YouTube channels</p>
    </div>
    <div class="stats">
        <div class="stat-item"><span class="stat-number">""" + str(len(results)) + """</span> videos analyzed</div>
        <div class="stat-item"><span class="stat-number">""" + str(sum(1 for r in results if r['has_transcript'])) + """</span> with transcripts</div>
        <div class="stat-item"><span class="stat-number">""" + str(len(CHANNELS)) + """</span> channels monitored</div>
        <div class="stat-item">🤖 AI: Zhipu GLM-4-Air</div>
    </div>
    <table>
        <thead>
            <tr>
                <th style="width: 15%">Speaker</th>
                <th style="width: 30%">Video</th>
                <th style="width: 20%">Main Topic</th>
                <th style="width: 25%">Key LLM Points</th>
                <th style="width: 10%">Channel Relation</th>
            </tr>
        </thead>
        <tbody>"""
    
    for r in results:
        badge = '<span class="badge badge-transcript"> Transcript</span>' if r['has_transcript'] else '<span class="badge badge-title"> Title-based</span>'
        points_html = ""
        for p in r['llm_key_points'][:3]:
            points_html += f'<div class="key-point">{p}</div>'
        
        html += f"""
            <tr>
                <td>
                    <div class="speaker">{r['speaker']}</div>
                    {badge}
                </td>
                <td>
                    <div class="video-title"><a href="{r['url']}" target="_blank">{r['title'][:100]}</a></div>
                </td>
                <td>{r['main_topic']}</td>
                <td>{points_html}</td>
                <td>{r['relation']}</td>
            </tr>"""
    
    html += f"""
        </tbody>
    </table>
    <div class="footer">
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC | Auto-refresh: every 6 hours via GitHub Actions</p>
        <p>Data source: YouTube Transcript API | AI analysis: Zhipu GLM-4-Air</p>
    </div>
</div>
</body>
</html>"""
    return html

def main():
    print("=" * 60)
    print("LLM YouTube Watcher - AI Powered")
    print("=" * 60)
    
    all_results = []
    
    for channel in CHANNELS:
        print(f"\n📺 Processing: {channel['name']}")
        videos = get_channel_videos(channel['url'], max_results=2)
        print(f"   Found {len(videos)} videos")
        
        for video in videos:
            print(f"   🎬 Analyzing: {video['title'][:50]}...")
            
            transcript = get_transcript(video['video_id'])
            if transcript:
                print(f"      ✅ Transcript ({len(transcript)} chars)")
            else:
                print(f"      ⚠️ No transcript")
            
            analysis = analyze_video(video['title'], transcript, channel['name'])
            
            all_results.append({
                "speaker": analysis['speaker'],
                "title": video['title'],
                "url": video['url'],
                "main_topic": analysis['main_topic'],
                "llm_key_points": analysis['llm_key_points'],
                "relation": analysis['relation'],
                "has_transcript": analysis['has_transcript']
            })
            
            time.sleep(1)
    
    html_content = generate_html(all_results)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    transcript_count = sum(1 for r in all_results if r['has_transcript'])
    print("\n" + "=" * 60)
    print(f"✅ Done! {len(all_results)} videos analyzed")
    print(f"   📝 With transcripts: {transcript_count}")
    print(f"   📄 Dashboard: index.html")
    print("=" * 60)

if __name__ == "__main__":
    main()
