from models.f_rivals.recap import RivalsGamePostGameInfo
from models.f_rivals.upcoming import RivalsGamePreGameInfo
from client import Client
from services import rivals_recap_api



def build_post_game_info(client: Client, rpgi: RivalsGamePreGameInfo, game_slug:str) -> RivalsGamePostGameInfo:
    game_result = rivals_recap_api.get_rivals_game_result( client, game_slug)
    #rpgi.away_lineup[0].cap_score
    #result = RivalsGamePostGameInfo(
    #    game_id=game_id,
    #    my_lineup=None,
    #    opp_lineup=None
    #)

    return None