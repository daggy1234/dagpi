url = 'http://dagpi.tk/api/quote'
headers = {'url':'https://media.discordapp.net/attachments/381963689470984203/722043865527484416/unknown.png','token':'sexytoken123#','name':'daggy','text':'testing a tweet lmao'}
import requests
from io import BytesIO
from PIL import Image,ImageSequence
r = requests.post(url,headers=headers)
print(r.status_code)
print('hmmmm')


print('eval')
cont = r.content
io = BytesIO(cont)
io.seek(0)
print('io dones')
try:
    with Image.open(io) as t:
        for frame in ImageSequence.Iterator(t):
            frame.show()
except:
    print(r.text)
# io = BytesIO(cont)
# io.seek(0)
# print('reading contents')
# try:
#     with Image.open(io) as t:
#         print('bytes done')
#         print(t.mode)
#         t.save('good.gif')
# except:
#     print(r.text)
#     print('error')