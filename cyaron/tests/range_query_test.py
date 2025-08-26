import unittest
import random
from cyaron.query import *
from cyaron.vector import *


def valid_query(l, r, mode: RangeQueryRandomMode, limits) -> bool:
    if len(l) != len(r) or len(l) != len(limits):
        return False
    dimension = len(l)
    for i in range(dimension):
        cur_limit = limits[i]
        if isinstance(cur_limit, int):
            cur_limit = (1, cur_limit)
        elif len(limits[i]) == 1:
            cur_limit = (1, cur_limit[0])
        if l[i] > r[i] or (l[i] == r[i] and mode == RangeQueryRandomMode.LESS):
            return False
        if not (cur_limit[0] <= l[i] <= r[i] <= cur_limit[1]):
            return False
    return True


TEST_LEN = 20000


class TestRangeQuery(unittest.TestCase):

    def test_allow_equal_v1(self):
        limits = [154, 220, 1]
        qs = RangeQuery.random(TEST_LEN, limits)
        self.assertEqual(len(qs), TEST_LEN)
        for i in range(TEST_LEN):
            self.assertTrue(
                valid_query(qs[i][0], qs[i][1],
                            RangeQueryRandomMode.ALLOW_EQUAL, limits))
            self.assertTrue(qs[i][2] == ())

    def test_allow_equal_v2_throw(self):
        limits = [(147, 154), (51, 220), (5, 4)]  # 5 > 4
        self.assertRaises(ValueError,
                          lambda: RangeQuery.random(TEST_LEN, limits))

    def test_allow_equal_v2_no_throw(self):
        limits = [(147, 154), (51, 220),
                  (4, 4)]  # 4 == 4 and mode == ALLOW_EQUAL, should not throw
        qs = RangeQuery.random(TEST_LEN, limits)
        self.assertEqual(len(qs), TEST_LEN)
        for i in range(TEST_LEN):
            self.assertTrue(
                valid_query(qs[i][0], qs[i][1],
                            RangeQueryRandomMode.ALLOW_EQUAL, limits))
            self.assertTrue(qs[i][2] == ())

    def test_less_v1(self):
        limits = [154, 220, 2]
        qs = RangeQuery.random(TEST_LEN,
                               limits,
                               mode=RangeQueryRandomMode.LESS)
        self.assertEqual(len(qs), TEST_LEN)
        for i in range(TEST_LEN):
            self.assertTrue(
                valid_query(qs[i][0], qs[i][1], RangeQueryRandomMode.LESS,
                            limits))
            self.assertTrue(qs[i][2] == ())

    def test_less_v1_throw(self):
        limits = [154, 220, 1]
        self.assertRaises(
            ValueError, lambda: RangeQuery.random(
                TEST_LEN, limits, mode=RangeQueryRandomMode.LESS))

    def test_less_v2_throw_g(self):
        limits = [(147, 154), (51, 220), (5, 4)]  # 5 > 4
        self.assertRaises(
            ValueError, lambda: RangeQuery.random(
                TEST_LEN, limits, mode=RangeQueryRandomMode.LESS))

    def test_less_v2_throw_eq(self):
        limits = [(147, 154), (51, 220),
                  (4, 4)]  # 4 == 4 and mode == LESS, should throw
        self.assertRaises(
            ValueError, lambda: RangeQuery.random(
                TEST_LEN, limits, mode=RangeQueryRandomMode.LESS))

    def test_less_v2_no_throw(self):
        limits = [(147, 154), (51, 220), (4, 5)]
        qs = RangeQuery.random(TEST_LEN,
                               limits,
                               mode=RangeQueryRandomMode.LESS)
        self.assertEqual(len(qs), TEST_LEN)
        for i in range(TEST_LEN):
            self.assertTrue(
                valid_query(qs[i][0], qs[i][1], RangeQueryRandomMode.LESS,
                            limits))
            self.assertTrue(qs[i][2] == ())

    def test_weight(self):

        def weight_gen(i, l, r):
            ret = pow(114514, i, 19260817)
            self.assertEqual(len(l), len(r))
            for j in range(len(l)):
                ret = (ret + l[j] * r[j] * 3301) % 19260817
            return ret

        limits = [(147, 154), (51, 220), (4, 5)]
        for i in range(len(limits)):
            if limits[i][0] > limits[i][1]:
                limits[i] = limits[i][1], limits[i][0]
        qs = RangeQuery.random(TEST_LEN, limits, weight_generator=weight_gen)
        i = 1
        for l, r, w in qs.result:
            self.assertTrue(
                valid_query(l, r, RangeQueryRandomMode.ALLOW_EQUAL, limits))
            self.assertEqual(w, weight_gen(i, l, r))
            i += 1
