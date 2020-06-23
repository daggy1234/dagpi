from fastapi import FastAPI, Header
import aiohttp
from fastapi.responses import StreamingResponse, JSONResponse, RedirectResponse
from io import BytesIO
from fastapi.openapi.utils import get_openapi
from tokencheck import tokenprocess

tkc = tokenprocess()
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageEnhance,
    ImageOps,
    ImageFilter,
    ImageSequence,
)
import wand.image as wi
import os
from datetime import datetime
from pydantic import BaseModel
from writetext import writetext
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from functools import partial
import asyncio

app = FastAPI()
from fastapi.staticfiles import StaticFiles


class Item(BaseModel):
    id: str
    value: str


# /.well-known/acme-challenge
app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/bin", StaticFiles(directory="bin"), name="bin")
# app = FastAPI(docs_url=None, redoc_url=None)
class Message(BaseModel):
    message: str


rdict = {
    400: {
        "message": Message,
        "content": {
            "application/json": {
                "example": {"error": "We were unable to use the link your provided"}
            }
        },
    },
    500: {
        "message": Message,
        "content": {
            "application/json": {
                "example": {"error": "The Image manipulation had a small error"}
            }
        },
    },
    401: {
        "message": Message,
        "content": {"application/json": {"example": {"error": "Invalid token"}}},
    },
    422: {"message": Message},
    200: {
        "message": Message,
        "content": {
            "application/json": {
                "example": {"succes": True, "url": "http://dagpi.tk/bin/LezddANR4N.png"}
            }
        },
    },
}


async def checktoken(tok):
    y = tkc.validtoken(tok)
    return y


async def delimage(source):
    await asyncio.sleep(60)
    os.remove(source)


async def checkenhanced(tok):
    y = tkc.checkenhanced(tok)
    return y


def memegen(byt: BytesIO, text):
    tv = Image.open(BytesIO(byt))

    if str((tv.format)) == "GIF":
        gg = tv
        tv.seek(0)
        form = "gif"
        print("gif")
    else:
        form = "png"
    y = Image.new("RGBA", (tv.size[0], 800), (256, 256, 256))
    wra = writetext(y)
    f = wra.write_text_box(
        20, -75, text, tv.size[0] - 40, "assets/whitney-medium.ttf", 60, color=(0, 0, 0)
    )
    t = f + 75
    bt = wra.retimg()
    im = Image.open(bt)
    ima = im.crop((0, 0, tv.size[0], t))
    retimg = BytesIO()
    if form == "gif":
        flist = []
        for frame in ImageSequence.Iterator(gg):
            bcan = Image.new("RGBA", (tv.size[0], tv.size[1] + t), (0, 0, 0, 0))
            bcan.paste(ima)
            bcan.paste(frame, (0, t))
            flist.append(bcan)
        y = tkc.randomword(10)
        flist[0].save(
            f"bin/{y}.gif",
            format="gif",
            save_all=True,
            append_images=flist,
            optimize=True,
            loop=0,
        )
        form = "gif"
    else:
        bcan = Image.new("RGBA", (tv.size[0], tv.size[1] + t), (0, 0, 0, 0))
        bcan.paste(ima)
        bcan.paste(tv, (0, t))
        form = "png"
        y = tkc.randomword(10)
        bcan.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.{form}"


async def getimg(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            print(r)
            if r.status == 200:
                # imgf = await aiofiles.open(f'avatar{name}.png', mode='wb')
                byt = await r.read()
                return byt
                # await imgf.close()
            else:
                return False
            del r


def getsepia(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with wi.Image() as dst_image:
        with wi.Image(blob=io) as src_image:
            for frame in src_image.sequence:
                frame.sepia_tone(threshold=0.8)
                dst_image.sequence.append(frame)
        y = tkc.randomword(10)
        dst_image.save(filename=f"bin/{y}.gif")
        return f"bin/{y}.gif"


def getwasted(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with wi.Image() as dst_image:
        with wi.Image(blob=io) as src_image:
            for frame in src_image.sequence:
                frame.transform_colorspace("gray")
                dst_image.sequence.append(frame)
        bts = dst_image.make_blob()
        i = BytesIO(bts)
        i.seek(0)
    im = Image.open(i)
    fil = Image.open("assets/wasted.png")
    w, h = im.size
    filr = fil.resize((w, h), 5)
    flist = []
    for frame in ImageSequence.Iterator(im):
        ci = im.convert("RGBA")
        ci.paste(filr, mask=filr)
        flist.append(ci)
    y = tkc.randomword(10)
    flist[0].save(
        f"bin/{y}.gif", format="gif", save_all=True, append_images=flist, optimize=True
    )
    return f"bin/{y}.gif"


def getgay(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with Image.open(io) as im:
        flist = []
        w, h = im.size
        fil = Image.open("assets/gayfilter.png")
        filr = fil.resize((w, h), 5)
        for frame in ImageSequence.Iterator(im):
            ci = frame.convert("RGBA")
            ci.paste(filr, mask=filr)
            ci.show()
            flist.append(ci)
        y = tkc.randomword(10)
        flist[0].save(
            f"bin/{y}.gif",
            format="gif",
            save_all=True,
            append_images=flist,
            optimize=True,
        )
        return f"bin/{y}.gif"


def getcharc(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with wi.Image() as dst_image:
        with wi.Image(blob=io) as src_image:
            for frame in src_image.sequence:
                frame.transform_colorspace("gray")
                frame.sketch(0.5, 0.0, 98.0)
                dst_image.sequence.append(frame)
        y = tkc.randomword(10)
        dst_image.save(filename=f"bin/{y}.gif")
        return f"bin/{y}.gif"


def getsolar(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with wi.Image() as dst_image:
        with wi.Image(blob=io) as src_image:
            for frame in src_image.sequence:
                frame.solarize(threshold=0.5 * frame.quantum_range)
                dst_image.sequence.append(frame)
        y = tkc.randomword(10)
        dst_image.save(filename=f"bin/{y}.gif")
        return f"bin/{y}.gif"


def getpaint(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with wi.Image() as dst_image:
        with wi.Image(blob=io) as src_image:
            for frame in src_image.sequence:
                frame.oil_paint(sigma=3)
                dst_image.sequence.append(frame)
        y = tkc.randomword(10)
        dst_image.save(filename=f"bin/{y}.gif")
        return f"bin/{y}.gif"


def quotegen(user, text, img: BytesIO):
    today = datetime.today()
    y = Image.new("RGBA", (2400, 800), (0, 0, 0, 0))
    ft = Image.open(BytesIO(img))
    topa = ft.resize((150, 150), 5)
    size = (150, 150)
    mask = Image.new("L", size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((20, 20) + size, fill=255)
    avatar = ImageOps.fit(topa, mask.size, centering=(0.5, 0.5))
    y.paste(avatar, (0, 10), mask=mask)
    stoday = datetime.today()
    h = today.hour
    if h > 12:
        su = "PM"
        h = h - 12
    else:
        su = "AM"
    tstring = f"Today at {h}:{today.minute} {su}"
    d = ImageDraw.Draw(y)
    fntd = ImageFont.truetype("assets/whitney-medium.ttf", 80)
    fntt = ImageFont.truetype("assets/whitney-medium.ttf", 40)
    if len(text) > 1000:
        print("text too long")
    else:
        d.text((190, 35), user, color=(256, 256, 256), font=fntd)
        wi = fntd.getsize(user)
        d.text((200 + wi[0], 70), tstring, color=(114, 118, 125), font=fntt)
        wrap = writetext(y)
        f = wrap.write_text_box(
            190, 70, text, 2120, "assets/whitney-medium.ttf", 60, color=(256, 256, 256)
        )
        print(f)
        bt = wrap.retimg()
        im = Image.open(bt)
        ima = im.crop((0, 0, 2400, (f + 90)))
        top = Image.new("RGBA", ima.size, (54, 57, 63))
        out = Image.alpha_composite(top, ima)
        y = tkc.randomword(10)
        out.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"


def getpixel(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with Image.open(io) as t:
        flist = []
        for frame in ImageSequence.Iterator(t):
            imgSmall = frame.resize((32, 32), resample=Image.BILINEAR)
            fim = imgSmall.resize(frame.size, Image.NEAREST)
            flist.append(fim)
        y = tkc.randomword(10)
        flist[0].save(
            f"bin/{y}.gif",
            format="gif",
            save_all=True,
            append_images=flist,
            optimize=True,
        )
        return f"bin/{y}.gif"


def getdeepfry(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with Image.open(io) as t:
        flist = []
        for frame in ImageSequence.Iterator(t):
            colours = ((254, 0, 2), (255, 255, 15))
            img = frame.convert("RGB")
            flare_positions = []
            width, height = img.width, img.height
            img = img.resize(
                (int(width ** 0.75), int(height ** 0.75)), resample=Image.LANCZOS
            )
            img = img.resize(
                (int(width ** 0.88), int(height ** 0.88)), resample=Image.BILINEAR
            )
            img = img.resize(
                (int(width ** 0.9), int(height ** 0.9)), resample=Image.BICUBIC
            )
            img = img.resize((width, height), resample=Image.BICUBIC)
            img = ImageOps.posterize(img, 4)
            r = img.split()[0]
            r = ImageEnhance.Contrast(r).enhance(2.0)
            r = ImageEnhance.Brightness(r).enhance(1.5)

            r = ImageOps.colorize(r, colours[0], colours[1])

            # Overlay red and yellow onto main image and sharpen the hell out of it
            img = Image.blend(img, r, 0.75)
            img = ImageEnhance.Sharpness(img).enhance(100.0)
            flist.append(img)
        y = tkc.randomword(10)
        flist[0].save(
            f"bin/{y}.gif",
            format="gif",
            save_all=True,
            append_images=flist,
            optimize=True,
        )
        return f"bin/{y}.gif"


def getinvert(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with Image.open(io) as t:
        flist = []
        for frame in ImageSequence.Iterator(t):
            frame = frame.convert("RGB")
            blurred_image = ImageOps.invert(frame)
            flist.append(blurred_image)
        y = tkc.randomword(10)
        flist[0].save(
            f"bin/{y}.gif",
            format="gif",
            save_all=True,
            append_images=flist,
            optimize=True,
        )
        return f"bin/{y}.gif"


def getblur(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with Image.open(io) as t:
        flist = []
        for frame in ImageSequence.Iterator(t):
            frame = frame.convert("RGBA")
            blurred_image = frame.filter(ImageFilter.BLUR)
            flist.append(blurred_image)
        y = tkc.randomword(10)
        flist[0].save(
            f"bin/{y}.gif",
            format="gif",
            save_all=True,
            append_images=flist,
            optimize=True,
        )
        return f"bin/{y}.gif"


def gethitler(image: BytesIO):
    with Image.open(BytesIO(image)) as t:
        im = Image.open("assets/hitler.jpg")
        wthf = t.resize((260, 300), 5)

        width = 800
        height = 600
        fim = im.resize((width, height), 4)
        area = (65, 40)
        fim.paste(wthf, area)
        y = tkc.randomword(10)
        fim.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"


# @app.get("/docs", include_in_schema=False)
# async def redoc_html():
#     return get_redoc_html(
#         openapi_url=app.openapi_url,
#         title=app.title + " - Docs",
#         redoc_js_url="/static/redoc.standalone.js",
#     )
#


def tweetgen(username, image: BytesIO, tezt):
    today = datetime.today()
    mlist = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "October",
        "November",
        "December",
    ]
    m = today.month
    mo = mlist[int(m - 1)]

    h = today.hour
    if h > 12:
        su = "PM"
        h = h - 12
    else:
        su = "AM"
    y = str(today.day).strip("0")
    tstring = f"{h}:{today.minute} {su} - {y} {mo} {today.year}"
    print(tstring)
    tweet = Image.open("assets/tweet.png")
    st = username
    lst = st.lower()
    ft = Image.open(BytesIO(image))
    topa = ft.resize((150, 150), 5)
    size = (100, 100)
    mask = Image.new("L", size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((20, 20) + size, fill=255)
    avatar = ImageOps.fit(topa, mask.size, centering=(0.5, 0.5))
    tweet.paste(avatar, mask=mask)
    d = ImageDraw.Draw(tweet)
    fntna = ImageFont.truetype("assets/HelveticaNeue Medium.ttf", 22)
    fnth = ImageFont.truetype("assets/HelveticaNeue Light.ttf", 18)
    fntt = ImageFont.truetype("assets/HelveticaNeue Light.ttf", 18)
    d.multiline_text((110, 35), st, font=fntna, fill=(0, 0, 0, 0))
    d.multiline_text((110, 60), f"@{lst}", font=fnth, fill=(101, 119, 134, 178))
    d.multiline_text((20, 310), tstring, font=fntt, fill=(101, 119, 134, 178))
    margin = 20
    offset = 120
    text = tezt
    print(len(text))
    imgwrap = writetext(tweet)
    imgwrap.write_text_box(
        20, 100, text, 630, "assets/HelveticaNeue Medium.ttf", 26, (0, 0, 0, 0)
    )
    t = imgwrap.retimg()
    y = tkc.randomword(10)
    with open(f"bin/{y}.png", "wb") as out:
        out.write(t.read())
    return f"bin/{y}.png"


def getsatan(image: BytesIO):
    with Image.open(BytesIO(image)) as t:
        im = Image.open("assets/satan.jpg")
        wthf = t.resize((400, 225), 5)
        width = 800
        height = 600
        fim = im.resize((width, height), 4)
        area = (250, 100)
        fim.paste(wthf, area)
        y = tkc.randomword(10)
        fim.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"


def getwanted(image: BytesIO):
    with Image.open(BytesIO(image)) as av:
        im = Image.open("assets/wanted.png")
        tp = av.resize((800, 800), 0)
        im.paste(tp, (200, 450))
        y = tkc.randomword(10)
        im.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"


def getsithorld(image: BytesIO):
    with Image.open(BytesIO(image)) as ft:
        im = Image.open("assets/sithlord.jpg")

        topa = ft.resize((250, 275), 5)
        size = (225, 225)
        mask = Image.new("L", size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((50, 10) + size, fill=255)
        topt = ImageOps.fit(topa, mask.size, centering=(0.5, 0.5))
        im.paste(topt, (225, 180), mask=mask)
        y = tkc.randomword(10)
        im.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"


def gettrash(image: BytesIO):
    with Image.open(BytesIO(image)) as t:
        im = Image.open("assets/trash.jpg")
        wthf = t.resize((200, 150), 5)
        width = 800
        height = 600
        fim = im.resize((width, height), 4)
        area = (500, 250)
        fim.paste(wthf, area)
        y = tkc.randomword(10)
        fim.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"


def getthoughtimg(image: BytesIO, text):
    with Image.open(BytesIO(image)) as ft:
        im = Image.open("assets/speech.jpg")

        file = str(text)
        if len(file) > 200:
            return f"Your text is too long {len(file)} is greater than 200"
        else:
            if len(file) > 151:
                fo = file[:50] + "\n" + file[50:]
                ft = fo[:100] + "\n" + fo[100:]
                ff = ft[:150] + "\n" + ft[150:]
                size = 10
            elif len(file) > 101:
                fo = file[:50] + "\n" + file[50:]
                ff = fo[:100] + "\n" + fo[100:]
                size = 12
            elif len(file) > 51 and len(file) < 100:
                ff = file[:50] + "\n" + file[50:]
                size = 14
            elif len(file) > 20 and len(file) <= 50:
                ff = file
                size = 18
            else:
                ff = file
                size = 25
            wthf = ft.resize((200, 225), 5)

            width = 800
            height = 600
            fim = im.resize((width, height), 4)
            area = (125, 50)
            fim.paste(wthf, area)
            base = fim.convert("RGBA")
            txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
            fnt = ImageFont.truetype("Helvetica-Bold-Font.ttf", size)
            d = ImageDraw.Draw(txt)
            d.text((400, 150), f"{ff}", font=fnt, fill=(0, 0, 0, 255))
            out = Image.alpha_composite(base, txt)
            y = tkc.randomword(10)
            out.save(f"bin/{y}.png", format="PNG", optimize=True)
        return f"bin/{y}.png"


def badimg(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with Image.open(BytesIO(image)) as im:
        back = Image.open("assets/bad.png")
        t = im.resize((200, 200), 5)
        back.paste(t, (20, 150))
        y = tkc.randomword(10)
        back.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"


def getangel(image: BytesIO):
    with Image.open(BytesIO(image)) as t:
        im = Image.open("assets/angel.jpg")
        wthf = t.resize((300, 175), 5)
        width = 800
        height = 600
        fim = im.resize((width, height), 4)
        area = (250, 130)
        fim.paste(wthf, area)
        y = tkc.randomword(10)
        fim.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"


@app.get("/docs", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


@app.get("/playground", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API playground",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/", include_in_schema=False)
def read_root():
    return {
        "Hello": "World",
        "Join our discord server to get a token": "http://server.daggy.tech",
        "Read the documentation at ": "http://dagpi.tk/docs",
        "Play around with the api (needs token)": "http://dagpi.tk/playground",
        "Check out dagbot": "https://dagbot-is.the-be.st",
    }


@app.post("/api/wanted", response_model=Item, responses=rdict)
async def wanted(token: str = Header(None), url: str = Header(None)):
    """Get a wanted poster of a person by supplying a url"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getwanted, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/bad", response_model=Item, responses=rdict)
async def bad(token: str = Header(None), url: str = Header(None)):
    """Generate an image pointing at someone calling them bad"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return "Error"
        else:
            img = badimg(byt)
            return JSONResponse(
                status_code=200,
                content={"succes": True, "url": f"http://dagpi.tk/{img}"},
            )

    else:
        return "Invalid token"


# @app.post('/api/deepfry')
# async def deepfry(token: str = Header(None),url:str = Header(None)):
#
#     r = await checktoken(token)
#     if r:
#         byt = await getimg(url)
#         if byt == False:
#             return JSONResponse(status_code=400,content={'error':"We were unable to use the link your provided"})
#         else:
#             fn = partial(get,byt)
#             loop = asyncio.get_event_loop()
#             img = await loop.run_in_executor(None,fn)
#             if isinstance(img,BytesIO):
#                 return StreamingResponse(img, status_code=200,media_type="image/png")
#
#             else:
#                 return JSONResponse(status_code=500,content={"error":"The Image manipulation had a small"})
#     else:
#         return JSONResponse(status_code=401,content={'error':'Invalid token'})
@app.post("/api/hitler", response_model=Item, responses=rdict)
async def hitler(token: str = Header(None), url: str = Header(None)):
    """Make a person worse than hitler by supplying a url"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(gethitler, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/tweet", response_model=Item, responses=rdict)
async def tweet(
    token: str = Header(None),
    url: str = Header(None),
    name: str = Header(None),
    text: str = Header(None),
):
    """Generate a realistic fake tweet of someone by supplying a url, the text and their name"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(tweetgen, name, byt, text)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/quote", response_model=Item, responses=rdict)
async def quote(
    token: str = Header(None),
    url: str = Header(None),
    name: str = Header(None),
    text: str = Header(None),
):
    """Get a realistic discord message of someone """

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(quotegen, name, text, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/thoughtimage", response_model=Item, responses=rdict)
async def thoughtimage(
    token: str = Header(None), url: str = Header(None), text: str = Header(None)
):
    """Help a person think aloud by simply adding text to a thought bubble"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getthoughtimg, byt, text)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/angel", response_model=Item, responses=rdict)
async def angel(token: str = Header(None), url: str = Header(None)):
    """Divine and angelic person"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getangel, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.get("/api", include_in_schema=False)
async def redirecttodocs():
    return RedirectResponse(url="/docs")


@app.get("/server", include_in_schema=False)
async def serverredirect():
    return RedirectResponse(url="https://discord.gg/4R72Pks")


@app.get("/wrappers", include_in_schema=False)
async def comiongsoon():
    return JSONResponse(status_code=404, content={"In the works": "Wrappers soon"})


@app.post("/api/trash", response_model=Item, responses=rdict)
async def trash(token: str = Header(None), url: str = Header(None)):
    """Denotes someone is trash aka garbage"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(gettrash, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/satan", response_model=Item, responses=rdict)
async def satan(token: str = Header(None), url: str = Header(None)):
    """Depcits the true form of a devil in disguise"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getsatan, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/paint", response_model=Item, responses=rdict)
async def paint(token: str = Header(None), url: str = Header(None)):
    """Turn a boring old picture/gif into a work of art"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getpaint, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/solar", response_model=Item, responses=rdict)
async def solar(token: str = Header(None), url: str = Header(None)):
    """make an image/gif be tripping with weird effects"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getsolar, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/evil", response_model=Item, responses=rdict)
async def evil(token: str = Header(None), url: str = Header(None)):
    """*Laughs in Sithlord*"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getsithorld, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/blur", response_model=Item, responses=rdict)
async def blur(token: str = Header(None), url: str = Header(None)):
    """Blur an image/gif"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getblur, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/invert", response_model=Item, responses=rdict)
async def invert(token: str = Header(None), url: str = Header(None)):
    """A fliperroni , swithc the colors of an image/gif"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getinvert, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


# uvicorn main:app --reload
@app.post("/api/pixel", response_model=Item, responses=rdict)
async def pixel(token: str = Header(None), url: str = Header(None)):
    """Retro 8but version of an image/gif"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getpixel, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/deepfry", response_model=Item, responses=rdict)
async def deepfry(token: str = Header(None), url: str = Header(None)):
    """Deepfry a gif/static image"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getdeepfry, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/sepia", response_model=Item, responses=rdict)
async def sepia(token: str = Header(None), url: str = Header(None)):
    """Add a cool brown filter on an image/gif"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getsepia, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/wasted", response_model=Item, responses=rdict)
async def wasted(token: str = Header(None), url: str = Header(None)):
    """GTA V Wasted screen on any image/gif"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getwasted, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/gay", response_model=Item, responses=rdict)
async def gay(token: str = Header(None), url: str = Header(None)):
    """Pride flag on any image/gif. Show some love <3"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getgay, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/charcoal", response_model=Item, responses=rdict)
async def charcoal(token: str = Header(None), url: str = Header(None)):
    """Turn an image/gif into an artistic sketch"""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(getcharc, byt)
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


@app.post("/api/meme", response_model=Item, responses=rdict)
async def meme(
    token: str = Header(None), url: str = Header(None), text: str = Header(None)
):
    """Generate a meme by supplying the top joke and the template.Supports both gif and static images."""

    r = await checktoken(token)
    if r:
        byt = await getimg(url)
        if byt == False:
            return JSONResponse(
                status_code=400,
                content={"error": "We were unable to use the link your provided"},
            )
        else:
            fn = partial(memegen, byt, text)
            loop = asyncio.get_event_loop()
            img, f = await loop.run_in_executor(None, fn)
            if isinstance(img, str):
                return JSONResponse(
                    status_code=200,
                    content={"succes": True, "url": f"http://dagpi.tk/{img}"},
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "The Image manipulation had a small"},
                )
    else:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})


def custom_openapi(openapi_prefix: str = ""):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Dagpi",
        version="1.0",
        description="The Number 1 Image generation api",
        routes=app.routes,
        openapi_prefix=openapi_prefix,
    )
    openapi_schema["info"]["x-logo"] = {"url": "https://dagbot-is.the-be.st/logo.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
