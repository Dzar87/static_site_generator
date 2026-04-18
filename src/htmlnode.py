from abc import ABC, abstractmethod
from typing import MutableSequence

class Node(ABC):

    @abstractmethod
    def to_html(self) -> str: ...


class HTMLNode(Node):
    repr_attrs: tuple[str, ...] = ("tag", "value", "children", "props")

    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: MutableSequence["HTMLNode"] | None = None,
        props: dict[str, str | None] | None = None,
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
        for attr in self.repr_attrs:
            if (v := getattr(self, attr)) is None:
                continue
            if attr == "props":
                v = self.props_to_html()
            if isinstance(v, str):
                result.append(f"{attr}: '{v}'")
            else:
                result.append(f"{attr}: {v}")
        return f"{self.__class__.__name__}({', '.join(result)})"


class LeafNode(HTMLNode):
    repr_attrs = ("tag", "value", "props")

    def __init__(
        self,
        tag: str | None,
        value: str | None,
        props: dict[str, str | None] | None = None,
    ) -> None:
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self) -> str:
        if self.value is None:
            raise ValueError("all leaf nodes must have a value")
        if not self.tag:
            return self.value
        return f"<{self.tag}>{self.value}</{self.tag}>"


class ParentNode(HTMLNode):
    repr_attrs = ("tag", "children", "props")

    def __init__(
        self,
        tag: str | None,
        children: MutableSequence[HTMLNode] | None,
        props: dict[str, str | None] | None = None,
    ) -> None:
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("tag not initialised")
        if self.children is None:
            raise ValueError("children not initialised")
        result = [f"<{self.tag}>"]
        for child in self.children:
            result.append(child.to_html())
        result.append(f"</{self.tag}>")
        return "".join(result)
