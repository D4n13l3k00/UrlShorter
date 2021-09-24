import os
import random
import re
import string

import aioredis
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

db = aioredis.from_url(os.getenv("REDIS_URL")
                       or "redis://localhost/1", decode_responses=True)

templates = Jinja2Templates(directory="templates")
is_url = re.compile(
    r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')

app = FastAPI(
    title='UrlShorter',
    version='1.1',
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)


@app.get('/')
async def main_html(rq: Request):
    return templates.TemplateResponse("index.html", {"request": rq})


@app.get('/create')
async def create(rq: Request, link: str):
    if not is_url.match(link):
        return templates.TemplateResponse("message.html", {"request": rq, "message": "Not a valid url"}, 404)
    n = 1
    while True:
        shrt = ''.join(random.choice(string.ascii_letters) for _ in range(n))
        if not await db.get(shrt):
            break
        n += 1
    await db.set(shrt, link)
    return templates.TemplateResponse("success.html",
                                      {"request": rq,
                                       "link": f"http://{rq.url.hostname}{':'+ str(rq.base_url.port) if rq.base_url.port else ''}/{shrt}"
                                       })


@app.get('/{shrt}')
async def create(rq: Request, shrt: str):
    u = await db.get(shrt)
    if u:
        return RedirectResponse(u)
    return templates.TemplateResponse("message.html", {"request": rq, "message": "404: Not found"}, 404)
