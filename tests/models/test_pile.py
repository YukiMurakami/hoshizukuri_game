from hoshizukuri_game.models.pile import (
    Pile, PileType
)
from hoshizukuri_game.models.card import Card


class TestPile:
    def test_pile_number(self):
        pile = Pile(PileType.NUMBER, card_id_and_count=[10, 2])
        assert pile.pile_card_id == 10
        assert pile.count == 2

    def test_pile_list(self):
        card_list = [
            Card(card_id=2, uniq_id=1),
            Card(card_id=2, uniq_id=2),
            Card(card_id=3, uniq_id=3),
        ]
        pile = Pile(PileType.LIST, card_list=card_list)
        assert pile.pile_card_id == 2
        assert pile.count == 3

    def test_pile_listlist(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        assert pile.pile_card_id == 2
        assert pile.count == 4

    def test_str_number(self):
        pile = Pile(PileType.NUMBER, card_id_and_count=[10, 2])
        assert str(pile) == "{10:2}"

    def test_str_list(self):
        card_list = [
            Card(card_id=2, uniq_id=1),
            Card(card_id=2, uniq_id=2),
            Card(card_id=3, uniq_id=3),
        ]
        pile = Pile(PileType.LIST, card_list=card_list)
        assert str(pile) == "[2-1,2-2,3-3]"

    def test_str_listlist(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        assert str(pile) == "[[2-1],[2-2,2-3,3-4]]"

    def test_push_1(self):
        card_list = [
            Card(card_id=2, uniq_id=1),
            Card(card_id=2, uniq_id=2),
            Card(card_id=3, uniq_id=3),
        ]
        pile = Pile(PileType.LIST, card_list=card_list)
        card = Card(card_id=7, uniq_id=4)
        pile.push(card)
        assert pile.pile_card_id == 2
        assert pile.count == 4
        assert str(pile) == "[2-1,2-2,3-3,7-4]"

    def test_push_2(self):
        pile = Pile(PileType.NUMBER, card_id_and_count=[8, 3])
        card = Card(card_id=8, uniq_id=1)
        pile.push(card)
        assert str(pile) == "{8:4}"

    def test_push_3(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        card = Card(card_id=7, uniq_id=4)
        pile.push(card)
        assert pile.pile_card_id == 2
        assert pile.count == 5
        assert str(pile) == "[[2-1],[2-2,2-3,3-4],[7-4]]"

    def test_index_1(self):
        pile = Pile(PileType.LIST, card_list=[
            Card(1, 2), Card(1, 3), Card(1, 4),
            Card(2, 5), Card(2, 6), Card(3, 7)
        ])
        assert pile.index(card_id=2) == 3

    def test_index_2(self):
        pile = Pile(PileType.LIST, card_list=[
            Card(1, 2), Card(1, 3), Card(1, 4),
            Card(2, 5), Card(2, 6), Card(3, 7)
        ])
        assert pile.index(uniq_id=3) == 1

    def test_index_3(self):
        pile = Pile(PileType.LIST, card_list=[
            Card(1, 2), Card(1, 3), Card(1, 4),
            Card(2, 5), Card(2, 6), Card(3, 7)
        ])
        assert pile.index(card_id=8) == -1

    def test_index_4(self):
        pile = Pile(PileType.LIST, card_list=[
            Card(1, 2), Card(1, 3), Card(1, 4),
            Card(2, 5), Card(2, 6), Card(3, 7)
        ])
        assert pile.index(uniq_id=10) == -1

    def test_index_5(self):
        pile = Pile(PileType.NUMBER, card_id_and_count=[2, 8])
        assert pile.index(card_id=2) == -1

    def test_index_6(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        assert pile.index(uniq_id=4) == 1

    def test_index_7(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        assert pile.index(uniq_id=5) == -1

    def test_index_8(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        assert pile.index(card_id=2) == 0

    def test_index_9(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        assert pile.index(card_id=5) == -1

    def test_insert_1(self):
        card_list = [
            Card(card_id=2, uniq_id=1),
            Card(card_id=2, uniq_id=2),
            Card(card_id=3, uniq_id=3),
        ]
        pile = Pile(PileType.LIST, card_list=card_list)
        card = Card(card_id=7, uniq_id=4)
        pile.insert(card, 1)
        assert pile.pile_card_id == 2
        assert pile.count == 4
        assert str(pile) == "[2-1,7-4,2-2,3-3]"

    def test_insert_2(self):
        pile = Pile(PileType.NUMBER, card_id_and_count=[8, 3])
        card = Card(card_id=8, uniq_id=1)
        pile.insert(card, 1)
        assert str(pile) == "{8:4}"

    def test_insert_3(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        card = Card(card_id=8, uniq_id=1)
        pile.insert(card, 2, 0)
        assert str(pile) == "[[2-1],[2-2,2-3,3-4],[8-1]]"
        assert pile.count == 5

    def test_insert_4(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        card = Card(card_id=8, uniq_id=1)
        pile.insert(card, 1, 2)
        assert str(pile) == "[[2-1],[2-2,2-3,8-1,3-4]]"
        assert pile.count == 5

    def test_insert_5(self):
        card_list = [
            Card(card_id=2, uniq_id=1),
            Card(card_id=2, uniq_id=2),
            Card(card_id=3, uniq_id=3),
        ]
        pile = Pile(PileType.LIST, card_list=card_list)
        card = Card(card_id=7, uniq_id=4)
        pile.insert(card, -1)
        assert pile.pile_card_id == 2
        assert pile.count == 4
        assert str(pile) == "[2-1,2-2,3-3,7-4]"

    def test_insert_6(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        card = Card(card_id=8, uniq_id=1)
        pile.insert(card, -1, -1)
        assert str(pile) == "[[2-1],[2-2,2-3,3-4],[8-1]]"
        assert pile.count == 5

    def test_insert_7(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        card = Card(card_id=8, uniq_id=1)
        pile.insert(card, 1, -1)
        assert str(pile) == "[[2-1],[2-2,2-3,3-4,8-1]]"
        assert pile.count == 5

    def test_remove_at_1(self):
        card_list = [
            Card(card_id=2, uniq_id=1),
            Card(card_id=2, uniq_id=2),
            Card(card_id=3, uniq_id=3),
        ]
        pile = Pile(PileType.LIST, card_list=card_list)
        pile.remove_at(1)
        assert str(pile) == "[2-1,3-3]"
        assert pile.count == 2

    def test_remove_at_2(self):
        card_list = [
            Card(card_id=2, uniq_id=1),
        ]
        pile = Pile(PileType.LIST, card_list=card_list)
        pile.remove_at(0)
        assert str(pile) == "[]"
        assert pile.count == 0

    def test_remove_at_3(self):
        pile = Pile(PileType.NUMBER, card_id_and_count=[8, 4])
        pile.remove_at(1)
        assert str(pile) == "{8:3}"
        assert pile.count == 3

    def test_remove_at_4(self):
        pile = Pile(PileType.NUMBER, card_id_and_count=[8, 1])
        pile.remove_at(0)
        assert str(pile) == "{8:0}"
        assert pile.count == 0

    def test_remove_at_5(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        pile.remove_at(1, 1)
        assert str(pile) == "[[2-1],[2-2,3-4]]"
        assert pile.count == 3

    def test_remove_at_6(self):
        card_list = [
            [
                Card(card_id=2, uniq_id=1),
            ],
            [
                Card(card_id=2, uniq_id=2),
                Card(card_id=2, uniq_id=3),
                Card(card_id=3, uniq_id=4),
            ]
        ]
        pile = Pile(PileType.LISTLIST, card_list=card_list)
        pile.remove_at(0, 0)
        assert str(pile) == "[[2-2,2-3,3-4]]"
        assert pile.count == 3

    def test_get_card_1(self):
        pile = Pile(PileType.LIST, card_list=[Card(1, 1), Card(1, 2)])
        assert pile.get_card(2).id == 1
        assert pile.get_card(3) is None
