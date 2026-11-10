"""Exercise nodes over plain values; the doctor runs as a separate gate."""

from maple_text import NODES, Shout


def test_shout() -> None:
    assert NODES == [Shout]
    assert Shout.define_schema().node_type == "maple-text.shout"
    assert Shout.execute(text="Hello there", times=3) == {
        "shouted": "HELLO THERE!HELLO THERE!HELLO THERE!"
    }
    assert Shout.execute(text="Hi") == {"shouted": "HI!"}
    assert Shout.execute(text="No repetitions", times=0) == {"shouted": ""}
