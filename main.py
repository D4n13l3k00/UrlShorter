import random
import re
import string

import aioredis
from fastapi import FastAPI, Request
from fastapi.responses import *
from fastapi.templating import Jinja2Templates

db = aioredis.from_url("redis://localhost/1", decode_responses=True)

templates = Jinja2Templates(directory="templates")
is_url = re.compile(
    r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')

app = FastAPI(
    title='Shrtr',
    version='1.0'
)

@app.get('/', include_in_schema=False)
async def main_html(rq: Request):
    return templates.TemplateResponse("index.html", {"request":rq})

@app.get('/create', include_in_schema=False)
async def create(rq: Request, link: str):
    if not is_url.match(link):
        return templates.TemplateResponse("message.html", {"request":rq, "message":"Not a valid url"}, 502)
    n = 1
    while True:
        shrt = ''.join(random.sample(string.ascii_letters, n))
        if not await db.get(shrt):
            break
        n += 1
    await db.set(shrt, link)
    return templates.TemplateResponse("success.html", {"request":rq, "link":f"http://{rq.url.hostname}{':'+ str(rq.base_url.port) if rq.base_url.port != 80 else ''}/{shrt}"})


@app.get('/{shrt}', include_in_schema=False)
async def create(rq: Request, shrt: str):
    u = await db.get(shrt)
    if u:
        return RedirectResponse(u)
    return templates.TemplateResponse("message.html", {"request":rq, "message":"404: Not found"}, 404)

