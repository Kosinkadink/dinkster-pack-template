"""Exercise plain values and the real worker; doctor remains a separate gate."""

from pathlib import Path

from dinkster_engine.testing import load_pack

import my_pack
from my_pack import NODES, Shout


def test_shout() -> None:
    assert NODES == [Shout]
    assert Shout.define_schema().node_type == "my-pack.shout"
    assert Shout.execute(text="Hello there", times=3) == {
        "shouted": "HELLO THERE!HELLO THERE!HELLO THERE!"
    }
    assert Shout.execute(text="Hi") == {"shouted": "HI!"}
    assert Shout.execute(text="No repetitions", times=0) == {"shouted": ""}


def test_worker_graph_values_and_cache() -> None:
    manifest = Path(my_pack.__file__).with_name("dinkster-pack.toml")
    with load_pack(manifest) as pack:
        graph = {
            "first": ("my-pack.shout", {"text": "Hi there", "times": 2}),
            "second": ("my-pack.shout", {"text": pack.link("first", "shouted"), "times": 3}),
        }
        first = pack.run(graph)
        assert first.value("first", "shouted") == "HI THERE!HI THERE!"
        assert first.value("second", "shouted") == (
            "HI THERE!HI THERE!!HI THERE!HI THERE!!HI THERE!HI THERE!!"
        )
        assert first.executed == {"first", "second"}
        assert first.cached == set()
        again = pack.run(graph)
        assert again.outputs == first.outputs
        assert again.executed == set()
        assert again.cached == {"first", "second"}
