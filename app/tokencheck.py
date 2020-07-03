import pandas as pd
import random
import string
from tabulate import tabulate


class tokenprocess(object):
    def __init__(self):
        print("class inited lmao")

    def checkenhanced(self, token):
        df = pd.read_csv("tokens.csv")
        l = df.loc[(df.token == token) & (df.enhanced == 1)]
        print(l)
        if l.empty:
            return False
        else:
            return True

    def randomword(self, length):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits

        st = "".join(random.choice(letters) for i in range(length))
        print(st)
        return st

    def validtoken(self, token):
        df = pd.read_csv("tokens.csv")
        l = df.loc[(df.token == token)]
        if l.empty:
            return False,1
        else:
            rt = df[df.token == token].uses
            if int(rt) >= 60:
                return False,2
            df.loc[(df.token == token), "uses"] += 1
            df.loc[(df.token == token), "totaluses"] += 1
            df.to_csv("tokens.csv", index=False)
            return True,0

    def showtokens(self):
        df = pd.read_csv("tokens.csv")
        print(tabulate(df.head(), tablefmt="psql"))

    def deluser(self, userid):
        tkst = self.randomword(64)
        df = pd.read_csv("tokens.csv")
        if userid in df["userid"].tolist():
            newdf = df[df.userid != userid]
            newdf.to_csv("tokens.csv", index=False)
            return True
        else:
            return (False, 1)
    def getstats(self):
        df = pd.read_csv('tokens.csv')
        return (df.shape)
    def adduser(self, userid):
        tkst = self.randomword(64)
        df = pd.read_csv("tokens.csv")
        if userid not in df["userid"].tolist():
            newdf = df.append(
                {"token": tkst, "uses": 0, "userid": userid, "enhanced": 0},
                ignore_index=True,
            )
            newdf.to_csv("tokens.csv", index=False)
            return True,tkst
        else:
            return False, 1

    def resetlimits(self):
        df = pd.read_csv("tokens.csv")
        df.loc[df.uses != 0, "uses"] = 0
        df.to_csv("tokens.csv", index=False)
        return True


# #
# y = tokenprocess()
# try:
#     y.resetlimits()
# except:
#     print('error')
