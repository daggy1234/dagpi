from fastapi import FastAPI, Header,Request
import aiohttp
import os
import json
import config
from fastapi.responses import StreamingResponse, JSONResponse, RedirectResponse
from io import BytesIO
import random
import typing
import sentry_sdk
from skimage.morphology import skeletonize,disk
import skimage
from skimage.color import rgb2gray,gray2rgb,rgba2rgb
from skimage.color.adapt_rgb import adapt_rgb, each_channel
from skimage import data, img_as_float
from skimage.exposure import rescale_intensity
from skimage import io
from skimage.segmentation import chan_vese,watershed
from io import BytesIO
from skimage.feature import hog
import matplotlib.pyplot as plt
from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
import re
import textwrap
from async_timeout import timeout
from fastapi.openapi.utils import get_openapi
sentry_sdk.init(dsn=config.sentry)
from tokencheck import tokenprocess
from datetime import datetime, timedelta
import wand.exceptions as we
session = aiohttp.ClientSession()
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

wsgi_app = SentryWsgiMiddleware(app)
from fastapi.staticfiles import StaticFiles


class Item(BaseModel):
    id: str
    value: str

class BadUrl(Exception):
    pass


class InvalidToken(Exception):
    pass


class RateLimit(Exception):
    pass


class Badimage(Exception):
    pass


class FileLarge(Exception):
    pass


class ServerTimeout(Exception):
    pass


# /.well-known/acme-challenge
app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/bin", StaticFiles(directory="bin"), name="bin")
app.mount("/pokemon", StaticFiles(directory="pokemon"), name="pokemon")
# app = FastAPI(docs_url=None, redoc_url=None)
class Message(BaseModel):
    message: str


rdict = {
    400: {
        "message": Message,
        "content": {
            "application/json": {
                "example": {"error": "We were unable to use the link your provided."}
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
    429: {
        "message": Message,
        "content": {"application/json": {"example": {"error": "You are being ratelimited. Please stick to 60 requests per minute"}}},
    },
    415: {
        "message": Message,
        "content": {"application/json": {"example": {"error": "There was no image at your url"}}},
    },
    413: {
        "message": Message,
        "content": {"application/json": {"example": {"error": "The image your provided was too large. Please use files under 10 Mb"}}},
    },
    408: {
        "message": Message,
        "content": {"application/json": {"example": {"error": "The time taken to connect to the image server and download the image was too long."}}},
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
    y, s = tkc.validtoken(tok)
    print(y)
    print(s)
    if y:
        return y
    else:
        if s == 1:
            raise InvalidToken('Your token is invalid')
        elif s == 2:
            raise RateLimit('Tooo many requests')
        else:
            return False
async def checkenhcanced(tok):
    y = tkc.checkenhanced(tok)
    if y:
        return y
    else:
        raise InvalidToken('You do not have an enhanced token. Only admins have this.')
async def delimage(source):
    await asyncio.sleep(60)
    os.remove(source)






async def getimg(url):
    import re
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    r = (re.match(regex, url) is not None)
    if r == False:
        raise BadUrl('Your url is malformed')
    try:
        async with timeout(10):
            r = await session.get(url)
            if r.status == 200:
                # imgf = await aiofiles.open(f'avatar{name}.png', mode='wb')
                byt = await r.read()
                io = BytesIO(byt)
                bitsize = (len(io.getbuffer()) - io.tell())
                if bitsize > 10 * (2 ** 20):
                    raise FileLarge('File too large')
                else:
                    return byt
                # await imgf.close()
            else:
                return False
    except asyncio.TimeoutError:
        raise ServerTimeout('Image took too long to get')
def bytes_to_np(img_bytes):
    bytes = BytesIO(img_bytes)
    ret = io.imread(bytes)
    return ret

def getsobel(img):
    bt = bytes_to_np(img)
    @adapt_rgb(each_channel)
    def _sobel_each(image):
        return skimage.filters.sobel(image)
    resc = rescale_intensity(1 - _sobel_each(bt))
    y = tkc.randomword(10)
    plt.imsave(f'bin/{y}.png', resc)
    return f'bin/{y}.png'
def gethog(img):
    bt = bytes_to_np(img)
    fd, hog_image = hog(bt, orientations=8, pixels_per_cell=(16, 16),
                        cells_per_block=(1, 1), visualize=True, multichannel=True)
    y = tkc.randomword(10)
    plt.imsave(f'bin/{y}.png', hog_image, cmap=plt.cm.get_cmap("seismic"))
    return f'bin/{y}.png'
def pilimagereturn(image: bytes):
    try:
        io = BytesIO(image)
        io.seek(0)
        im = Image.open(io)
        return im
    except:
        raise Badimage('There was no image at your url')


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
    try:
        with wi.Image() as dst_image:
            with wi.Image(blob=io) as src_image:
                for frame in src_image.sequence:
                    frame.transform_colorspace("gray")
                    dst_image.sequence.append(frame)
            bts = dst_image.make_blob()
            i = BytesIO(bts)
            i.seek(0)
    except we.TypeError:
        raise Badimage
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

def memegen(byt, text):
    tv = pilimagereturn(byt)
    wid = tv.size[0]
    hei = tv.size[0]
    if 0 < wid < 200:
        sfm = [25, 15, 10, 5]
        mplier = 0.1
        hply = 0.1
    elif 400 > wid >= 200:
        sfm = [30, 20, 10, 5]
        mplier = 0.075
        hply = 0.2
    elif 400 <= wid < 600:
        sfm = [50, 30, 20, 10]
        mplier = 0.05
        hply = 0.3
    elif 800 > wid >= 600:
        sfm = [70, 50, 30, 20]
        mplier = 0.025
        hply = 0.4
    elif 1000 > wid >= 800:
        sfm = [80, 60, 40, 30]
        mplier = 0.01
        hply = 0.5
    elif 1500 > wid >= 1000:
        sfm = [100, 80, 60, 40]
        mplier = 0.01
        hply = 0.6
    elif 2000 > wid >= 1400:
        sfm = [120, 100, 80, 60]
        mplier = 0.01
        hply = 0.6
    elif 2000 <= wid < 3000:
        sfm = [140, 120, 100, 80]
        mplier = 0.01
        hply = 0.6
    elif wid >= 3000:
        sfm = [180, 160, 140, 120]
        mplier = 0.01
        hply = 0.6
    x_pos = int(mplier * wid)
    y_pos = int(-1 * (mplier * hply * 10) * hei)
    if 50 > len(text) > 0:
        size = sfm[1]
    elif 100 > len(text) > 50:
        size = sfm[1]
    elif 100 < len(text) < 250:
        size = sfm[2]
    elif len(text) > 250 and len(text) > 500:
        size = sfm[3]
    elif 500 < len(text) < 1000:
        size = sfm[4]
    if str(tv.format) == "GIF":
        gg = tv
        tv.seek(0)
        form = "gif"
    else:
        form = "png"
    y = Image.new("RGBA", (tv.size[0], 800), (256, 256, 256))
    wra = writetext(y)
    f = wra.write_text_box(
        x_pos, -10, text, tv.size[0] - 40, "assets/whitney-medium.ttf", size, color=(0, 0, 0)
    )
    t = f
    bt = wra.retimg()
    im = Image.open(bt)
    ima = im.crop((0, 0, tv.size[0], t))
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

def getjail(image):
    im = pilimagereturn(image)
    flist = []
    w, h = im.size
    fil = Image.open("assets/jail.png")
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


def getgay(image):
    im = pilimagereturn(image)
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

def getwtp(ig: BytesIO,rst):
    im = pilimagereturn(ig)
    ques = Image.open('assets/wtp.png')
    ans = Image.open('assets/wtp.png')
    w, h = im.size
    imane = Image.new('RGBA', (w, h), color=(3, 100, 150))
    fim = Image.composite(imane, im, mask=im)
    ques.paste(fim, (50, 50), mask=im)
    ans.paste(im, (50, 40), mask=im)
    ques.save(f'pokemon/{rst}q.png')
    ans.save(f'pokemon/{rst}a.png')
    with open('assets/pokemons.json', 'r') as file:
        cont = json.load(file)
        mondict = cont[rst]
    return (mondict)
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


def getswirl(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with wi.Image() as dst_image:
        with wi.Image(blob=io) as src_image:
            for frame in src_image.sequence:
                frame.swirl(degree=-90)
                dst_image.sequence.append(frame)
        y = tkc.randomword(10)
        dst_image.save(filename=f"bin/{y}.gif")
        return f"bin/{y}.gif"


def getpolaroid(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with wi.Image() as dst_image:
        with wi.Image(blob=io) as src_image:
            for frame in src_image.sequence:
                frame.polaroid()
                dst_image.sequence.append(frame)
        y = tkc.randomword(10)
        dst_image.save(filename=f"bin/{y}.gif")
        return f"bin/{y}.gif"
def getedged(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with wi.Image() as dst_image:
        with wi.Image(blob=io) as src_image:
            for frame in src_image.sequence:
                frame.alpha_channel = False
                frame.transform_colorspace('gray')
                frame.edge(2)
        y = tkc.randomword(10)
        dst_image.save(filename=f"bin/{y}.gif")
        return f"bin/{y}.gif"

def getnight(image: BytesIO):
    io = BytesIO(image)
    io.seek(0)
    with wi.Image() as dst_image:
        with wi.Image(blob=io) as src_image:
            for frame in src_image.sequence:
                frame.blue_shift(factor=1.25)
                dst_image.sequence.append(frame)
        y = tkc.randomword(10)
        dst_image.save(filename=f"bin/{y}.gif")
        return f"bin/{y}.gif"


def quotegen(user, text, img):
    today = datetime.today()
    y = Image.new("RGBA", (2400, 800), (0, 0, 0, 0))
    ft = pilimagereturn(img)
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


def getpixel(image):
    t = pilimagereturn(image)
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


def getdeepfry(image):
    t = pilimagereturn(image)
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


def getinvert(image):
    t = pilimagereturn(image)
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


def getblur(image):
    t = pilimagereturn(image)
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


def gethitler(image):
    t = pilimagereturn(image)
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


def tweetgen(username, image, tezt):
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
    ft = pilimagereturn(image)
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


def getsatan(image):
    t = pilimagereturn(image)
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


def getwanted(image):
    av = pilimagereturn(image)
    im = Image.open("assets/wanted.png")
    tp = av.resize((800, 800), 0)
    im.paste(tp, (200, 450))
    y = tkc.randomword(10)
    im.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"
def gettriggered(image):
    im = pilimagereturn(image)
    im = im.resize((500, 500), 1)
    overlay = Image.open('assets/triggered.png')
    ml = []
    for i in range(0, 30):
        blank = Image.new('RGBA', (400, 400))
        x = -1 * (random.randint(50, 100))
        y = -1 * (random.randint(50, 100))
        blank.paste(im, (x, y))
        rm = Image.new('RGBA', (400, 400), color=(255, 0, 0, 80))
        blank.paste(rm, mask=rm)
        blank.paste(overlay, mask=overlay)
        ml.append(blank)
    y = tkc.randomword(10)
    ml[0].save(f"bin/{y}.gif", format='gif', save_all=True, duration=1, append_images=ml, loop=0)
    return f"bin/{y}.gif"
def getobama(image):
    im = pilimagereturn(image)
    obam = Image.open('assets/obama.png')
    y = im.resize((300, 300), 1)
    obam.paste(y, (250, 100))
    obam.paste(y, (650, 0))
    y = tkc.randomword(10)
    obam.save(f'bin/{y}.png')
    return f'bin/{y}.png'
def getsithorld(image):
    ft = pilimagereturn(image)
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
def get5g1g(img1,img2):
    im = pilimagereturn(img1)
    im2 = pilimagereturn(img2)
    back = Image.open('assets/5g1g.png')
    im = im.resize((150,150),1)
    back.paste(im,(80,100))
    back.paste(im,(320,10))
    back.paste(im,(575,60))
    back.paste(im,(830,60))
    back.paste(im,(1050,0))
    im2 = im2.resize((150,150),1)
    back.paste(im2,(650,320))
    y = tkc.randomword(10)
    back.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"

def getwhyareyougay(img1,img2):
    gay = pilimagereturn(img1)
    av = pilimagereturn(img2)
    im = Image.open('assets/whyareyougay.png')
    mp = av.resize((150, 150), 0)
    op = gay.resize((150, 150), 0)
    im.paste(op, (550, 100))
    im.paste(mp, (100, 125))
    y = tkc.randomword(10)
    im.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"
def gettrash(image):
    t = pilimagereturn(image)
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


def getthoughtimg(image, text):
    ft = pilimagereturn(image)
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


def badimg(image):
    im = pilimagereturn(image)
    back = Image.open("assets/bad.png")
    t = im.resize((200, 200), 5)
    back.paste(t, (20, 150))
    y = tkc.randomword(10)
    back.save(f"bin/{y}.png", format="PNG", optimize=True)
    return f"bin/{y}.png"


def getangel(image):
    t = pilimagereturn(image)
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
class Meme:
    def __init__(self, text):

        self.meme_path = None
        self.tmp_path = None
        self.text = text
        self.filetype = "png"
        self.font_path = "assets/impact.ttf"

    def store_image(self):
        y = tkc.randomword(10)
        self.image.save(f"bin/{y}.png", format="PNG", optimize=True)
        return f"bin/{y}.png"

    def get_image(self, image):
        self.image = Image.open(BytesIO(image)).convert("RGB")
        return True

    def find_longest_line(self, text):
        longest_width = 0
        longest_line = ""
        for line in text:
            width = self.draw.textsize(
                line, font=ImageFont.truetype(self.font_path, 20)
            )[0]
            if width > longest_width:
                longest_width = width
                longest_line = line

        return longest_line

    def get_font_measures(self, text, font_size, ratio):
        measures = {}
        measures["font"] = ImageFont.truetype(self.font_path, size=font_size)
        measures["width"] = self.draw.textsize(text, font=measures["font"])[0]
        measures["ratio"] = measures["width"] / float(self.image.width)
        measures["ratio_diff"] = abs(ratio - measures["ratio"])

        return measures

    def optimize_font(self, text):
        """Fuckin' magnets how do they work"""
        font_min_size = 12
        font_max_size = 70
        font_size_range = range(font_min_size, font_max_size + 1)

        longest_text_line = self.find_longest_line(text)

        # set min/max ratio of font width to image width
        min_ratio = 0.7
        max_ratio = 0.9
        perfect_ratio = min_ratio + (max_ratio - min_ratio) / 2
        ratio = 0

        while (ratio < min_ratio or ratio > max_ratio) and len(font_size_range) > 2:
            measures = {
                "top": self.get_font_measures(
                    text=longest_text_line,
                    font_size=font_size_range[-1],
                    ratio=perfect_ratio,
                ),
                "low": self.get_font_measures(
                    text=longest_text_line,
                    font_size=font_size_range[0],
                    ratio=perfect_ratio,
                ),
            }

            half_index = len(font_size_range) // 2
            if measures["top"]["ratio_diff"] < measures["low"]["ratio_diff"]:
                closer = "top"
                font_size_range = font_size_range[int(half_index) : -1]
            else:
                closer = "low"
                font_size_range = font_size_range[0:half_index]

            ratio = measures[closer]["ratio"]
            witdh = measures[closer]["width"]
            font = measures[closer]["font"]

        width = self.draw.textsize(longest_text_line, font=font)[0]

        return font, width

    def set_text_wrapping(self, text_length):
        if text_length <= 32:
            wrapping = 32
        elif text_length > 100:
            wrapping = 10 + text_length // 3
        elif text_length > 32:
            wrapping = 5 + text_length // 2
        return int(wrapping)

    def prepare_text(self, text):
        if not text:
            return "", 0
        if type(text) == list:
            text = text[0]
        wrapping = self.set_text_wrapping(len(text))
        text = text.strip().upper()
        text = textwrap.wrap(text, wrapping)
        font, text_width = self.optimize_font(text)

        text = "\n".join(text)

        return text, text_width, font

    def draw_text(self, xy, text, font):
        x = xy[0]
        y = xy[1]

        o = 1

        xys = (
            (x + o, y),
            (x - o, y),
            (x + o, y + o),
            (x - o, y - o),
            (x - o, y + o),
            (x, y - o),
            (x, y + o),
        )

        for xy in xys:
            self.draw.multiline_text(xy, text, fill="black", font=font, align="center")

        self.draw.multiline_text((x, y), text, fill="white", font=font, align="center")

    def draw_meme(self):
        self.draw = ImageDraw.Draw(self.image)

        margin_xy = (0, self.image.height / 18)

        text_top = self.text.split("|")[0]
        if text_top:
            text_top, text_top_width, top_font = self.prepare_text(text_top)
            top_xy = (((self.image.width - text_top_width) / 2), (margin_xy[1]))
            self.draw_text(top_xy, text_top, top_font)

        text_bottom = self.text.split("|")[1:]
        if text_bottom:
            text_bottom, text_bottom_width, bottom_font = self.prepare_text(text_bottom)
            bottom_xy = [
                ((self.image.width - text_bottom_width) / 2),
                (
                    self.image.height
                    - bottom_font.getsize(text_bottom)[1] * len(text_bottom.split("\n"))
                    - margin_xy[1]
                ),
            ]
            self.draw_text(bottom_xy, text_bottom, bottom_font)

    def make_meme(self, path):

        ret = self.get_image(path)
        if ret:
            self.draw_meme()
            im = self.store_image()
            return im
        else:
            return False
@app.exception_handler(we.TypeError)
async def wandtypehandler(request: Request,exec: we.TypeError):
    return JSONResponse(status_code=415,content={'error':'There was no image at the url you provided'})
@app.exception_handler(Badimage)
async def badimage(request : Request,exec: Badimage):
    return JSONResponse(status_code=415, content={'error': 'There was no image at the url you provided'})
@app.exception_handler(BadUrl)
async def badurl(request : Request,exec: BadUrl):
    return JSONResponse(status_code=400, content={'error': 'The url provided for the image was incorrectly framed'})
@app.exception_handler(FileLarge)
async def largefile(request : Request,exec: FileLarge):
    return JSONResponse(status_code=413, content={'error': 'The file you provided was too large'})
@app.exception_handler(ServerTimeout)
async def servertimeout(request : Request,exec: ServerTimeout):
    return JSONResponse(status_code=408, content={'error': 'The time taken to get the image at your url was too long'})
@app.exception_handler(RateLimit)
async def ratelimit(request : Request,exec: RateLimit):
    return JSONResponse(status_code=429, content={'error': 'You are being ratelimited. Please stick to 60 requests per minute'})
@app.exception_handler(InvalidToken)
async def badimage(request : Request,exec: InvalidToken):
    return JSONResponse(status_code=401, content={'error': 'The token you provided is invalid. Please apply for a token'})

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
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
                )

@app.post("/api/obamameme", response_model=Item, responses=rdict)
async def obamameme(token: str = Header(None), url: str = Header(None)):
    """Get a wanted poster of a person by supplying a url"""
    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(getobama, byt)
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
            content={"error": "The Image manipulation had a small error"},
                )


@app.post("/api/bad", response_model=Item, responses=rdict)
async def bad(token: str = Header(None), url: str = Header(None)):
    """Generate an image pointing at someone calling them bad"""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(badimg, byt)
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
            content={"error": "The Image manipulation had a small error"},
        )


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
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )


@app.post("/api/tweet", response_model=Item, responses=rdict)
async def tweet(
        token: str = Header(None),
        url: str = Header(None),
        name: str = Header(None),
        text: str = Header(None),
):
    """Generate a realistic fake tweet of someone by supplying a url, the text and their name"""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(tweetgen, name,byt,text)
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
            content={"error": "The Image manipulation had a small error"},
        )


@app.post("/api/quote", response_model=Item, responses=rdict)
async def quote(
        token: str = Header(None),
        url: str = Header(None),
        name: str = Header(None),
        text: str = Header(None),
):
    """Get a realistic discord message of someone """

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(quotegen, name, text ,byt)
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
            content={"error": "The Image manipulation had a small error"},
        )


@app.post("/api/thoughtimage", response_model=Item, responses=rdict)
async def thoughtimage(
        token: str = Header(None), url: str = Header(None), text: str = Header(None)
):
    """Help a person think aloud by simply adding text to a thought bubble"""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(getthoughtimg, byt,text)
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
            content={"error": "The Image manipulation had a small error"},
        )


@app.post("/api/angel", response_model=Item, responses=rdict)
async def angel(token: str = Header(None), url: str = Header(None)):
    """Divine and angelic person"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )


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
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )


@app.post("/api/satan", response_model=Item, responses=rdict)
async def satan(token: str = Header(None), url: str = Header(None)):
    """Depcits the true form of a devil in disguise"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )

@app.post("/api/sobel", response_model=Item, responses=rdict)
async def sobel(token: str = Header(None), url: str = Header(None)):
    """Vividly colored image with a pretty background"""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(getsobel, byt)
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
            content={"error": "The Image manipulation had a small error"},
        )
@app.post("/api/hog", response_model=Item, responses=rdict)
async def hogend(token: str = Header(None), url: str = Header(None)):
    """Histogram of oriented ggradients (trippy dashes)"""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(gethog, byt)
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
            content={"error": "The Image manipulation had a small error"},
        )
@app.post("/api/paint", response_model=Item, responses=rdict)
async def paint(token: str = Header(None), url: str = Header(None)):
    """Turn a boring old picture/gif into a work of art"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )


@app.post("/api/night", response_model=Item, responses=rdict)
async def night(token: str = Header(None), url: str = Header(None)):
    """Turn a   picture/gif into a nighttime scene"""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(getnight, byt)
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
            content={"error": "The Image manipulation had a small error"},
        )

@app.post("/api/polaroid", response_model=Item, responses=rdict)
async def polaroid(token: str = Header(None), url: str = Header(None)):
    """Turn a   picture/gif into a polarid image"""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(getpolaroid, byt)
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
            content={"error": "The Image manipulation had a small error"},
        )

@app.post("/api/solar", response_model=Item, responses=rdict)
async def solar(token: str = Header(None), url: str = Header(None)):
    """make an image/gif be tripping with weird effects"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )
@app.post("/api/edge", response_model=Item, responses=rdict)
async def edge(token: str = Header(None), url: str = Header(None)):
    """make an image/gif be tripping with weird effects"""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(getedged, byt)
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
            content={"error": "The Image manipulation had a small error"},
        )
@app.post("/api/evil", response_model=Item, responses=rdict)
async def evil(token: str = Header(None), url: str = Header(None)):
    """*Laughs in Sithlord*"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )

@app.post("/api/whyareyougay", response_model=Item, responses=rdict)
async def whyareyougay(token: str = Header(None), url: str = Header(None),url2: str = Header(None)):
    """The why are you gay meme"""

    r = await checktoken(token)
    byta = await getimg(url)
    bytb = await getimg(url2)
    fn = partial(getwhyareyougay,byta,bytb)
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
            content={"error": "The Image manipulation had a small error"},
        )
@app.post("/api/5g1g", response_model=Item, responses=rdict)
async def fourguysonegirl(token: str = Header(None), url: str = Header(None),url2: str = Header(None)):
    """You know the meme, 5 guys surrounding 1 girl"""

    r = await checktoken(token)
    byta = await getimg(url)
    bytb = await getimg(url2)
    fn = partial(get5g1g,byta,bytb)
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
            content={"error": "The Image manipulation had a small error"},
        )
@app.post("/api/blur", response_model=Item, responses=rdict)
async def blur(token: str = Header(None), url: str = Header(None)):
    """Blur an image/gif"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )

@app.post("/api/invert", response_model=Item, responses=rdict)
async def invert(token: str = Header(None), url: str = Header(None)):
    """A fliperroni , swithc the colors of an image/gif"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )


# uvicorn main:app --reload
@app.post("/api/pixel", response_model=Item, responses=rdict)
async def pixel(token: str = Header(None), url: str = Header(None)):
    """Retro 8but version of an image/gif"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )


@app.post("/api/deepfry", response_model=Item, responses=rdict)
async def deepfry(token: str = Header(None), url: str = Header(None)):
    """Deepfry a gif/static image"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )

@app.post("/api/sepia", response_model=Item, responses=rdict)
async def sepia(token: str = Header(None), url: str = Header(None)):
    """Add a cool brown filter on an image/gif"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )


@app.post("/api/wasted", response_model=Item, responses=rdict)
async def wasted(token: str = Header(None), url: str = Header(None)):
    """GTA V Wasted screen on any image/gif"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )
@app.post("/api/triggered", response_model=Item, responses=rdict)
async def triggered(token: str = Header(None), url: str = Header(None)):
    """GTA V Wasted screen on any image/gif"""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(gettriggered, byt)
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
            content={"error": "The Image manipulation had a small error"},
        )

@app.post("/api/jail", response_model=Item, responses=rdict)
async def jail(token: str = Header(None), url: str = Header(None)):
    """Put someone behind bars"""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(getjail, byt)
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
            content={"error": "The Image manipulation had a small error"},
        )


@app.post("/api/gay", response_model=Item, responses=rdict)
async def gay(token: str = Header(None), url: str = Header(None)):
    """Pride flag on any image/gif. Show some love <3"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )

@app.post("/api/charcoal", response_model=Item, responses=rdict)
async def charcoal(token: str = Header(None), url: str = Header(None)):
    """Turn an image/gif into an artistic sketch"""

    r = await checktoken(token)
    byt = await getimg(url)
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
            content={"error": "The Image manipulation had a small error"},
        )
@app.get("/api/wtp")
async def whosethatpokemon( token: str = Header(None)):
    """Get a full whose that pokemon response"""
    r = await checktoken(token)
    rst = str((random.randint(1, 800)))
    if len(rst) == 3:
        r = str(rst)
    elif len(rst) == 2:
        r = '0' + str(rst)
    else:
        r = '00' + str(rst)
    path = "/pokemon"
    if os.path.exists(f'{rst}q.png'):
        with open('assets/pokemons.json', 'r') as file:
            cont = json.load(file)
            mondict = cont[rst]
    else:
        print(f'https://assets.pokemon.com/assets/cms2/img/pokedex/full/{r}.png')
        byt = await getimg(f'https://assets.pokemon.com/assets/cms2/img/pokedex/full/{r}.png')
        fn = partial(getwtp,byt,rst)
        mondict = await loop.run_in_executor(None, fn)
    return JSONResponse(status_code=200,content={"question_image":f'https://dagpi.tk/pokemon/{rst}q.png',"answer_image":f'https://dagpi.tk/pokemon/{rst}a.png',"pokemon":mondict})

# @app.get('/api/pokemonimage')
# async def getmon(token: str = Header(None), search:str = Header(None)):
#     async with aiofiles.open('assets/pokemons.json',mode='r') as file:
#         st = await file.read()
#         js = json.loads(st)
#     try:
#         mon = js[search]
#     except:
#         try:
#             for key in js:
#                 if js[key]['name'].lower() == search.lower():
#                     mon = js[key]
#                 else:
#                     continue
#         except:
            #raise

@app.post("/api/meme", response_model=Item, responses=rdict,include_in_schema=False)
async def meme(
        token: str = Header(None), url: str = Header(None), text: str = Header(None)
):
    """Generate a meme by supplying the top joke and the template.Supports both gif and static images."""

    r = await checktoken(token)
    byt = await getimg(url)
    fn = partial(memegen, byt,text)
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
            content={"error": "The Image manipulation had a small error"},
        )
@app.post("/api/retromeme", response_model=Item, responses=rdict,include_in_schema=False)
async def retromeme(
        token: str = Header(None), url: str = Header(None), text: str = Header(None)
):
    """Generate a meme by supplying the top joke and the template.Supports both gif and static images."""

    r = await checktoken(token)
    byt = await getimg(url)
    meme = Meme(text)
    fn = partial(meme.make_meme, byt)
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
            content={"error": "The Image manipulation had a small error"},
        )
@app.post('/gettoken',include_in_schema=False)
async def gettokenpls(enhancedtoken: str = Header(None),userid : int = Header(None)):
    y = await checkenhcanced(enhancedtoken)
    stat,tok = tkc.gettoken(userid)
    if stat:
        return JSONResponse(status_code=200, content={'token': tok})
    else:
        return JSONResponse(status_code=500, content={'error': 'We were unable to find a tokenfrom that userid'})


@app.post('/tokenapply',include_in_schema=False)
async def tokenapply(enhancedtoken: str = Header(None),userid : int = Header(None)):
    y = await checkenhcanced(enhancedtoken)
    stat, co = tkc.adduser(userid)
    if stat == True:
        return JSONResponse(status_code=200, content={'token': co})
    elif stat == False:
        if co == 1:
            tok = tkc.gettoken(userid)
            return JSONResponse(status_code=200, content={'User aldready exists': co})
        else:
            return JSONResponse(status_code=500, content={'error': 'we were unable to insert your token'})

@app.get('/tokenlist',include_in_schema=False)
async def userstats(enhancedtoken: str = Header(None)):
    y = await checkenhcanced(enhancedtoken)
    stats = tkc.getstats()
    return JSONResponse(status_code=200,content={'data':stats})
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


async def main():
    while True:
        tkc.resetlimits()
        await asyncio.sleep(60)


loop = asyncio.get_event_loop()
task = loop.create_task(main())
try:
    task
except asyncio.CancelledError:
    pass
