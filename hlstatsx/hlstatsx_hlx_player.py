class HlxPlayer():
    def __init__(self, player_rank, player_id, connection_time, name, flag, country, skill, kills, deaths, kill_deaths, headshots, headshot_percent, acuracy, activity, last_skill_change):
        self.player_rank = player_rank
        self.player_id = player_id
        self.connection_time = connection_time
        self.name = name
        self.flag = flag
        self.country = country
        self.skill = skill
        self.kills = kills
        self.deaths = deaths
        self.kill_deaths = kill_deaths
        self.headshots = headshots
        self.headshot_percent = headshot_percent
        self.acuracy = acuracy
        self.activity = activity
        self.last_skill_change= last_skill_change

    @classmethod
    def shortPlayer(cls, nick):
        return cls(None,None,None,nick,None,None,None,None,None,None,None,None,None,None,None)

    def toString(self):
         return f'rank: {self.player_rank}, skill: {self.skill}, name: {self.name}, k/d: {self.kill_deaths}'