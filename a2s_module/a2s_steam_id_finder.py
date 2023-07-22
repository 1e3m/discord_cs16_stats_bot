from valve.steam.id import SteamID

async def get_steam_id_from_url(url):
    return SteamID.from_community_url(url)

# validation input steam_id from user
async def chek_steam_id(steam_id) -> bool:
    url = SteamID.community_url(steam_id)
    if(url is not None):
        return True
    return False


