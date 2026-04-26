# LLM YouTube Watcher

## Project Overview

LLM YouTube Watcher is an automated monitoring tool that tracks selected YouTube channels focused on Large Language Models (LLMs). It fetches latest videos, extracts transcripts, analyzes content using AI, and generates a clean HTML table for easy viewing.

## Features

- Automated YouTube channel monitoring
- Transcript extraction (auto-generated or manual captions)
- AI-powered content analysis using Zhipu GLM-4-Air
- Beautiful HTML table output
- Scheduled updates every 6 hours via GitHub Actions
- Public access via GitHub Pages

## Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.11 |
| Video Fetching | yt-dlp |
| Transcript API | youtube-transcript-api |
| AI Model | Zhipu GLM-4-Air |
| CI/CD | GitHub Actions |
| Hosting | GitHub Pages |
| Frontend | HTML5 + CSS3 |

## Monitored Channels

| Channel | Focus Area |
|---------|------------|
| Andrej Karpathy | LLM from scratch, deep technical tutorials |
| Dave Ebbelaar | AI project practice and deployment |

## Project Structure

```
llm-youtube-watcher/
├── main.py                      # Main Python script
├── index.html                   # Generated HTML dashboard
├── .github/
│   └── workflows/
│       └── update.yml           # GitHub Actions cron job
└── README.md                    # Project documentation
```

## How It Works

### 1. Video Fetching
The script uses `yt-dlp` to fetch the 2 most recent videos from each configured channel.

### 2. Transcript Extraction
`youtube-transcript-api` retrieves English transcripts (auto-generated or manual) from each video.

### 3. AI Analysis
The transcript (up to 800 characters) is sent to Zhipu GLM-4-Air with a prompt that asks for:

- Main topic of the video
- Key LLM-related points
- Channel relation to other LLM educators

### 4. HTML Generation
The analysis results are formatted into a clean, responsive HTML table with:
- Green header bar
- Transcript badge for videos with captions
- Bullet points for key insights
- Hover effects on rows

### 5. Automation
GitHub Actions runs the script every 6 hours and deploys the updated `index.html` to GitHub Pages.

## Live Demo

**https://una-sariel.github.io/llm-youtube-watcher_new/index.html**

## GitHub Repository

**https://github.com/una-sariel/llm-youtube-watcher_new**

## Sample Output

| Speaker | Video | Main Topic | Key LLM Points | Channel Relation |
|---------|-------|------------|----------------|-------------------|
| Andrej Karpathy | How I use LLMs | Practical applications of LLMs | Introduction to LLMs, LLM fundamentals, Real-world examples | Deep technical tutorials, builds from scratch |
| Dave Ebbelaar | The biggest opportunity for developers in 2026 | Future of tech jobs and AI | AI engineering, Agentic engineering, Developer skills | AI project practice and deployment |

## Results Summary

| Metric | Value |
|--------|-------|
| Channels monitored | 2 |
| Videos per run | 4 |
| Transcript success rate | ~100% |
| Update frequency | Every 6 hours |
| Page auto-refresh | Hourly |

## Limitations

- YouTube may block cloud server IPs from accessing transcripts
- Transcript quality depends on YouTube's auto-caption accuracy
- AI analysis cost is minimal (~$0.002 per video)

## Future Improvements

- Add more LLM-focused channels
- Implement RAG for better context understanding
- Add email notifications for high-value videos
- Support multi-language transcripts

## License

MIT
