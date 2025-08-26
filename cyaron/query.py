"""
This module provides a `RangeQuery` class for generating queries
based on limits of each dimension.

Classes:
    RangeQueryRandomMode: Enum to control how random range endpoints are generated.
    RangeQuery: A class for generating random queries.
    
Usage:
    n = randint(1, 10)
    q = randint(1, 10)
    Q = RangeQuery.random(q, [(1, n)])
    io.input_writeln(Q)
"""

import random
from enum import IntEnum
from typing import Optional, Union, Tuple, List, Callable, TypeVar, overload, Generic, Any, Sequence

from .utils import list_like


class RangeQueryRandomMode(IntEnum):
    """Control how random range endpoints are generated for range queries."""
    LESS = 0  # disallow l = r
    ALLOW_EQUAL = 1  # allow l = r


WeightT = TypeVar('WeightT', bound=Tuple[Any, ...])


class RangeQuery(Generic[WeightT], Sequence[Tuple[List[int], List[int],
                                                  WeightT]]):
    """A class for generating random queries."""
    result: List[Tuple[List[int], List[int], WeightT]]  # Vector L, R, weights.

    def __init__(self):
        self.result = []

    def __len__(self):
        return len(self.result)

    @overload
    def __getitem__(self, item: int) -> Tuple[List[int], List[int], WeightT]:
        ...

    @overload
    def __getitem__(self,
                    item: slice) -> List[Tuple[List[int], List[int], WeightT]]:
        ...

    def __getitem__(self, item: Union[int, slice]):
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
        The string contains all the queries with l and r (and w if generated) in a row, splits with "\\n".
        """
        res = ''
        for l, r, w in self.result:
            l_to_str = [str(x) for x in l]
            r_to_str = [str(x) for x in r]
            w_to_str = [str(x) for x in w]
            res += ' '.join(l_to_str) + ' ' + ' '.join(r_to_str)
            if len(w_to_str) > 0:
                res += ' ' + ' '.join(w_to_str)
            res += '\n'
        return res[:-1]  # remove the last '\n'

    @staticmethod
    @overload
    def random(
        num: int = 1,
        position_range: Optional[Sequence[Union[int, Tuple[int, int]]]] = None,
        *,
        mode: RangeQueryRandomMode = RangeQueryRandomMode.ALLOW_EQUAL,
        weight_generator: None = None,
        big_query: float = 0.2,
    ) -> "RangeQuery[Tuple[()]]":
        ...

    @staticmethod
    @overload
    def random(
        num: int = 1,
        position_range: Optional[Sequence[Union[int, Tuple[int, int]]]] = None,
        *,
        mode: RangeQueryRandomMode = RangeQueryRandomMode.ALLOW_EQUAL,
        weight_generator: Callable[[int, List[int], List[int]], WeightT],
        big_query: float = 0.2,
    ) -> "RangeQuery[WeightT]":
        ...

    @staticmethod
    def random(
        num: int = 1,
        position_range: Optional[Sequence[Union[int, Tuple[int, int]]]] = None,
        *,
        mode: RangeQueryRandomMode = RangeQueryRandomMode.ALLOW_EQUAL,
        weight_generator: Optional[Callable[[int, List[int], List[int]],
                                            WeightT]] = None,
        big_query: float = 0.2,
    ):
        """
        Generate `num` random queries with dimension limit.
        Args:
            num: the number of queries
            position_range: a list of limits for each dimension
                single number x represents range [1, x]
                list [x, y] or tuple (x, y) represents range [x, y]
            mode: the mode queries generate, see Enum Class RangeQueryRandomMode
            weight_generator: A function that generates the weights for the queries. It should:
                - Take the index of query (starting from 1), starting and ending positions as input.
                - Return a list of weights of any length.
            big_query: a float number representing the probability for generating big queries.
        """
        ret = RangeQuery()

        for i in range(num):
            ret.result.append(
                RangeQuery.get_one_query(position_range,
                                         big_query=big_query,
                                         mode=mode,
                                         weight_generator=weight_generator,
                                         index=i + 1))
        return ret

    @staticmethod
    @overload
    def get_one_query(
            position_range: Optional[Sequence[Union[int, Tuple[int,
                                                               int]]]] = None,
            *,
            big_query: float = 0.2,
            mode: RangeQueryRandomMode = RangeQueryRandomMode.ALLOW_EQUAL,
            weight_generator: None = None,
            index: int = 1) -> Tuple[List[int], List[int], Tuple[()]]:
        ...

    @staticmethod
    @overload
    def get_one_query(
            position_range: Optional[Sequence[Union[int, Tuple[int,
                                                               int]]]] = None,
            *,
            big_query: float = 0.2,
            mode: RangeQueryRandomMode = RangeQueryRandomMode.ALLOW_EQUAL,
            weight_generator: Callable[[int, List[int], List[int]], WeightT],
            index: int = 1) -> Tuple[List[int], List[int], WeightT]:
        ...

    @staticmethod
    def get_one_query(
            position_range: Optional[Sequence[Union[int, Tuple[int,
                                                               int]]]] = None,
            *,
            big_query: float = 0.2,
            mode: RangeQueryRandomMode = RangeQueryRandomMode.ALLOW_EQUAL,
            weight_generator: Optional[Callable[[int, List[int], List[int]],
                                                WeightT]] = None,
            index: int = 1):
        """
        Generate a pair of query lists (query_l, query_r, w) based on the given position ranges and mode.
        Args:
            position_range (Optional[List[Union[int, Tuple[int, int]]]]): A list of position ranges. Each element can be:
                - An integer, which will be treated as a range from 1 to that integer.
                - A tuple of two integers, representing the lower and upper bounds of the range.
            mode (RangeQueryRandomMode): The mode for generating the queries. It can be:
                - RangeQueryRandomMode.allow_equal: Allow the generated l and r to be equal.
                - RangeQueryRandomMode.less: Ensure that l and r are not equal.
            weight_generator: A function that generates the weights for the queries. It should:
                - Take the index of query (starting from 1), starting and ending positions as input.
                - Return a list of weights of any length.
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
            pr = position_range[i]
            if isinstance(pr, int):
                cur_range = (1, pr)
            elif len(pr) == 1:
                cur_range = (1, pr[0])
            else:
                cur_range = pr

            if cur_range[0] > cur_range[1]:
                raise ValueError(
                    "upper-bound should be larger than lower-bound")
            if mode == RangeQueryRandomMode.LESS and cur_range[0] == cur_range[
                    1]:
                raise ValueError(
                    "mode is set to less but upper-bound is equal to lower-bound"
                )

            if random.random() < big_query:
                # Generate a big query
                cur_l = cur_range[1] - cur_range[0] + 1
                lb = max(2 if mode == RangeQueryRandomMode.LESS else 1,
                         cur_l // 2)
                ql = random.randint(lb, cur_l)
                l = random.randint(cur_range[0], cur_range[1] - ql + 1)
                r = l + ql - 1
            else:
                l = random.randint(cur_range[0], cur_range[1])
                r = random.randint(cur_range[0], cur_range[1])
                # Expected complexity is O(1)
                # We can use random.sample, But it's actually slower according to benchmarks.
                while mode == RangeQueryRandomMode.LESS and l == r:
                    l = random.randint(cur_range[0], cur_range[1])
                    r = random.randint(cur_range[0], cur_range[1])
                if l > r:
                    l, r = r, l

            query_l.append(l)
            query_r.append(r)
        if weight_generator is None:
            return (query_l, query_r, ())
        return (query_l, query_r, weight_generator(index, query_l, query_r))
