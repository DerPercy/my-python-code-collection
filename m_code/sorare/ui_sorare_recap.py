import api_schema
from context import value_aggregator,hash_map


class UICompetition():
    api_competition: api_schema.Competition
    va: value_aggregator.MyValueAggregator
    def __init__(self,comp:api_schema.Competition ) -> None:
        self.api_competition = comp
        self.va = value_aggregator.MyValueAggregator()

    def name(self):
        return self.api_competition.value_displayName
    
    def num_games(self) -> int:
        return self.va.count()
    def win_percentage(self) -> int:
        return int(self.va.get_average())
    
    def set_result(self, won:bool):
        if won:
            self.va.add_value(100)
        else:
            self.va.add_value(0)
class UIGame():
    game:api_schema.FootballRivalsGame
    def __init__(self, game: api_schema.FootballRivalsGame) -> None:
        self.game = game
    def name(self):
        return self.game.value_slug
    def competition(self):
        return self.game.value_game.value_competition.value_displayName
    
    def won(self) -> bool:
        return self.game.value_myPointsDelta > 0
class UISorareRecap():
    games_list:list[api_schema.FootballRivalsGame]
    competitions: hash_map.MyHashMap[UICompetition]
    def __init__(self, games_list:list[api_schema.FootballRivalsGame]) -> None:
        self.competitions = hash_map.MyHashMap()
        self.games_list = []
        for game in games_list:
            if game.value_myPointsDelta != None:
                comp:UICompetition = self.competitions.get_item(str(game.value_game.value_competition.value_slug))
                if comp == None:
                    comp = UICompetition(game.value_game.value_competition)
                    self.competitions.set_item(k=str(game.value_game.value_competition.value_slug),v=comp)
                comp.set_result(UIGame(game).won())
                self.games_list.append(game)

    def games(self) -> list[UIGame]:
        result:list[UIGame] = []
        for game in self.games_list:
            result.append(UIGame(game))
        return result
    def get_competitions(self) -> list[UICompetition]:
        return self.competitions.item__list()