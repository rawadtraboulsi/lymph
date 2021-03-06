import re
import unittest

import mock

from lymph.testing.mock_helpers import MockMixins


class DummyTestCase(unittest.TestCase, MockMixins):

    def runTest(self):
        pass


class RPCMockHelperTests(unittest.TestCase):

    def setUp(self):
        self.dummy_case = DummyTestCase()

    def test_single_call_match(self):
        self.dummy_case._assert_equal_calls(
            [mock.call('func', 1, foo='bar')],
            [mock.call('func', 1, foo='bar')]
        )

    def test_single_call_different_name(self):
        with self.assertRaisesRegexp(AssertionError, "function #0 name doesn't match, expected 'func2' actual 'func1'"):
            self.dummy_case._assert_equal_calls(
                [mock.call('func1', 1)],
                [mock.call('func2', 1)]
            )

    def test_single_call_args_mismatch(self):
        with self.assertRaisesRegexp(AssertionError, re.compile("function #0 argument #0 doesn't match.*", re.DOTALL)):
            self.dummy_case._assert_equal_calls(
                [mock.call('func', 1, foo='bar')],
                [mock.call('func', 102, foo='bar')]
            )

    def test_single_call_keyword_value_mismatch(self):
        with self.assertRaisesRegexp(AssertionError, re.compile("function #0 keyword argument 'foo' doesn't match.*", re.DOTALL)):
            self.dummy_case._assert_equal_calls(
                [mock.call('func', 1, foo='foobar')],
                [mock.call('func', 1, foo='bar')]
            )

    def test_single_call_keyword_name_mismatch(self):
        with self.assertRaisesRegexp(AssertionError, "function #0 keyword arguments doesn't match, expected \['something'\] actual \['foo'\]"):
            self.dummy_case._assert_equal_calls(
                [mock.call('func', 1, foo='bar')],
                [mock.call('func', 1, something='bar')]
            )

    def test_single_call_keyword_different_count(self):
        with self.assertRaisesRegexp(AssertionError, "function #0 keyword arguments doesn't match, expected \['bar', 'foo'\] actual \['foo'\]"):
            self.dummy_case._assert_equal_calls(
                [mock.call('func', 1, foo='bar')],
                [mock.call('func', 1, foo='bar', bar='taz')]
            )

    def test_single_call_argument_different_count(self):
        with self.assertRaisesRegexp(AssertionError, "function #0 arguments count doesn't match, expected 1 actual 2"):
            self.dummy_case._assert_equal_calls(
                [mock.call('func', 1, 2)],
                [mock.call('func', 1)]
            )

    def test_multiple_call_match(self):
        self.dummy_case._assert_equal_calls(
            [
                mock.call('func', 1, foo='foo'),
                mock.call('func', 2, foo='bar'),
                mock.call('func', 3, foo='foobar')
            ],
            [
                mock.call('func', 1, foo='foo'),
                mock.call('func', 2, foo='bar'),
                mock.call('func', 3, foo='foobar')
            ],
        )

    def test_assert_equal_any_call_success(self):
        self.dummy_case._assert_equal_any_calls(
            [
                mock.call('func1', 1, foo='foo'),
                mock.call('func2', 2, foo='bar'),
                mock.call('func3', 3, foo='foobar')
            ],
            [
                mock.call('func2', 2, foo='bar'),
                mock.call('func3', 3, foo='foobar')
            ],
        )

    def test_assert_equal_any_call_success_with_no_expect(self):
        self.dummy_case._assert_equal_any_calls(
            [
                mock.call('func1', 1, foo='foo'),
                mock.call('func2', 2, foo='bar'),
                mock.call('func3', 3, foo='foobar')
            ],
            [],
        )

    def test_assert_equal_any_call_fail_with_possible_matches(self):
        with self.assertRaisesRegexp(AssertionError, "Call 'call\('func10', 3, foo='foobar'\)' wasn't found."):
            self.dummy_case._assert_equal_any_calls(
                [
                    mock.call('func1', 1, foo='foo'),
                    mock.call('func2', 2, foo='bar'),
                    mock.call('func3', 3, foo='foobar')
                ],
                [
                    mock.call('func10', 3, foo='foobar')
                ],
            )

    def test_assert_equal_any_call_fail_with_no_match(self):
        with self.assertRaisesRegexp(AssertionError, re.compile("Call 'call\('func2', 3, foo='foo'\)' wasn't found. Maybe you want:.*?", re.DOTALL)):
            self.dummy_case._assert_equal_any_calls(
                [
                    mock.call('func2', 1, foo='foo'),
                    mock.call('func2', 2, foo='bar'),
                    mock.call('func2', 3, foo='foobar')
                ],
                [
                    mock.call('func2', 3, foo='foo')
                ],
            )

    def test_assert_equal_any_call_fail_with_no_match_better_message(self):
        with self.assertRaisesRegexp(AssertionError, re.compile("function #0 keyword argument 'foo' doesn't match*?", re.DOTALL)):
            self.dummy_case._assert_equal_any_calls(
                [
                    mock.call('func1', 2, foo='bar'),
                    mock.call('func2', 3, foo='foobar')
                ],
                [
                    mock.call('func2', 3, foo='foo')
                ],
            )

    def test_assert_equal_any_call_fail_with_wrong_order(self):
        with self.assertRaisesRegexp(AssertionError, re.compile("Call 'call\('func2', 2, foo='bar'\)' wasn't found.", re.DOTALL)):
            self.dummy_case._assert_equal_any_calls(
                [
                    mock.call('func1', 1, foo='foo'),
                    mock.call('func2', 2, foo='bar'),
                    mock.call('func3', 3, foo='foobar')
                ],
                [
                    mock.call('func3', 3, foo='foobar'),
                    mock.call('func2', 2, foo='bar')
                ],
            )
