"""
This module defines the cost.
"""


class Cost:
    """Cost model class.

    Args:
        cost (int): The coin cost.

    Attributes:
        __cost (int): The coin cost.

    Examples:
        Can compare between Costs or add.

        >>> a = Cost(3)
        >>> b = Cost(5)
        >>> a < b
        True
        >>> a + b
        Cost(8)
    """
    def __init__(self, cost):
        self.__cost = cost

    @classmethod
    def str2cost(self, cost_str: str):
        """
        Create cost instance with string.

        Args:
            cost_str (str): Cost string.

        Returns:
            Cost: Cost instance.
        """
        cost = 0
        if cost_str.isdigit():
            cost = int(cost_str)
        return Cost(cost)

    @property
    def cost(self):
        """
        The coin cost.
        """
        return self.__cost

    def __eq__(self, other):
        if not isinstance(other, Cost):
            raise NotImplementedError
        return self.cost == other.cost

    def __lt__(self, other):
        if not isinstance(other, Cost):
            raise NotImplementedError
        return self.cost < other.cost

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        if not isinstance(other, Cost):
            raise NotImplementedError
        return self.cost > other.cost

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __str__(self):
        sub_s = str(self.cost)
        return sub_s

    def __add__(self, other):
        return Cost(
            self.cost + other.cost
        )

    def __sub__(self, other):
        return Cost(
            self.cost - other.cost
        )

    def __mul__(self, other: int):
        return Cost(
            self.cost * other
        )
