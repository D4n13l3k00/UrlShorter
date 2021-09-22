import random
import re
import string

import redis
from fastapi import FastAPI, Request
from fastapi.responses import *
from fastapi.templating import Jinja2Templates

db = redis.Redis(host='REDIS_DB_URL', port=6379, db=0)
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

@app.get('/favicon.ico', include_in_schema=False)
async def null_point():
    return Response(status_code=404)

@app.get('/create', include_in_schema=False)
async def create(rq: Request, link: str):
    if not is_url.match(link):
        return templates.TemplateResponse("message.html", {"request":rq, "message":"Not a valid url"}, 502)
    while True:
        shrt = ''.join(random.sample(string.ascii_letters, 5))
        if not db.get(shrt):
            break
    db.set(shrt, link)
    return templates.TemplateResponse("success.html", {"request":rq, "link":f"http://{rq.url.hostname}{':'+ str(rq.base_url.port) if rq.base_url.port != 80 else ''}/{shrt}"})


@app.get('/{shrt}', include_in_schema=False)
async def create(rq: Request, shrt: str):
    u = db.get(shrt)
    if u:
        return RedirectResponse(u.decode('utf-8'))
    return templates.TemplateResponse("message.html", {"request":rq, "message":"404: Not found"}, 404)

