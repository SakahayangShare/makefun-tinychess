import sys
import os

import main

def test_perft():
    pos = main.Position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    p1 = pos.perft(1)
    p2 = pos.perft(2)
    p3 = pos.perft(3)
    print(f"Start perft: 1={p1}, 2={p2}, 3={p3}")
    assert p1 == 20, f"Start d1: {p1}"
    assert p2 == 400, f"Start d2: {p2}"
    assert p3 == 8902, f"Start d3: {p3}"
    print("Starting position perft(1..3) passed!")

    kiwi = main.Position("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1")
    kp1 = kiwi.perft(1)
    kp2 = kiwi.perft(2)
    kp3 = kiwi.perft(3)
    print(f"Kiwipete perft: 1={kp1}, 2={kp2}, 3={kp3}")
    assert kp1 == 48, f"Kiwipete d1: {kp1}"
    assert kp2 == 2039, f"Kiwipete d2: {kp2}"
    assert kp3 == 97862, f"Kiwipete d3: {kp3}"
    print("Kiwipete position perft(1..3) passed!")

if __name__ == "__main__":
    test_perft()
    print("ALL TESTS PASSED!")
