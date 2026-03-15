from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import gspread
from google.oauth2.service_account import Credentials

TOKEN = "8705179513:AAEllHJpYv8nhPDy19DQfUc0R61ekMFmK18"
SPREADSHEET_NAME = "엘베현장"
JSON_KEYFILE = "persuasive-ace-490314-k2-17e834471c1a.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_file(JSON_KEYFILE, scopes=SCOPES)
gc = gspread.authorize(credentials)


def find_site(keyword):
    sh = gc.open(SPREADSHEET_NAME)
    ws = sh.sheet1

    headers = [
        "proj",
        "현장명",
        "계약",
        "점검",
        "승강기번호",
        "기종",
        "연락처",
        "비밀번호",
        "열쇠",
        "주소",
        "특이사항"
    ]

    data = ws.get_all_values()
    rows = []

    for r in data[1:]:
        if not any(cell.strip() for cell in r):
            continue

        row = {}
        for i, h in enumerate(headers):
            row[h] = r[i].strip() if i < len(r) else ""
        rows.append(row)

    keyword = keyword.strip().lower()
    results = []

    for row in rows:
        site = str(row.get("현장명", "")).strip().lower()
        if keyword in site:
            results.append(row)

    return results


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("엘베현장봇 연결 완료\n현장명을 입력해라.")


async def search_site(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text.strip()
    results = find_site(keyword)

    if not results:
        await update.message.reply_text("검색 결과 없음")
        return

    messages = []

    for r in results[:5]:
        msg = (
            f"proj : {r.get('proj','')}\n"
            f"현장명 : {r.get('현장명','')}\n"
            f"계약 : {r.get('계약','')}\n"
            f"점검 : {r.get('점검','')}\n"
            f"승강기번호 : {r.get('승강기번호','')}\n"
            f"기종 : {r.get('기종','')}\n"
            f"연락처 : {r.get('연락처','')}\n"
            f"비밀번호 : {r.get('비밀번호','')}\n"
            f"열쇠 : {r.get('열쇠','')}\n"
            f"주소 : {r.get('주소','')}\n"
            f"특이사항 : {r.get('특이사항','')}"
        )
        messages.append(msg)

    await update.message.reply_text("\n\n-----------------\n\n".join(messages))


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_site))

print("봇 실행중...")
app.run_polling()