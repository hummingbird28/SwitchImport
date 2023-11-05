import logging, asyncio, random, os
from logging import FileHandler, StreamHandler

logging.basicConfig(
    level=logging.INFO,
    handlers=[FileHandler("File.log", encoding="utf-8"), StreamHandler()],
    encoding="utf-8",
)

import time
from datetime import datetime as dt
from secrets import token_hex
from FastTelethon import download_file
from config import *
from functions import get_progress_bar, humanbytes
from swibots import Message, UploadProgress
from telethon.tl.custom import Message as TMessage
from telethon.tl import types
from swibots import (
    Client as BotApp,
    BotCommand,
    BotContext,
    CommandEvent,
)
from telethon.utils import guess_extension

loop = asyncio.get_event_loop()
bots = CONFIG.BOTS

tokens = "bot_tokens.txt"
if not os.path.exists(tokens):
    LOG.info("Bot token file not found!")
    exit()

client = BotApp(BOT_TOKEN).set_bot_commands(
    [
        BotCommand("start", "Get Start message", True),
        BotCommand("copy", "Copy messages from telegram", True),
        BotCommand("cancel", "Cancel Ongoing task", True),
    ]
)


async def startBOT(token, index):
    try:
        index += 1
        if not bots.get(index):
            bots[index] = {"dc_id": index}
        bots[index]["client"] = client = TelegramClient(
            f"bot{index}", api_id=API_ID, api_hash=API_HASH, receive_updates=False
        )
        await bots[index]["client"].start(bot_token=token.strip(), phone=lambda: None)
        client.me = await bots[index]["client"].get_me()
        LOG.info("Started", client.me.username, index)
    except Exception as er:
        LOG.exception(er)


async def start_bots():
    with open(tokens, "r") as f:
        await asyncio.gather(
            *[startBOT(token, index) for index, token in enumerate(f.readlines())]
        )


# loop.create_task(start_bots())


async def getRandomClient():
    client = bots[random.randint(1, len(bots.keys()))]["client"]
    await client.start()
    return client


class Timer:
    def __init__(self, time_between=2):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False


@client.on_command("cancel")
async def cancel(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    chat_id = message.channel_id or message.group_id or message.user_id
    if chat_id not in TASKS:
        await message.reply_text("No task active in current chat!")
        return
    for tsk in TASKS[chat_id]:
        try:
            tsk.cancel()
        except Exception:
            pass
    await message.reply_text("Cancelled!")


@client.on_command("copy")
async def processCommand(ctx: BotContext[CommandEvent]):
    event: Message = ctx.event.message
    param = ctx.event.params
    if not param:
        return await event.reply_text("Provide a chanenl username to copy!")
    umsg = await event.reply_text("Starting task!")
    split = param.split()
    start = 0
    end = 1
    try:
        if "-" in split[-1]:
            spl = split[-1].split("-")
            start = int(spl[0])
            end = int(spl[1])
    except Exception as er:
        print(er)
        await event.reply_text(
            "Provide in this format!\n<copy>/copy channelusername startMsgId-endMsgId</copy>"
        )
        return

    timer = Timer()

    async def processMessage(message: TMessage):
        if isinstance(message, types.MessageService):
            return
        if not message:
            return
        name = message.file.name
        if message.document:
            name = message.file.name or (
                "document_"
                + dt.now().isoformat("_", "seconds")
                + guess_extension(message.media.document.mime_type)
            )

            async def downloadCallback(current, total):
                if not timer.can_send():
                    return
                perc = round((current * 100 / total), 2)
                message = f"""
Downloading `{name}`!\n\n{get_progress_bar(perc)} [{humanbytes(current)}/{humanbytes(total)}]"""
                await umsg.edit_text(message)

            client = bots[random.randint(1, len(bots.keys()))]["client"]
            await client.start()
            message = await client.get_messages(split[0], ids=message.id)

            with open(name, "wb") as f:
                await download_file(
                    message.client,
                    message.document or message.photo,
                    f,
                    progress_callback=downloadCallback,
                )
        elif message.photo:
            name = token_hex(8) + ".jpg"
            name = await message.download_media(name)

        async def uploadCallback(upl: UploadProgress):
            if not timer.can_send():
                return
            perc = round((upl.readed / upl.total) * 100, 2)

            name = os.path.basename(upl.path)
            message = f"""
Uploading `{name}`!\n\n{get_progress_bar(perc)} [{humanbytes(upl.readed)}/{humanbytes(upl.total)}]"""
            await umsg.edit_text(message)

        await umsg.reply_media(
            message=message.message,
            document=name,
            progress=uploadCallback,
            tasks_count=10,
            part_size=40 * 1024 * 1024,
        )
        os.remove(name)

    client = await getRandomClient()
    m = event
    chat_id = m.user_session_id or m.group_id or m.channel_id or m.user_id

    async def uploadTask():
        async for m in client.iter_messages(split[0], ids=[*range(start, end + 1)]):
            if not m:
                continue
            LOG.info(f"processing [{m.id}] {m.text} {m.document or m.photo}")
            for _ in range(3):
                if not TASKS.get(chat_id):
                    return
                if _:
                    LOG.info("Retrying...")
                try:
                    await processMessage(m)
                    break
                except Exception as er:
                    LOG.exception(er)
                    await asyncio.sleep(random.randint(3, 5))

    tsk = asyncio.create_task(uploadTask())
    if not TASKS.get(chat_id):
        TASKS[chat_id] = [tsk]
    else:
        TASKS[chat_id].append(tsk)
    try:
        await tsk
    except asyncio.CancelledError:
        pass
    await umsg.delete()


"""
async def get_messages(param, limit=None, callback=None):
    chat_id = param
    hash = None
    LOG.info(f"Getting {param}")
    if "t.me/+" in chat_id:
        hash = chat_id.split("+")[-1]
    elif "t.me/joinchat" in chat_id:
        hash = chat_id.split("/")[-1]

    async def GetMessage(bot: TelegramClient):
        chat_id = param
        if hash:
            invite = await bot(CheckChatInviteRequest(hash))
            if isinstance(invite, ChatInviteAlready):
                chat_id = int(f"-100{invite.chat.id}")
            else:
                updates = await bot(ImportChatInviteRequest(hash))
                chat_id = get_peer_id(updates.chats[0])
            LOG.info(f"Joined {param}")
        if not chat_id:
            return
        async for message in bot.get_messages(chat_id, limit=limit):
            if callback:
                await callback(message)

    await startSession(GetMessage)
"""

client.run()
