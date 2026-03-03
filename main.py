import os
from datetime import datetime
import json

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import copy_sheet




# ======================
# ENV
# ======================
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
PLAYLIST_ID = os.getenv("PLAYLIST_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

SERVICE_FILE = "credentials/service_account.json"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# YouTube API
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Sheets API
credentials = Credentials.from_service_account_file(
    SERVICE_FILE,
    scopes=SCOPES
)
sheets_service = build("sheets", "v4", credentials=credentials)

# ======================
# JSON
# ======================
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

SOURCE_SHEET = CONFIG["SOURCE_SHEET"]


# ======================
# YOUTUBE
# ======================
def get_video_ids():
    video_ids = []
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=PLAYLIST_ID,
        maxResults=50
    )

    while request:
        response = request.execute()
        for item in response["items"]:
            video_ids.append(
                item["snippet"]["resourceId"]["videoId"]
            )
        request = youtube.playlistItems().list_next(request, response)

    return video_ids


def get_video_details(video_ids):
    result = {}

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]

        response = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(batch)
        ).execute()

        for item in response["items"]:
            snippet = item["snippet"]
            stats = item["statistics"]

            video_url = f"https://www.youtube.com/watch?v={item['id']}"
            published = snippet["publishedAt"]  # 2026-03-03T10:20:30Z
            dt = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")

            result[video_url] = {
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "date": f"{dt.year}. {dt.month}. {dt.day}",
                "views": int(stats.get("viewCount", 0))
            }
    return result


# ======================
# SHEET SYNC
# ======================
def get_existing_links(sheet_name):
    """
    Read Link Column and identify Existing videos.
    """
    response = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A2:I"
    ).execute()

    values = response.get("values", [])

    existing = {}
    for idx, row in enumerate(values, start=2):
        if len(row) >= 3:
            existing[row[2]] = {
                "row_number": idx,
                "views": int(row[6]) if len(row) > 6 else 0
            }

    return existing


def append_new_rows(sheet_name, rows):
    """
    tableRange set and Expand Table.
    """
    sheets_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A1:I1",  # 🔥 tableRange 기준
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": rows}
    ).execute()


def update_views(updates):
    """
    view batch update
    """
    # breakpoint()
    sheets_service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": updates
        }
    ).execute()


def sync_sheet(video_data, sheet_name=SOURCE_SHEET):
    existing = get_existing_links(sheet_name)

    new_rows = []
    view_updates = []

    # breakpoint()

    for url, data in video_data.items():

        if url in existing:
            if existing[url]["views"] != data["views"]:
                row_number = existing[url]["row_number"]
                view_updates.append({
                    "range": f"{sheet_name}!G{row_number}",
                    "values": [[data["views"]]]
                })
        else:
            new_rows.append([
                data["title"],
                data["channel"],
                url,
                "",
                "",
                data["date"],
                data["views"],
                False,
                False
            ])

    if new_rows:
        append_new_rows(sheet_name, new_rows)

    if view_updates:
        update_views(view_updates)

    print(f"New Addition : {len(new_rows)}")
    print(f"View Update: {len(view_updates)}")
    print("Sync Complete.")

def update_last_update():
    now = datetime.now()

    formatted = (
        f"Last Update : "
        f"{now.year}. {now.month}. {now.day}. "
        f"{now.strftime('%H:%M:%S')}"
    )

    sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="readme!B1",
        valueInputOption="USER_ENTERED",
        body={
            "values": [[formatted]]
        }
    ).execute()

# ======================
# MAIN
# ======================
if __name__ == "__main__":
    print("Retrieving Videos...")
    ids = get_video_ids()
    print(f"{len(ids)} Found")

    data = get_video_details(ids)

    print("Sheet Sync...")
    sync_sheet(data, sheet_name=SOURCE_SHEET)

    print("Translate & Copy Sheet...")
    copy_sheet.main()

    update_last_update()

    print("Done")