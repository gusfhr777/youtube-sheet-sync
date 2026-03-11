# Automatic Sync System using Youtube Playlist & Google Sheets 
<img width="2310" height="1398" alt="image" src="https://github.com/user-attachments/assets/6dd2d298-08a9-401c-9e1e-b477438a2c13" />


This project is based on the game "Trickcal" and can be adapted for other services with appropriate modifications.

The system supports Korean, English, and Japanese.

## System Deployment Guide

Requirements:

- A container deployment platform or a server capable of running Docker.

## Google Sheets and API Configuration

Google Sheet template:
https://docs.google.com/spreadsheets/d/1MU8xj6105hQ8MKa2s6wqhi8AiDzQzaio-hKfr9w6Z4A

1. Open the following link and create a copy of the spreadsheet **using File → Make a copy.**

2. Refer to the guide below to create a Google service account.
https://develop-davi-kr.tistory.com/entry/%ED%8C%8C%EC%9D%B4%EC%8D%AC%EC%9D%84-%EC%9D%B4%EC%9A%A9%ED%95%9C-%EA%B5%AC%EA%B8%80-%EC%8A%A4%ED%94%84%EB%A0%88%EB%93%9C%EC%8B%9C%ED%8A%B8-%EC%97%B0%EB%8F%99-%EB%B0%8F-%EC%9E%90%EB%8F%99%ED%99%94-%EB%B0%A9%EB%B2%95

3. Save the generated JSON credential file as:
`credentials/service_account.json`

4. In the Google Cloud Console, navigate to:

`APIs & Services → Library`

Enable the following APIs:

- YouTube Data API v3
- Google Sheets API

5. Create a .env file and configure the following values:

- YOUTUBE_API_KEY
- PLAYLIST_ID
- SPREADSHEET_ID

Where:
- YouTube API Key: Google Cloud Console → Credentials → API Key
- Playlist ID: Extracted from the YouTube playlist URL
- Spreadsheet ID: Extracted from the Google Sheets URL you copied earlier

```.env
YOUTUBE_API_KEY=<YOUTUBE_API_KEY>
PLAYLIST_ID=<PLAYLIST_ID>
SPREADSHEET_ID=<SPREADSHEET_ID>
config.json Configuration
```

Modify config.json according to the requirements of your service.
The default configuration is as follows:

```json
{
  "SOURCE_SHEET": "트릭컬 영상 DB",
  "TARGET_EN": "Trickal Video DB",
  "TARGET_JP": "トリックカル 動画 DB",

  "LANG_MAP": {
    "한": { "en": "ko", "jp": "韓" },
    "영": { "en": "en", "jp": "英" },
    "일": { "en": "jp", "jp": "日" },
    "중": { "en": "cn", "jp": "中" }
  },

  "TYPE_MAP": {
    "음악": { "en": "Music", "jp": "音楽" },
    "볼팝": { "en": "Bolpop", "jp": "頬ポップ" },
    "공식": { "en": "Official", "jp": "公式" },
    "성우": { "en": "Voice Actor", "jp": "声優" },
    "커버": { "en": "Cover", "jp": "カバー" },
    "합성": { "en": "Mashup", "jp": "音MAD" }
  }
}
```

## Repository Clone and Docker Setup

6. Clone the repository and move into the project directory.

```bash
git clone https://github.com/gusfhr777/youtube-sheet-sync.git
cd youtube-sheet-sync
```

7. Build the Docker image.

```bash
docker build -t youtube-sheet-sync .
```

8. Configure a scheduled job using crontab.

```bash
crontab -e
```

Example configuration:

```bash
0 9 * * * docker run --rm youtube-sheet-sync >> /home/<user>/youtube.log 2>&1
```
This runs the container every day at 09:00, logging the output to youtube.log.
