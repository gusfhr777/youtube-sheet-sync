import os
import json

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# ======================
# ENV
# ======================
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
PLAYLIST_ID = os.getenv("PLAYLIST_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

SERVICE_FILE = "credentials/service_account.json"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# ======================
# JSON
# ======================


with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

SOURCE_SHEET = CONFIG["SOURCE_SHEET"]
TARGET_EN = CONFIG["TARGET_EN"]
TARGET_JP = CONFIG["TARGET_JP"]

LANG_MAP = CONFIG["LANG_MAP"]
TYPE_MAP = CONFIG["TYPE_MAP"]





credentials = Credentials.from_service_account_file(
    SERVICE_FILE,
    scopes=SCOPES
)

service = build("sheets", "v4", credentials=credentials)

def read_source():
    response = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SOURCE_SHEET}!A1:I"
    ).execute()

    return response.get("values", [])


def translate_rows(rows, lang):
    translated = []

    for i, row in enumerate(rows):
        if i == 0:
            continue

        if not row:
            continue

        row = row + [""] * (9 - len(row))

        # language = LANG_MAP.get(row[3], {}).get(lang, row[3]).split(',')
        languages = split_multi(row[3])
        types = split_multi(row[4])

        translated_types = [
            TYPE_MAP.get(t, {}).get(lang, t) for t in types
        ]

        translated_languages = [
            LANG_MAP.get(t, {}).get(lang, t) for t in languages
        ]
        # breakpoint()

        translated.append([
            row[0],                 # 제목 그대로
            row[1],                 # 제작자 그대로
            row[2],                 # 링크 그대로
            ",".join(translated_languages),
            ",".join(translated_types),
            row[5],
            row[6],
            row[7],
            row[8]
        ])

    # breakpoint()
    return translated

def get_existing_rows(sheet_name):
    res = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A2:I"
    ).execute()

    values = res.get("values", [])
    existing = {}

    for idx, row in enumerate(values, start=2):
        if len(row) < 3:
            continue

        # 길이 보정 (A~I 9칸)
        row = row + [""] * (9 - len(row))

        url = row[2]

        existing[url] = {
            "row_number": idx,
            "row_data": row[:9]
        }

    return existing

def write_target(sheet_name, rows):
    existing = get_existing_rows(sheet_name)

    new_rows = []
    row_updates = []

    for row in rows[1:]:  # 헤더 제외
        # 길이 보정
        row = row + [""] * (9 - len(row))
        url = row[2]

        if url in existing:
            old_row = existing[url]["row_data"]

            # 문자열 비교 통일
            new_row_normalized = [str(v) for v in row[:9]]
            old_row_normalized = [str(v) for v in old_row[:9]]

            if new_row_normalized != old_row_normalized:
                row_number = existing[url]["row_number"]

                row_updates.append({
                    "range": f"{sheet_name}!A{row_number}:I{row_number}",
                    "values": [row[:9]]
                })
        else:
            new_rows.append(row[:9])

    # 신규 행 추가
    if new_rows:
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A1:I1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": new_rows}
        ).execute()

    # 변경된 행 전체 업데이트
    if row_updates:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": row_updates
            }
        ).execute()


def split_multi(value: str):
    if not value:
        return []

    # Google Sheets 복수 선택 기본 구분자
    if "," in value:
        return [v.strip() for v in value.split(",")]

    # 혹시 모를 공백 구분 fallback
    return [v.strip() for v in value.split()]


def main():
    source_data = read_source()

    en_data = translate_rows(source_data, "en")
    jp_data = translate_rows(source_data, "jp")

    write_target(TARGET_EN, en_data)
    write_target(TARGET_JP, jp_data)



if __name__ == "__main__":
    main()