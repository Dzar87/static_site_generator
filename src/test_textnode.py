import unittest

from textnode import TextNode, TextType


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
        node2 = TextNode("This is a text node", TextType.PLAIN)
        self.assertNotEqual(node, node2)

    def test_url_not_eq(self) -> None:
        node = TextNode("This is a text node", TextType.IMAGE, url="http://example.com")
        node2 = TextNode("This is a text node", TextType.IMAGE, url="http://example.test")
        self.assertNotEqual(node, node2)


if __name__ == "__main__":
    unittest.main()
