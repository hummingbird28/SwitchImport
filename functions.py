import subprocess
import os, sys
from secrets import token_hex


def humanbytes(size):
    if not size:
        return "0 B"
    for unit in ["", "K", "M", "G", "T"]:
        if size < 1024:
            break
        size /= 1024
    if isinstance(size, int):
        size = f"{size}{unit}B"
    elif isinstance(size, float):
        size = f"{size:.2f}{unit}B"
    return size


def get_progress_bar(pct):
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = "■" * cFull
    p_str += "□" * (12 - cFull)
    return f"[{p_str}]"


def parseText(text):
    text = (text or "").replace("**", "*")
    if text:
        start = 0
        isSecond = False
        while "__" in text:
            start = text.find("__")
            if isSecond:
                text = text[:start] + "</i>" + text[start + 2 :]
            else:
                text = text[:start] + "<i>" + text[start + 2 :]
            isSecond = not isSecond
    return text


def generateThumbnail(file):
    if not file:
        return None
    if file.lower().endswith((".jpg", ".png", ".jpeg")):
        return file
    elif file.lower().endswith((".mkv", ".mp4")):
        name = token_hex(8) + ".png"
        proc = subprocess.run(
            ["ffmpeg", "-i", file, "-ss", "00:00:01.000", "-vframes", "1", name],
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        if os.path.exists(name):
            return name
        return 


# async def sendFile(
#     client: BotApp,
#     community_id=None,
#     channel_id=None,
#     group_id=None,
#     user_id=None,
#     message="",
#     document="",
#     caption=None,
#     description=None,
#     callback_message: Message = None,
# ):
#     chat_id = channel_id or group_id or user_id
#     TASKS[chat_id]["uploading"] = True

#     async def upload(progress: UploadProgress):
#         try:
#             TASKS[chat_id][document]["process"] = "Uploading"
#             TASKS[chat_id][document]["readed"] = progress.readed
#             TASKS[chat_id][document]["total"] = progress.total
#         except KeyError as er:
#             print(er)

#     try:
#         task = await client.send_message(
#             message=message.replace("**", " * ").replace("__", " __ "),
#             document=document,
#             caption=caption[:64] if caption else "caption",
#             description=description[:64] if description else "description",
#             thumb=generateThumbnail(document),
#             user_id=user_id,
#             community_id=community_id,
#             channel_id=channel_id,
#             group_id=group_id,
#             progress=upload,
#             task_count=30,
#             part_size=20*1024*1024
# #            blocking=False,
#         )
#     except Exception as er:
#         LOG.exception(er)
#         try:
#             del TASKS[chat_id][document]
#         except KeyError:
#             pass
#         try:
#             os.remove(document)
#         except Exception:
#             pass
#         return

#     def done():
#         #        LOG.info(_.exception())
#         try:
#             del TASKS[chat_id][document]

#             del TASKS[chat_id]["uploading"]
#         except KeyError:
#             pass
#         if chat_id in TASKS and not TASKS[chat_id]:
#             del TASKS[chat_id]
#         if document:
#             os.remove(document)

#     done()