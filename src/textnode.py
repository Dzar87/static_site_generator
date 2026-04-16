from enum import Enum

from htmlnode import HTMLNode, LeafNode

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str | None = None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TextNode):
            return (
                self.text == other.text
                and self.text_type == other.text_type
                and self.url == other.url
            )
        return False

    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node: TextNode) -> HTMLNode:
    value: LeafNode
    if text_node.text_type == TextType.TEXT:
        value = LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        value = LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        value = LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        value = LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        value = LeafNode("a", text_node.text, props={"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        props = {"src": text_node.url, "alt": text_node.text}
        value = LeafNode("img", "", props=props)
    else:
        raise ValueError("unknown TextType")
    return value
