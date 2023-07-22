from valve.steam.id import SteamID

async def get_steam_id_from_url(url):
    """get steam id from premalink url, example: https://steamcommunity.com/profiles/765XXXXXXXXXXXXX"""
    return SteamID.from_community_url(url)


async def chek_steam_id(steam_id) -> bool:
    """validation input steam_id from user"""
    url = SteamID.community_url(steam_id)
    if(url is not None):
        return True
    return False


