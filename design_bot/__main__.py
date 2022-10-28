import logging

from design_bot.routes.base import app
from design_bot.routes.vk import bot
import uvicorn

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


if __name__ == '__main__':
    bot.run_forever()
    uvicorn.run(app)
