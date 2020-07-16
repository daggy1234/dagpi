import aiosqlite
import random


class logogame:
    def __init__(self):

        with open('assets/filelist.txt', 'r') as file:
            c = file.readlines()
            self.st = [e.replace('\n', '') for e in c]

    async def makepool(self):
        self.db = await aiosqlite.connect('assets/logodata.db')
        self.cursor = await self.db.cursor()

    async def crafthint(self, text):
        l = text.split(' ')
        if len(l) == 1:
            psub = len(text) // 2
            wl = list(text)
            for i in range(0, psub):
                r = random.randint(1, len(text))-1
                if wl[r] != '_':
                    wl[r] = '_'
                    i += 1

        else:
            wl = []
            for word in l:
                psub = len(word) // 2
                j = 0
                charsdone = []
                wla = list(word)
                for i in range(0, psub):
                    r = random.randint(1, len(word)) -1
                    if wla[r] != '_':
                        wla[r] = '_'
                        i += 1

                wl.append(''.join(wla) + ' ')
        mst = ''.join(wl)
        return mst

    async def getdata(self, duct):
        search = str(duct['brand']).lower()
        try:
            print('umm')
            await self.cursor.execute('SELECT * FROM LOGOS WHERE lower(NAME) LIKE $1;', (search,))
            print('umm')
            row = await self.cursor.fetchall()
            print(row)
            print('umm')
            duct['hint'] = (row[0][10].split(',')[1])
            duct['clue'] = (row[0][13])
            duct['easy'] = True
        except:
            duct['hint'] = await self.crafthint(search)
            duct['easy'] = False
        return (duct)

    async def craftdata(self):
        p = random.choice(self.st)
        scon = []
        f = p.replace('.png', '')
        for i in range(0, len(f)):
            if p[i] == '_':
                scon.append(i + 1)
            i += 1
        br = f[scon[1]:]
        if f.endswith('_a'):
            quest = p
            ans = f[:-2] + '_b.png'
            br = br.replace('_a', '')
        elif f.endswith('_b'):
            quest = p
            ans = f[:-2] + '_a.png'

            br = br.replace('_b', '')
        elif f.endswith('_o'):
            quest = f[:-2] + '.png'
            ans = p
            br = br.replace('_o', '')
        else:
            quest = p
            ans = f + '_o.png'
        burl = 'https://logoassetsgame.s3.us-east-2.amazonaws.com/logogame/logos/'
        aurl = burl + ans
        qurl = burl + quest
        toret = {}
        if ans in self.st:
            toret['answer'] = aurl
        toret['question'] = qurl
        if br.startswith('b_'):
            br = br[2:]
        toret['brand'] = br.replace('_', ' ').title()
        toret['wiki_url'] = 'https://en.wikipedia.org/wiki/' + toret['brand']
        return (await self.getdata(toret))