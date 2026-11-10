"""A minimal Dinkster text node."""

from __future__ import annotations

from collections.abc import Mapping

from dinkster_api.v1 import InputSpec, Node, NodeSchema, OutputSpec, TypeExpr


class Shout(Node):
    """Uppercase and repeat a string."""

    @classmethod
    def define_schema(cls) -> NodeSchema:
        return NodeSchema(
            node_type="maple-text.shout",
            display_name="Shout",
            category="text",
            description="Uppercase the text and repeat it.",
            inputs=(
                InputSpec("text", TypeExpr.concrete("STRING")),
                InputSpec("times", TypeExpr.concrete("INT"), required=False, default=1),
            ),
            outputs=(OutputSpec("shouted", TypeExpr.concrete("STRING")),),
        )

    @classmethod
    def execute(cls, *, text: str, times: int = 1) -> Mapping[str, object]:
        return cls.outputs(shouted=(text.upper() + "!") * times)


NODES = [Shout]
