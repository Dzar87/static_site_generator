from typing import Self


class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: list[Self] | None = None,
        props: dict[str, str] | None = None,
    ) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self) -> str:
        raise NotImplementedError

    def props_to_html(self) -> str:
        if self.props is None:
            return ""
        return " ".join([f"{k}={v}" for k, v in self.props.items()])

    def __repr__(self) -> str:
        result: list[str] = []
        for attr in ("tag", "value", "children", "props"):
            if (v := getattr(self, attr)) is None:
                continue
            if attr == "props":
                v = self.props_to_html()
            if isinstance(v, str):
                result.append(f"{attr}: '{v}'")
            else:
                result.append(f"{attr}: {v}")
        return f"HTMLNode({", ".join(result)})"
