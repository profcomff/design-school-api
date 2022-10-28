from design_bot.routes.base import app
from design_bot.routes.vk import bot
import uvicorn


if __name__ == '__main__':
    bot.run_forever()
    uvicorn.run(app)
