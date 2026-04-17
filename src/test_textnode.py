import unittest

from textnode import (
    BlockType,
    TextNode,
    TextType,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    markdown_to_blocks,
    markdown_to_html_node,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_node_to_html_node,
    text_to_textnodes,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self) -> None:
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_text_not_eq(self) -> None:
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is another text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_texttype_not_eq(self) -> None:
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.TEXT)
        self.assertNotEqual(node, node2)

    def test_url_not_eq(self) -> None:
        node = TextNode("This is a text node", TextType.IMAGE, url="http://example.com")
        node2 = TextNode("This is a text node", TextType.IMAGE, url="http://example.test")
        self.assertNotEqual(node, node2)


class TestNodeToHTML(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a bold node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a bold node")

    def test_italic(self):
        node = TextNode("This is an italic node", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is an italic node")

    def test_code(self):
        node = TextNode("This is a code node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a code node")

    def test_link(self):
        node = TextNode("This is a link node", TextType.LINK, url="http://example.test")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a link node")
        self.assertEqual(html_node.props, {"href": "http://example.test"})

    def test_image(self):
        node = TextNode(
            "This is a image node", TextType.IMAGE, url="http://example.test"
        )
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {
                "src": "http://example.test",
                "alt": "This is a image node"
            }
        )


class TestSplitNodeDelimiter(unittest.TestCase):

    def test_delimit_uneven(self) -> None:
        nodes = [TextNode("some text with _uneven delimiter", TextType.TEXT)]
        with self.assertRaises(ValueError):
            split_nodes_delimiter(nodes, "_", TextType.ITALIC)

    def test_delimit_none(self) -> None:
        nodes = [
            TextNode("some text with no delimiter", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        self.assertSequenceEqual(result, nodes)
        self.assertIsNot(result, nodes)

    def test_delimit_text(self) -> None:
        nodes = [
            TextNode("some text with no delimiter", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "_", TextType.TEXT)
        self.assertSequenceEqual(result, nodes)
        self.assertIsNot(result, nodes)

    def test_delimit_bold(self) -> None:
        nodes = [
            TextNode("some text with **bold** delimiter", TextType.TEXT),
        ]
        expected = [
            TextNode("some text with ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" delimiter", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertSequenceEqual(result, expected)
        self.assertIsNot(result, nodes)

    def test_delimit_italic(self) -> None:
        nodes = [
            TextNode("some text with _italic_ delimiter", TextType.TEXT),
        ]
        expected = [
            TextNode("some text with ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" delimiter", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        self.assertSequenceEqual(result, expected)
        self.assertIsNot(result, nodes)

    def test_delimit_code(self) -> None:
        nodes = [
            TextNode("some text with `code` delimiter", TextType.TEXT),
        ]
        expected = [
            TextNode("some text with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" delimiter", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertSequenceEqual(result, expected)
        self.assertIsNot(result, nodes)

    def test_delimit_start(self) -> None:
        nodes = [
            TextNode("**bold** delimiter at the start", TextType.TEXT),
        ]
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode(" delimiter at the start", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertSequenceEqual(result, expected)
        self.assertIsNot(result, nodes)

    def test_delimit_end(self) -> None:
        nodes = [
            TextNode("delimiter at the end **bold**", TextType.TEXT),
        ]
        expected = [
            TextNode("delimiter at the end ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertSequenceEqual(result, expected)
        self.assertIsNot(result, nodes)

    def test_delimit_all(self) -> None:
        nodes = [
            TextNode("some text with no delimiter", TextType.TEXT),
            TextNode("some text with **bold** delimiter", TextType.TEXT),
            TextNode("some text with _italic_ delimiter", TextType.TEXT),
            TextNode("some text with `code` delimiter", TextType.TEXT),
        ]
        expected = [
            TextNode("some text with no delimiter", TextType.TEXT),
            TextNode("some text with ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" delimiter", TextType.TEXT),
            TextNode("some text with ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" delimiter", TextType.TEXT),
            TextNode("some text with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" delimiter", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        result = split_nodes_delimiter(result, "_", TextType.ITALIC)
        result = split_nodes_delimiter(result, "`", TextType.CODE)

        self.assertSequenceEqual(result, expected)
        self.assertIsNot(result, nodes)


class TestExtractMardownImages(unittest.TestCase):

    def test_none(self) -> None:
        text = "Nothing to see here."
        expected = []
        result = extract_markdown_images(text)
        self.assertSequenceEqual(result, expected)

    def test_single(self) -> None:
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif)."
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif")]
        result = extract_markdown_images(text)
        self.assertSequenceEqual(result, expected)

    def test_many(self) -> None:
        text = (
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and "
            "![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        expected = [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]
        result = extract_markdown_images(text)
        self.assertSequenceEqual(result , expected)

    def test_start(self) -> None:
        text = "![rick roll](https://i.imgur.com/aKaOqIh.gif) image at the start."
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif")]
        result = extract_markdown_images(text)
        self.assertSequenceEqual(result , expected)

    def test_end(self) -> None:
        text = "Image at the end ![rick roll](https://i.imgur.com/aKaOqIh.gif)"
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif")]
        result = extract_markdown_images(text)
        self.assertSequenceEqual(result, expected)

    def test_exclude_links(self) -> None:
        text = "This is text with a link [to boot dev](https://www.boot.dev)."
        expected = []
        result = extract_markdown_images(text)
        self.assertSequenceEqual(result, expected)

class TestExtractMardownLinks(unittest.TestCase):
    def test_none(self) -> None:
        text = "Nothing to see here."
        expected = []
        result = extract_markdown_links(text)
        self.assertSequenceEqual(result, expected)

    def test_single(self) -> None:
        text = "This is text with a link [to boot dev](https://www.boot.dev)."
        result = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev")]
        self.assertSequenceEqual(result, expected)

    def test_many(self) -> None:
        text = (
            "This is text with a link [to boot dev](https://www.boot.dev) and "
            "[to youtube](https://www.youtube.com/@bootdotdev)"
        )
        result = extract_markdown_links(text)
        expected = [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertSequenceEqual(result, expected)

    def test_start(self) -> None:
        text = "[to boot dev](https://www.boot.dev) link at the start."
        result = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev")]
        self.assertSequenceEqual(result, expected)

    def test_end(self) -> None:
        text = "link at the end [to boot dev](https://www.boot.dev)"
        result = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev")]
        self.assertSequenceEqual(result, expected)

    def test_exclude_image(self) -> None:
        text = "Image at the end ![rick roll](https://i.imgur.com/aKaOqIh.gif)"
        expected = []
        result = extract_markdown_links(text)
        self.assertSequenceEqual(result, expected)


class TestSplitNodesLink(unittest.TestCase):
    def test_none(self) -> None:
        node = TextNode("Nothing to see here.", TextType.TEXT)
        expected = [TextNode("Nothing to see here.", TextType.TEXT)]
        result = split_nodes_link([node])
        self.assertSequenceEqual(result, expected)

    def test_single(self) -> None:
        node = TextNode(
            "This is text with an [link](https://i.imgur.com/zjjcJKZ.png).",
            TextType.TEXT,
        )
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(".", TextType.TEXT),
        ]
        result = split_nodes_link([node])
        self.assertSequenceEqual(result, expected)

    def test_start(self) -> None:
        node = TextNode(
            "[link](https://i.imgur.com/zjjcJKZ.png) at the start.",
            TextType.TEXT,
        )
        expected = [
            TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" at the start.", TextType.TEXT),
        ]
        result = split_nodes_link([node])
        self.assertSequenceEqual(result, expected)

    def test_end(self) -> None:
        node = TextNode(
            "at the end [link](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        expected = [
            TextNode("at the end ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
        ]
        result = split_nodes_link([node])
        self.assertSequenceEqual(result, expected)

    def test_many(self) -> None:
        node = TextNode(
            "This is text with an [link](https://i.imgur.com/zjjcJKZ.png) and "
            "another [second link](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode("second link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"),
        ]
        new_nodes = split_nodes_link([node])
        self.assertSequenceEqual(new_nodes, expected)

    def test_with_images(self) -> None:
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and "
            "a [link](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        expected = [
            TextNode(
                "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and "
                "a ",
                TextType.TEXT
            ),
            TextNode("link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"),
        ]
        new_nodes = split_nodes_link([node])
        self.assertSequenceEqual(new_nodes, expected)


class TestSplitNodesImages(unittest.TestCase):
    def test_none(self) -> None:
        node = TextNode("Nothing to see here.", TextType.TEXT)
        expected = [TextNode("Nothing to see here.", TextType.TEXT)]
        result = split_nodes_image([node])
        self.assertSequenceEqual(result, expected)

    def test_single(self) -> None:
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png).",
            TextType.TEXT,
        )
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(".", TextType.TEXT),
        ]
        result = split_nodes_image([node])
        self.assertSequenceEqual(result, expected)

    def test_start(self) -> None:
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png) at the start.",
            TextType.TEXT,
        )
        expected = [
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" at the start.", TextType.TEXT),
        ]
        result = split_nodes_image([node])
        self.assertSequenceEqual(result, expected)

    def test_end(self) -> None:
        node = TextNode(
            "at the end ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        expected = [
            TextNode("at the end ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
        ]
        result = split_nodes_image([node])
        self.assertSequenceEqual(result, expected)

    def test_many(self) -> None:
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and "
            "another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode(
                "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
            ),
        ]
        new_nodes = split_nodes_image([node])
        self.assertSequenceEqual(new_nodes, expected)

    def test_with_links(self) -> None:
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and "
            "a [link](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and a [link](https://i.imgur.com/3elNhQu.png)", TextType.TEXT),
        ]
        new_nodes = split_nodes_image([node])
        self.assertSequenceEqual(new_nodes, expected)


class TestTextToTextNodes(unittest.TestCase):

    def test_to_textnodes(self) -> None:
        text = (
            "This is **text** with an _italic_ word and a `code block` and an "
            "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a "
            "[link](https://boot.dev)"
        )
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        result = text_to_textnodes(text)
        self.assertSequenceEqual(result, expected)


class TestMarkdownToBlocks(unittest.TestCase):

    def test_md_to_blocks(self) -> None:
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        expected = [
            "This is **bolded** paragraph",
            "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
            "- This is a list\n- with items",
        ]
        blocks = markdown_to_blocks(md)
        self.assertSequenceEqual(blocks, expected)


class TestBlockToBlockType(unittest.TestCase):

    def test_empty(self) -> None:
        self.assertEqual(block_to_block_type(""), BlockType.PARAGRAPH)

    def test_heading_block_happy(self) -> None:
        blocks = [
            "# heading1",
            "## heading2",
            "### heading3",
            "#### heading3",
            "##### heading5",
            "###### heading6",
        ]
        expected = [BlockType.HEADING] * len(blocks)
        result = [block_to_block_type(b) for b in blocks]
        self.assertListEqual(result, expected)

    def test_heading_block_sad(self) -> None:
        blocks = [
            "heading0",
            "#heading1",
            "##heading2",
            "###heading3",
            "####heading4",
            "#####heading5",
            "######heading6",
            "####### heading7",
        ]
        expected = [BlockType.PARAGRAPH] * len(blocks)
        result = [block_to_block_type(b) for b in blocks]
        self.assertListEqual(result, expected)

    def test_code_block_happy(self) -> None:
        blocks = [
            """```
            some code
            ```""",
        ]
        expected = [BlockType.CODE] * len(blocks)
        result = [block_to_block_type(b) for b in blocks]
        self.assertListEqual(result, expected)

    def test_code_block_sad(self) -> None:
        blocks = [
            """```python
            some code
            ```""",
            """``
            some code
            ```""",
            """```
            some code
            ``""",
        ]
        expected = [BlockType.PARAGRAPH] * len(blocks)
        result = [block_to_block_type(b) for b in blocks]
        self.assertListEqual(result, expected)

    def test_quote_block_happy(self) -> None:
        blocks = [
            ">quote",
            "> quote",
            ">  quote",
            """>quote line1
>line2""",
            """> quote line1
> line2""",
            """> quote line1
>line2""",
            """>quote line1
> line2""",
        ]
        expected = [BlockType.QUOTE] * len(blocks)
        result = [block_to_block_type(b) for b in blocks]
        self.assertListEqual(result, expected)

    def test_quote_block_sad(self) -> None:
        blocks = [
            "quote",
            """>quote line1
line2""",
            """> quote line2
line2""",
            """quote line1
>line2""",
            """quote line1
> line2""",
        ]
        expected = [BlockType.PARAGRAPH] * len(blocks)
        result = [block_to_block_type(b) for b in blocks]
        self.assertListEqual(result, expected)

    def test_unordered_list_happy(self) -> None:
        blocks = [
            "- line1",
            """- line1
- line2""",
        ]
        expected = [BlockType.UNORDERED_LIST] * len(blocks)
        result = [block_to_block_type(b) for b in blocks]
        self.assertListEqual(result, expected)

    def test_unordered_list_sad(self) -> None:
        blocks = [
            "-line1",
            """- line1
line2""",
            """- line1
-line2""",
            """line1
- line2""",
            """-line1
- line2""",
        ]
        expected = [BlockType.PARAGRAPH] * len(blocks)
        result = [block_to_block_type(b) for b in blocks]
        self.assertListEqual(result, expected)

    def test_ordered_list_happy(self) -> None:
        blocks = [
            "1. line1",
            """1. line1
2. line2""",
        ]
        expected = [BlockType.ORDERED_LIST] * len(blocks)
        result = [block_to_block_type(b) for b in blocks]
        self.assertListEqual(result, expected)

    def test_ordered_list_sad(self) -> None:
        blocks = [
            "0. line1",
            """2. line1
1. line2""",
            """1. line1
3. line2
2. line3""",
        ]
        expected = [BlockType.PARAGRAPH] * len(blocks)
        result = [block_to_block_type(b) for b in blocks]
        self.assertListEqual(result, expected)


class TestMarkdownToHTML(unittest.TestCase):

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is"
            " another paragraph with <i>italic</i> text and <code>code</code> here</p>"
            "</div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self) -> None:
        md = """
# Heading1

## Heading2

### Heading3

#### Heading4

##### Heading5

###### Heading6
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        heading_elements = "".join([f"<h{i}>Heading{i}</h{i}>" for i in range(1, 7)])
        self.assertEqual(html, f"<div>{heading_elements}</div>")

    def test_quote(self) -> None:
        md = """
> This is a quote
> with some **bold text**

> This is another quote
> with some `code`
"""
        expected = (
            "<div>"
            "<blockquote>This is a quote with some <b>bold text</b></blockquote>"
            "<blockquote>This is another quote with some <code>code</code></blockquote>"
            "</div>"
        )
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, expected)

    def test_unordered_list(self) -> None:
        md = """
- item1
- item2
- item3

- item4
- item5
- item6
"""
        expected = (
            "<div>"
            "<ul><li>item1</li><li>item2</li><li>item3</li></ul>"
            "<ul><li>item4</li><li>item5</li><li>item6</li></ul>"
            "</div>"
        )
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, expected)

    def test_ordered_list(self) -> None:
        md = """
1. item1
2. item2
3. item3

1. item4
2. item5
3. item6
"""
        expected = (
            "<div>"
            "<ol><li>item1</li><li>item2</li><li>item3</li></ol>"
            "<ol><li>item4</li><li>item5</li><li>item6</li></ol>"
            "</div>"
        )
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, expected)


if __name__ == "__main__":
    unittest.main()
