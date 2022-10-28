from design_bot.settings import get_settings
from vkbottle import Bot
from vkbottle.bot import Message
from vkbottle.callback import BotCallback
from fastapi import BackgroundTasks, APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
from .models.confrm_access import AccessModel


bot_router = APIRouter()

# token from vk for init callback server
confirmation_code: str
secret_key: str
TOKEN = get_settings().TOKEN
callback = BotCallback(url="https://design.bot.test.profcomff.com/", title="my server")
bot = Bot(token=TOKEN, callback=callback)


@bot.on.message
async def hi_handler(message: Message):
    await message.answer(message.json())


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

    if data["type"] == "confirmation":
        return Response(confirmation_code)

    # If the secrets match, then the message definitely came from our bot
    if data["secret"] == secret_key:
        # Running the process in the background, because the logic can be complicated
        background_task.add_task(bot.process_event, data)
    return Response("ok")


@bot_router.post("/confirm")
async def confirm_group(access: AccessModel) -> PlainTextResponse:
    if access.group_id == 213296541:
        return PlainTextResponse('7c0b2c0d')
