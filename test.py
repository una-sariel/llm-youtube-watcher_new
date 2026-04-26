from youtube_transcript_api import YouTubeTranscriptApi

def test_transcript(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        print(f"可用字幕: {[t.language_code for t in transcript_list]}")
        
        transcript = transcript_list.find_transcript(['en'])
        fetched = transcript.fetch()
        
        text_parts = []
        for item in fetched:
            text_parts.append(item.text)
        
        text = ' '.join(text_parts)
        print(f"成功！字幕长度: {len(text)}")
        print(f"预览: {text[:200]}...")
        return True
    except Exception as e:
        print(f"失败: {e}")
        return False

print("测试视频: Let's build GPT")
test_transcript("kCc8FmEb1nY")
