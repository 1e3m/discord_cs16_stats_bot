import urllib.request, json
from texttable import Texttable
import config 

from fuzzywuzzy import fuzz
from fuzzywuzzy import process


cNick = 1
cPlace = 25
cAUTHID = 2
cFrags = 16
cDeath = 17
cHeadshots = 18
cTeamkills = 19
cShots = 4
cHits = 5
cDamage = 6
cSuicide = 20
cDefusing = 7
cDefuse = 21
cPlanted = 8
cExplore = 22
cSkill = 24

class Player:
    def __init__(self, place, nick, frags, deaths, headshots, teamkill, shots, hits, damage, suicide, defusing, defuse, planted, explore, skill):
        self.place = place
        self.nick = nick.replace('&gt;','>').replace('&lt;','<')
        self.frags = frags
        self.deaths = deaths
        self.headshots = headshots
        self.teamkill = teamkill
        self.shots = shots
        self.hits = hits
        self.damage = damage
        self.suicide = suicide
        self.defusing = defusing
        self.defuse = defuse
        self.planted = planted
        self.explore = explore
        self.KD = frags/(1 if deaths == 0 else deaths)
        self.acurary = '{:.2f}'.format(((hits/shots)*100)) + '%'
        self.skill = skill

    def toString(self):
         t_block = "\t\t\t\t\t" if len(self.nick) <= 7 else "\t\t\t\t"
         t_block = t_block if len(self.nick) <= 15 else "\t\t"
         return f'{self.place}\t{self.nick}' + t_block + f'{self.frags}\t{self.deaths}\t{self.headshots}\t{self.teamkill}\t{self.shots}\t{self.hits}\t{self.damage}\t{self.suicide}\t{self.defusing}\t\t{self.defuse}\t{self.planted}\t{self.explore}'

#N = 15

cvar = [0,200,800,1500,3500,4500,5500,8000,10000,11000,12000,13000,17000]


def getSkill(skill):
    if skill >= cvar[0]  and skill < cvar[1]:
        user_skill = "Lm"
    elif (skill >= cvar[1] and skill < cvar[2]):
        user_skill = "L"
    elif (skill >= cvar[2]  and skill < cvar[3]):
        user_skill = "Lp"
    elif (skill >= cvar[3]  and skill < cvar[4]):
        user_skill = "Mm"
    elif (skill >= cvar[4]  and skill < cvar[5]):
        user_skill = "M"
    elif(skill >= cvar[5]  and skill < cvar[6]):
        user_skill = "Mp"
    elif (skill >= cvar[6]  and skill < cvar[7]):
        user_skill = "Hm"
    elif(skill >= cvar[7]  and skill < cvar[8]):
        user_skill = "H"
    elif (skill >= cvar[8]  and skill < cvar[9]):
        user_skill = "Hp"
    elif(skill >= cvar[9]  and skill < cvar[10]):
        user_skill = "Pm"
    elif (skill >= cvar[10] and skill < cvar[11]):
        user_skill = "P"
    elif (skill >= cvar[11] and skill < cvar[12]):
        user_skill = "Pp";
    elif (skill >= cvar[12]):
        user_skill = "G";
    else:
        user_skill = "Lm";	
    return user_skill

def getSkillEmoji(skill):
    if skill >= cvar[0]  and skill < cvar[1]:
        user_skill = "🅻-"
    elif (skill >= cvar[1] and skill < cvar[2]):
        user_skill = "🅻"
    elif (skill >= cvar[2]  and skill < cvar[3]):
        user_skill = "🅻+"
    elif (skill >= cvar[3]  and skill < cvar[4]):
        user_skill = "🅼-"
    elif (skill >= cvar[4]  and skill < cvar[5]):
        user_skill = "🅼"
    elif(skill >= cvar[5]  and skill < cvar[6]):
        user_skill = "🅼+"
    elif (skill >= cvar[6]  and skill < cvar[7]):
        user_skill = "🅷-"
    elif(skill >= cvar[7]  and skill < cvar[8]):
        user_skill = "🅷"
    elif (skill >= cvar[8]  and skill < cvar[9]):
        user_skill = "🅷+"
    elif(skill >= cvar[9]  and skill < cvar[10]):
        user_skill = "🅿-"
    elif (skill >= cvar[10] and skill < cvar[11]):
        user_skill = "🅿"
    elif (skill >= cvar[11] and skill < cvar[12]):
        user_skill = "🅿+";
    elif (skill >= cvar[12]):
        user_skill = "🅶";
    else:
        user_skill = "🅻-";  
    return user_skill



async def get_table_stats(N):
    with urllib.request.urlopen(config.URL) as request:
        data = json.load(request)
        players = []
        for x in data:
            players.append(Player(x[0][cPlace],x[0][cNick],x[0][cFrags],x[0][cDeath],x[0][cHeadshots],x[0][cTeamkills],x[0][cShots],x[0][cHits],x[0][cDamage],x[0][cSuicide],x[0][cDefusing],x[0][cDefuse],x[0][cPlanted],x[0][cExplore],x[0][cSkill]))
        players.sort(key=lambda x: x.place)

        table = Texttable()
        table.set_cols_align(["l", "c", "r", "r", "r", "r", "r", "r", "r", "r"])
        table.set_cols_valign(["i", "t", "i", "i", "i", "i", "i", "i", "t", "t"])
        table.set_deco(Texttable.HEADER)
        pp = [['Место','Ник','Фраги','Смерти','В голову','k/d','Попадания','Урон','Точность','Скилл']]
        table.set_cols_width([5, 25, 10, 10, 10, 10, 10, 10, 10, 10])  
        for p in players[N-10:N]:
            pp.append([p.place,p.nick,p.frags,p.deaths,p.headshots,p.KD,p.hits,p.damage, p.acurary, getSkillEmoji(p.skill) + f'({p.skill})'])
        table.add_rows(pp)        
        return table.draw()
        #print(table.draw())

async def get_table_player(nick, hadrFind = False):
    with urllib.request.urlopen(config.URL) as request:
        data = json.load(request)
        players = []
        players_names = []
        search_player = ""
        
        if(hadrFind == False):
            for x in data:
                players_names.append(x[0][cNick])

            search_player = process.extractOne(nick, players_names)

            if search_player[1] < 45:
                return 0
            search_player = search_player[0]
        else:
            search_player = nick
        
        for x in data:
            if(search_player == x[0][cNick].replace('&gt;','>').replace('&lt;','<').strip()):
                players.append(Player(x[0][cPlace],x[0][cNick],x[0][cFrags],x[0][cDeath],x[0][cHeadshots],x[0][cTeamkills],x[0][cShots],x[0][cHits],x[0][cDamage],x[0][cSuicide],x[0][cDefusing],x[0][cDefuse],x[0][cPlanted],x[0][cExplore],x[0][cSkill]))

        print(players)
        if(len(players) == 0):
            return 0;

        table = Texttable()
        table.set_cols_align(["l", "c", "r", "r", "r", "r", "r", "r", "r", "r"])
        table.set_cols_valign(["i", "t", "i", "i", "i", "i", "i", "i", "t", "t"])
        table.set_deco(Texttable.HEADER)
        pp = [['Место','Ник','Фраги','Смерти','В голову','k/d','Попадания','Урон','Точность','Скилл']]
        table.set_cols_width([5, 25, 10, 10, 10, 10, 10, 10, 10, 10])


        for p in players:           
            pp.append([p.place,p.nick,p.frags,p.deaths,p.headshots,p.KD,p.hits,p.damage, p.acurary, getSkillEmoji(p.skill) + f'({p.skill})'])
        table.add_rows(pp)        
        return table.draw()
        
#get_table_stats()
