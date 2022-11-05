import uvicorn

from design_bot.routes.base import app

if __name__ == '__main__':
    uvicorn.run(app)
