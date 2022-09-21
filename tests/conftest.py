"""
Implement pytest fixtures for the tests.
"""

import pytest

@pytest.fixture
def test_data(tmp_path):
    """
    Return a temporary directory with test data
    """
    data = """1 -303 101
2 -205 130
3 -120 148
4 -35 159
5 38 164
6 144 165
7 241 154
8 323 136
9 390 103
10 452 57
11 488 9
12 474 -48
13 443 -111
14 404 -147
15 350 -181
16 278 -216
17 248 -234
18 178 -261
19 112 -272
20 37 -293
21 -30 -309
22 -77 -315
23 -132 -315
24 -194 -312
25 -245 -304
26 -318 -296
27 -385 -275
28 0 0
29 0 0
30 -566 0
31 -387 87
32 352 126
33 486 -1
34 455 -89
35 68 -275
36 -339 -11
37 -341 -44
38 3 -91
39 -10 -205
    """
    d = tmp_path / "data"
    d.mkdir()
    f = d / "test_data.txt"
    f.write_text(data)
    return f
