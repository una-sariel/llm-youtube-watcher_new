import yt_dlp
import time
import json
import re
from datetime import datetime
from zhipuai import ZhipuAI

AI_API_KEY = "a5a921cb20464dcf80b57af9868ea910.2N9VRx9zcFjgFrBJ"

CHANNELS = [
    {"name": "Andrej Karpathy", "url": "https://www.youtube.com/@AndrejKarpathy"},
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
    html = '<!DOCTYPE html>\n'
    html += '<html>\n'
    html += '<head>\n'
    html += '<meta charset="utf-8">\n'
    html += '<title>LLM YouTube Watcher</title>\n'
    html += '<meta http-equiv="refresh" content="3600">\n'
    html += '<style>\n'
    html += 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; margin: 40px; background: #f0f0f0; }\n'
    html += 'h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }\n'
    html += '.timestamp { color: #666; font-size: 14px; margin-bottom: 20px; }\n'
    html += 'table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }\n'
    html += 'th { background: #4CAF50; color: white; padding: 12px; text-align: left; }\n'
    html += 'td { padding: 12px; border-bottom: 1px solid #ddd; vertical-align: top; }\n'
    html += 'tr:hover { background: #f5f5f5; }\n'
    html += '.video-title a { color: #2196F3; text-decoration: none; font-weight: bold; }\n'
    html += '.video-title a:hover { text-decoration: underline; }\n'
    html += '.key-point { margin: 4px 0; padding-left: 16px; position: relative; }\n'
    html += '.key-point:before { content: "•"; position: absolute; left: 0; color: #4CAF50; }\n'
    html += '.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-left: 8px; }\n'
    html += '.badge-transcript { background: #4CAF50; color: white; }\n'
    html += '.footer { margin-top: 20px; text-align: center; color: #666; font-size: 12px; }\n'
    html += '</style>\n'
    html += '</head>\n'
    html += '<body>\n'
    html += '<h1> LLM YouTube Watcher</h1>\n'
    html += '<div class="timestamp">Last updated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | Auto-refresh: hourly</div>\n'
    html += '<table>\n'
    html += '<thead>\n'
    html += '<tr><th style="width:15%">Speaker</th><th style="width:30%">Video</th><th style="width:20%">Main Topic</th><th style="width:25%">Key LLM Points</th><th style="width:10%">Channel Relation</th></tr>\n'
    html += '</thead>\n'
    html += '<tbody>\n'
    
    for r in results:
        points_html = ""
        for p in r['llm_key_points'][:3]:
            points_html += f'<div class="key-point">{p}</div>'
        badge = '<span class="badge badge-transcript">Transcript</span>' if r['has_transcript'] else ''
        html += '<tr>'
        html += f'<td><strong>{r["speaker"]}</strong>{badge}</td>'
        html += f'<td><div class="video-title"><a href="{r["url"]}" target="_blank">{r["title"][:100]}</a></div></td>'
        html += f'<td>{r["main_topic"]}</td>'
        html += f'<td>{points_html}</td>'
        html += f'<td>{r["relation"]}</td>'
        html += '</tr>\n'
    
    transcript_count = sum(1 for r in results if r['has_transcript'])
    html += '</tbody>\n'
    html += '</table>\n'
    html += '<div class="footer">'
    html += f'<p>{len(results)} videos analyzed | {transcript_count} with transcripts | Auto-refresh: every 6 hours</p>'
    html += '<p>Data: YouTube Transcript API | AI: Zhipu GLM-4-Air | Channels: Andrej Karpathy, Dave Ebbelaar</p>'
    html += '</div>\n'
    html += '</body>\n'
    html += '</html>\n'
    
    return html

def main():
    print("=" * 60)
    print("LLM YouTube Watcher - AI Powered")
    print("=" * 60)
    
    all_results = []
    
    for channel in CHANNELS:
        print(f"\n Processing: {channel['name']}")
        videos = get_channel_videos(channel['url'], max_results=2)
        print(f"   Found {len(videos)} videos")
        
        for video in videos:
            print(f"   Analyzing: {video['title'][:50]}...")
            
            transcript = get_transcript(video['video_id'])
            if transcript:
                print(f"      Transcript obtained ({len(transcript)} chars)")
            else:
                print(f"      No transcript")
            
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
    print(f" Done! {len(all_results)} videos analyzed")
    print(f"   With transcripts: {transcript_count}")
    print(f"   Dashboard: index.html")
    print("=" * 60)

if __name__ == "__main__":
    main()
