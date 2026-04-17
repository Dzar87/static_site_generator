from enum import Enum
import re
from typing import Sequence

from htmlnode import HTMLNode, LeafNode


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


IMAGE_RE = re.compile(r"!\[(?P<alt>[^\[\]]*)\]\((?P<src>[^\(\)]*)\)")
IMAGE_SPLIT_RE = re.compile(r"!\[[^\[\]]*\]\([^\(\)]*\)")
LINK_RE = re.compile(r"(?<!!)\[(?P<value>[^\[\]]*)\]\((?P<href>[^\[\]]*)\)")
LINK_SPLIT_RE = re.compile(r"(?<!!)\[[^\[\]]*\]\([^\[\]]*\)")
HEADING_PREFIX_RE = re.compile(r"^#{1,6}\s.*$")
QUOTE_PREFIX_RE = re.compile(r"^>\s?.*$")
NUMBER_PREFIX_RE = re.compile(r"^(?P<n>\d+)\.\s.*$")

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


def split_nodes_delimiter(
    old_nodes: Sequence[TextNode], delimiter: str, text_type: TextType
) -> Sequence[TextNode]:
    new_nodes: Sequence[TextNode] = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT or delimiter not in node.text:
            new_nodes.append(node)
            continue
        split_nodes = node.text.split(delimiter)
        if not len(split_nodes) % 2:
            raise ValueError(f"uneven '{delimiter}'. node: {node}")
        for idx, split_node in enumerate(split_nodes):
            if not split_node:
                continue
            if idx % 2:
                new_nodes.append(TextNode(split_node, text_type))
                continue
            new_nodes.append(TextNode(split_node, TextType.TEXT))
    return new_nodes


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    extracted: list[tuple[str, str]] = []
    for match in IMAGE_RE.finditer(text):
        extracted.append((match["alt"], match["src"]))
    return extracted


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    extracted: list[tuple[str, str]] = []
    for match in LINK_RE.finditer(text):
        extracted.append((match["value"], match["href"]))
    return extracted


def split_nodes_link(old_nodes: Sequence[TextNode]) -> Sequence[TextNode]:
    extracted: list[TextNode] = []
    for node in old_nodes:
        links = extract_markdown_links(node.text)
        if not links:
            extracted.append(node)
            continue

        # Create the link nodes
        link_nodes = [TextNode(i[0], TextType.LINK, url=i[1]) for i in links]

        # Split the current node
        split_node = re.split(LINK_SPLIT_RE, node.text)

        # use zip to retain order
        for text, link in zip(split_node, link_nodes):
            if text != "":
                extracted.append(TextNode(text, TextType.TEXT))
            extracted.append(link)

        # split_node will always be larger than image_nodes
        if (last_text := split_node[-1]) != "":
            extracted.append(TextNode(last_text, TextType.TEXT))

    return extracted

def split_nodes_image(old_nodes: Sequence[TextNode]) -> Sequence[TextNode]:
    extracted: list[TextNode] = []
    for node in old_nodes:
        images = extract_markdown_images(node.text)
        if not images:
            extracted.append(node)
            continue

        # Create the image nodes
        image_nodes = [TextNode(i[0], TextType.IMAGE, url=i[1]) for i in images]

        # Split the current node
        split_node = re.split(IMAGE_SPLIT_RE, node.text)

        # use zip to retain order
        for text, image in zip(split_node, image_nodes):
            if text != "":
                extracted.append(TextNode(text, TextType.TEXT))
            extracted.append(image)

        # split_node will always be larger than image_nodes
        if (last_text := split_node[-1]) != "":
            extracted.append(TextNode(last_text, TextType.TEXT))
    return extracted


def text_to_textnodes(text: str) -> Sequence[TextNode]:
    result = [TextNode(text, TextType.TEXT)]
    result = split_nodes_image(result)
    result = split_nodes_link(result)
    result = split_nodes_delimiter(result, "**", TextType.BOLD)
    result = split_nodes_delimiter(result, "_", TextType.ITALIC)
    result = split_nodes_delimiter(result, "`", TextType.CODE)
    return result


def markdown_to_blocks(markdown: str) -> Sequence[str]:
    return [s for i in markdown.split("\n\n") if (s := i.strip())]


def block_to_block_type(block: str) -> BlockType:
    if HEADING_PREFIX_RE.match(block):
        return BlockType.HEADING
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    if all([QUOTE_PREFIX_RE.match(line) for line in block.split("\n")]):
        return BlockType.QUOTE
    if all([line.startswith("- ") for line in block.split("\n")]):
        return BlockType.UNORDERED_LIST
    if block.startswith("1. "):
        for idx, line in enumerate(block.split("\n"), start=1):
            if (match := re.match(NUMBER_PREFIX_RE, line)) and int(match["n"]) == idx:
                continue
            break
        else:
            return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH
