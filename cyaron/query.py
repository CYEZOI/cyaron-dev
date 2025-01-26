"""
This module provides a `RangeQuery` class for generating queries
based on limits of each dimension.

Classes:
    RangeQuery: A class for generating random queries.
    
Usage:
    n = randint(1, 10)
    q = randint(1, 10)
    Q = Query.random(q, [(1, n)])
"""

import random
from enum import IntEnum
from typing import Optional, Union, Tuple, List

from .utils import list_like


class RangeQueryRandomMode(IntEnum):
    less = 0  # disallow l = r
    allow_equal = 1  # allow l = r


class RangeQuery:
    """A class for generating random queries."""
    result: List[Tuple[List[int], List[int]]]

    def __init__(self):
        self.result = []

    def __len__(self):
        return len(self.result)

    def __getitem__(self, item):
        return self.result[item]

    def __str__(self):
        """__str__(self) -> str
            Return a string to output the queries. 
            The string contains all the queries with l and r in a row, splits with "\\n".
        """
        return self.to_str()

    def to_str(self):
        """
        Return a string to output the queries. 
        The string contains all the queries with l and r in a row, splits with "\\n".
        """
        res = ''
        for l, r, in self.result:
            l_to_str = [str(x) for x in l]
            r_to_str = [str(x) for x in r]
            res += ' '.join(l_to_str) + ' ' + ' '.join(r_to_str) + '\n'
        return res[:-1]  # remove the last '\n'

    @staticmethod
    def random(
        num: int = 1,
        position_range: Optional[List[Union[int, Tuple[int, int]]]] = None,
        mode: RangeQueryRandomMode = RangeQueryRandomMode.allow_equal,
    ):
        """
        Generate `num` random queries with dimension limit.
        Args:
            num: the number of queries
            position_range: a list of limits for each dimension
                single number x represents range [1, x]
                list [x, y] or tuple (x, y) represents range [x, y]
            mode: the mode queries generate, see Enum Class RangeQueryRandomMode
        """
        if position_range is None:
            position_range = [10]

        ret = RangeQuery()

        if not list_like(position_range):
            raise TypeError("the 2nd param must be a list or tuple")

        for _ in range(num):
            ret.result.append(RangeQuery.get_one_query(position_range, mode))
        return ret

    @staticmethod
    def get_one_query(
        position_range: Optional[List[Union[int, Tuple[int, int]]]] = None,
        mode: RangeQueryRandomMode = RangeQueryRandomMode.allow_equal,
    ) -> Tuple[List[int], List[int]]:
        """
        Generate a pair of query lists (query_l, query_r) based on the given position ranges and mode.
        Args:
            position_range (Optional[List[Union[int, Tuple[int, int]]]]): A list of position ranges. Each element can be:
                - An integer, which will be treated as a range from 1 to that integer.
                - A tuple of two integers, representing the lower and upper bounds of the range.
            mode (RangeQueryRandomMode): The mode for generating the queries. It can be:
                - RangeQueryRandomMode.allow_equal: Allow the generated l and r to be equal.
                - RangeQueryRandomMode.less: Ensure that l and r are not equal.
        Returns:
            Tuple[List[int], List[int]]: A tuple containing two lists:
                - query_l: A list of starting positions.
                - query_r: A list of ending positions.
        Raises:
            ValueError: If the upper-bound is smaller than the lower-bound.
            ValueError: If the mode is set to less but the upper-bound is equal to the lower-bound.
        """
        if position_range is None:
            position_range = [10]

        dimension = len(position_range)
        query_l: List[int] = []
        query_r: List[int] = []
        for i in range(dimension):
            cur_range: Tuple[int, int]
            if isinstance(position_range[i], int):
                cur_range = (1, position_range[i])
            elif len(position_range[i]) == 1:
                cur_range = (1, position_range[i][0])
            else:
                cur_range = position_range[i]

            if cur_range[0] > cur_range[1]:
                raise ValueError(
                    "upper-bound should be larger than lower-bound")
            if mode == RangeQueryRandomMode.less and cur_range[0] == cur_range[
                    1]:
                raise ValueError(
                    "mode is set to less but upper-bound is equal to lower-bound"
                )

            if mode == RangeQueryRandomMode.less:
                l, r = random.sample(range(cur_range[0], cur_range[1] + 1), 2)
            else:  # mode == RangeQueryRandomMode.allow_equal
                l = random.randint(cur_range[0], cur_range[1])
                r = random.randint(cur_range[0], cur_range[1])
            if l > r:
                l, r = r, l
            query_l.append(l)
            query_r.append(r)
        return (query_l, query_r)
