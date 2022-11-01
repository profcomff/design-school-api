import logging

from design_bot.routes.base import app
import uvicorn

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


if __name__ == '__main__':
    uvicorn.run(app)
