from context import lineup_ranking

def test_lineup_ranking():
    players = [
        lineup_ranking.Player(entity_data="A",position="G",cap_score=50,score=50),
        lineup_ranking.Player(entity_data="B",position="G",cap_score=51,score=51.1),
        lineup_ranking.Player(entity_data="C",position="D",cap_score=52,score=52),
        lineup_ranking.Player(entity_data="D",position="D",cap_score=53,score=53),
        lineup_ranking.Player(entity_data="E",position="D",cap_score=54,score=54),
        lineup_ranking.Player(entity_data="F",position="D",cap_score=55,score=55),
        lineup_ranking.Player(entity_data="G",position="M",cap_score=56,score=56),
        lineup_ranking.Player(entity_data="H",position="M",cap_score=40,score=57),
        lineup_ranking.Player(entity_data="I",position="M",cap_score=45,score=58),
        lineup_ranking.Player(entity_data="J",position="M",cap_score=46,score=59),
        lineup_ranking.Player(entity_data="K",position="F",cap_score=34,score=60),
        lineup_ranking.Player(entity_data="L",position="F",cap_score=50,score=61),
        lineup_ranking.Player(entity_data="M",position="F",cap_score=43,score=62),
        lineup_ranking.Player(entity_data="N",position="F",cap_score=46,score=63),       
    ]

    result = lineup_ranking.calculate_best_lineup(players,220)
    assert 1 == 0
