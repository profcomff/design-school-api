from design_bot.settings import get_settings
from vkbottle import Bot
from vkbottle.bot import Message
from vkbottle.callback import BotCallback
from fastapi import BackgroundTasks, APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
from .models.confrm_access import AccessModel
from logging import getLogger

logger = getLogger(__name__)

bot_router = APIRouter()

# token from vk for init callback server
confirmation_code: str
secret_key: str
TOKEN = get_settings().TOKEN
callback = BotCallback(url="https://design.bot.test.profcomff.com/", title="my server")
bot = Bot(token=TOKEN, callback=callback)


@bot.on.message(text="П")
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    logger.info(f"{users_info}")
    ans = await message.answer(f"Hello, {users_info[0].first_name}")
    logger.info(f"{ans}")


@bot_router.on_event("startup")
async def startup_event():
    global confirmation_code, secret_key
    confirmation_code, secret_key = await bot.setup_webhook()


@bot_router.post("/")
async def vk_handler(req: Request, background_task: BackgroundTasks):
    global confirmation_code, secret_key

    try:
        data = await req.json()
    except Exception:
        return Response("not today", status_code=403)

    if data.get("secret") == secret_key:
        # Running the process in the background, because the logic can be complicated
        return await bot.process_event(data)

    if data.get("type") == "confirmation":
        if data.get("group_id") == 213296541:
            return PlainTextResponse('486b5b99')
        return Response(confirmation_code)

    # If the secrets match, then the message definitely came from our bot

    return Response("ok")
