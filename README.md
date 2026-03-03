# 유튜브 & 구글 시트 자동 동기화 시스템
<img width="2310" height="1398" alt="image" src="https://github.com/user-attachments/assets/6dd2d298-08a9-401c-9e1e-b477438a2c13" />

유튜브 재생목록을 구글 시트와 자동으로 동기화하는 시스템입니다.

게임 "트릭컬" 을 기반으로 제작하였으며, 다른 서비스에 맞게 변경이 가능합니다.

한국어, 영어, 일본어를 지원합니다.






# 시스템 구축 방법

준비물 : 컨테이너 배포 서비스 or 도커 서버

## 구글 시트 및 API 설정
https://docs.google.com/spreadsheets/d/1MU8xj6105hQ8MKa2s6wqhi8AiDzQzaio-hKfr9w6Z4A

1. 다음 링크에 접속한 다음, 파일 - 사본 만들기를 통해 시트를 복사합니다.

https://develop-davi-kr.tistory.com/entry/%ED%8C%8C%EC%9D%B4%EC%8D%AC%EC%9D%84-%EC%9D%B4%EC%9A%A9%ED%95%9C-%EA%B5%AC%EA%B8%80-%EC%8A%A4%ED%94%84%EB%A0%88%EB%93%9C%EC%8B%9C%ED%8A%B8-%EC%97%B0%EB%8F%99-%EB%B0%8F-%EC%9E%90%EB%8F%99%ED%99%94-%EB%B0%A9%EB%B2%95#%EA%B5%AC%EA%B8%80_%ED%81%B4%EB%9D%BC%EC%9A%B0%EB%93%9C_%EC%84%9C%EB%B9%84%EC%8A%A4_%EA%B0%80%EC%9E%85_%EB%B0%8F_%EC%84%9C%EB%B9%84%EC%8A%A4_%EA%B3%84%EC%A0%95_%EC%83%9D%EC%84%B1

2. 다음 글을 참고하여 구글 서비스 계정을 생성합니다. 이때 생성되는 json 파일은 credentials/service_account.json으로 저장합니다.

3. 구글콘솔의 API 및 서비스 - 라이브러리 탭에서 YouTube Data API v3, Google Sheets API를 활성화합니다.

5. 마지막으로 .env 파일을 생성하고, YOUTUBE_API_KEY, PLAYLIST_ID, SPREADSHEET_ID를 설정합니다.

유튜브 API키는 구글 콘솔 - 사용자 인증 정보 - API 키, 플레이리스트 ID는 유튜브 플레이리스트 링크, 구글 시트 ID는 맨처음 복사한 구글 시트의 링크에서 획득가능합니다.

```.env
YOUTUBE_API_KEY=<YOUTUBE_API_KEY>
PLAYLIST_ID=<PLAYLIST_ID>
SPREADSHEET_ID=<SPREADSHEET_ID>
```


## config.json 설정

5. 원하는 서비스에 맞게 config.json 값을 변경합니다. 기본값은 다음과 같습니다.
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


## 클론 및 도커 설정
6. 깃 클론 및 이동
```bash
git clone https://github.com/gusfhr777/youtube-sheet-sync.git
cd youtube-sheet-sync
```

7. `crontab -e`를 통해 crontab 설정
```bash
0 9  * * * docker run --rm youtube-sheet-sync >> /home/<user>/youtube.log 2>&1
```
