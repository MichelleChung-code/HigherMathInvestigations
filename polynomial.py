import unittest
from cmath import exp, pi


class BasicPolynomial:
    def __init__(self, dc_powers, v='x'):
        """
        Args:
            dc_powers: dictionary of coefficients and powers
            v: which string variable to use
        """
        self.v = v

        # remove 0's
        self.dc_powers = {p: c for p, c in dc_powers.items() if c != 0}

        # change floats to ints if possible
        self.dc_powers = {p: int(c) if int(c) == c else c for p, c in self.dc_powers.items()}

    def __call__(self, x):
        ans = 0
        for p, c in self.dc_powers.items():
            ans += c * (x**p)
        return ans

    def q_eval(self, t, debug=False):
        q = exp(pi*t*complex(0, 1))
        if debug:
            print(q)
        if abs(q.imag) < 1e-14:
            return self.__call__(q.real)
        return self.__call__(q)

    def __add__(self, other):
        dc = self.dc_powers.copy()
        for p, c in other.dc_powers.items():
            dc[p] = dc.get(p, 0) + c
        if self.v != other.v:
            raise Warning('variable type not consistent')
        return BasicPolynomial(dc, self.v)

    def __sub__(self, other):
        dc = self.dc_powers.copy()
        for p, c in other.dc_powers.items():
            dc[p] = dc.get(p, 0) - c
        if self.v != other.v:
            raise Warning('variable type not consistent')
        return BasicPolynomial(dc, self.v)

    def __mul__(self, other):
        if isinstance(other, BasicPolynomial):
            dc = dict()
            for p1, c1 in self.dc_powers.items():
                for p2, c2 in other.dc_powers.items():
                    p = p1 + p2
                    c = c1*c2
                    dc[p] = c + dc.get(p, 0)
            if self.v != other.v:
                raise Warning('variable type not consistent')

        elif isinstance(other, (int, float)):
            dc = {p: c*other for p, c in self.dc_powers.items()}
        else:
            raise NotImplementedError(type(other))
        return BasicPolynomial(dc, self.v)

    def __pow__(self, power, modulo=None):
        if not isinstance(power, int):
            raise NotImplementedError('Non-Integer power')
        if power == 0:
            return 1
        elif power < 0:
            return NotImplementedError('Negative power')
        elif power == 1:
            return self
        else:
            ans = self
            for i in range(power-1):
                ans *= self
            return ans

    def __eq__(self, other):
        if self.is_constant() and isinstance(other, (int, float)):
            return self.dc_powers.get(1, 0) == other
        return self.dc_powers == other.dc_powers

    def is_constant(self):
        return len(set(self.dc_powers.keys()) - {0}) == 0

    def __str__(self):
        """
        This method returns the string representation of the object. This method is called when print() or str()
        function is invoked on an object.
        This method must return the String object. If we don’t implement __str__() function for a class,
        then built-in object implementation is used that actually calls __repr__() function.
        """
        ret = ''
        for p in sorted(self.dc_powers):
            c = self.dc_powers[p]
            if len(ret) != 0:
                if c > 0:
                    ret += ' + '
                else:
                    ret += ' - '
            if abs(c) == 1:
                if p == 1:
                    ret += self.v
                elif p == 0:
                    ret += '{}'.format(abs(c))
                elif p < 0:
                    if p == -1:
                        ret += '1/{}'.format(self.v)
                    else:
                        ret += '1/{}^{}'.format(self.v, abs(p))
                else:
                    ret += '{}^{}'.format(self.v, p)
            else:
                if p == 1:
                    ret += '{}{}'.format(abs(c), self.v)
                elif p == 0:
                    ret += '{}'.format(abs(c))
                elif p < 0:
                    if p == -1:
                        ret += '{}/{}'.format(abs(c), self.v)
                    else:
                        ret += '{}/{}^{}'.format(abs(c), self.v, abs(p))
                else:
                    ret += '{}{}^{}'.format(abs(c), self.v, p)

        return ret

    def __repr__(self):
        """
        Python __repr__() function returns the object representation.
        It could be any valid python expression such as tuple, dictionary, string etc.
        This method is called when repr() function is invoked on the object, in that case, __repr__()
        function must return a String otherwise error will be thrown.
        """
        return str(self.dc_powers)

    __rmul__ = __mul__

    def degree(self):
        return max(self.dc_powers.keys())


class TestPolynomial(unittest.TestCase):

    def test_custom_polynomial(self):
        poly_x = BasicPolynomial({1: 1})  # f(x) = x
        poly_2 = BasicPolynomial({0: 2, 1: -1, 3: 1})  # f(x) = 2 - x + x^3
        poly_3 = BasicPolynomial({-1: -3, 0: 2, 1: -1})  # f(x) = -3/x + 2 - x
        with self.subTest('call x'):
            for i in range(10):
                self.assertEqual(poly_x(i), i)
        with self.subTest('addition'):
            self.assertEqual(BasicPolynomial({0: 2, 3: 1}), poly_x + poly_2)
        with self.subTest('subtraction'):
            self.assertEqual(poly_3 - poly_3, 0)
        with self.subTest('call x for poly 3'):
            f = lambda x: -3/x + 2 - x
            for i in range(1, 10):
                self.assertAlmostEqual(poly_3(i), f(i))
        with self.subTest('string'):
            self.assertEqual(str(poly_3), '3/x + 2 - x')
        with self.subTest('simple multiplication'):
            # x*(2 - x + x^3) = 2x - x^2 + x^4
            self.assertEqual(BasicPolynomial({1: 2, 2: -1, 4: 1}), poly_x*poly_2)
        with self.subTest('multiplication'):
            # (-3/x + 2 - x)*(2 - x + x^3) = -6/x + 7 -4x - 2x^2 +2x^3 - x^4
            self.assertEqual(BasicPolynomial({-1: -6, 0: 7, 1: -4, 2: -2, 3: 2, 4: -1}), poly_3*poly_2)
        with self.subTest('q_eval t=0'):  # t=0 -> q=1
            # -3/x + 2 - x -> -3 + 2 -1 = -2
            self.assertEqual(-2, poly_3.q_eval(0, debug=True))
            # 2 - x + x^3 -> 2 - 1 + 1 = 2
            self.assertEqual(2, poly_2.q_eval(0, debug=True))
        with self.subTest('q_eval t=1'):  # t=1 -> q=-1
            # -3/x + 2 - x -> 3 + 2 +1 = 6
            self.assertEqual(6, poly_3.q_eval(1, debug=True))
            # 2 - x + x^3 -> 2 + 1 - 1 = 2
            self.assertEqual(2, poly_2.q_eval(1, debug=True))
        with self.subTest('power'):
            self.assertEqual(BasicPolynomial({5: 1}), poly_x**5)
