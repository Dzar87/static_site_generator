import unittest

from textnode import (
    TextNode,
    TextType,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    text_node_to_html_node,
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
        self.assertEqual(result, nodes)
        self.assertIsNot(result, nodes)

    def test_delimit_text(self) -> None:
        nodes = [
            TextNode("some text with no delimiter", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "_", TextType.TEXT)
        self.assertEqual(result, nodes)
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
        self.assertEqual(result, expected)
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
        self.assertEqual(result, expected)
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
        self.assertEqual(result, expected)
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
        self.assertEqual(result, expected)
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
        self.assertEqual(result, expected)
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

        self.assertEqual(result, expected)
        self.assertIsNot(result, nodes)


class TestExtractMardownImages(unittest.TestCase):

    def test_none(self) -> None:
        text = "Nothing to see here."
        expected = []
        result = extract_markdown_images(text)
        self.assertEqual(result, expected)

    def test_single(self) -> None:
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif)."
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif")]
        result = extract_markdown_images(text)
        self.assertEqual(result, expected)

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
        self.assertEqual(result , expected)

    def test_start(self) -> None:
        text = "![rick roll](https://i.imgur.com/aKaOqIh.gif) image at the start."
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif")]
        result = extract_markdown_images(text)
        self.assertEqual(result , expected)

    def test_end(self) -> None:
        text = "Image at the end ![rick roll](https://i.imgur.com/aKaOqIh.gif)"
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif")]
        result = extract_markdown_images(text)
        self.assertEqual(result, expected)

    def test_exclude_links(self) -> None:
        text = "This is text with a link [to boot dev](https://www.boot.dev)."
        expected = []
        result = extract_markdown_images(text)
        self.assertEqual(result, expected)

class TestExtractMardownLinks(unittest.TestCase):
    def test_none(self) -> None:
        text = "Nothing to see here."
        expected = []
        result = extract_markdown_links(text)
        self.assertEqual(result, expected)

    def test_single(self) -> None:
        text = "This is text with a link [to boot dev](https://www.boot.dev)."
        result = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev")]
        self.assertEqual(result, expected)

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
        self.assertEqual(result, expected)

    def test_start(self) -> None:
        text = "[to boot dev](https://www.boot.dev) link at the start."
        result = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev")]
        self.assertEqual(result, expected)

    def test_end(self) -> None:
        text = "link at the end [to boot dev](https://www.boot.dev)"
        result = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev")]
        self.assertEqual(result, expected)

    def test_exclude_image(self) -> None:
        text = "Image at the end ![rick roll](https://i.imgur.com/aKaOqIh.gif)"
        expected = []
        result = extract_markdown_links(text)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
