url = 'https://dagbotapi.herokuapp.com/api/sepia'
headers = {'url':'','token':'atMoMn2Pg3EUmZ065QBvdJN4IcjNxCQRMv1oZTZWg98i7HelIdvJwHtZFKPgCtf'}
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