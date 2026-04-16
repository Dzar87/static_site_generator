import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def setUp(self) -> None:
        self.child = HTMLNode(tag="a", value="some link")
        self.props = {
            "prop1": "value1",
            "prop2": "value2",
        }
        self.html_node = HTMLNode(tag="div", children=[self.child], props=self.props)

    def test_to_html_raises(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.html_node.to_html()

    def test_props_to_html(self) -> None:
        self.assertEqual(self.html_node.props_to_html(), "prop1=value1 prop2=value2")

    def test_repr(self) -> None:
        child_expected = "HTMLNode(tag: 'a', value: 'some link')"
        self.assertEqual(repr(self.child), child_expected)
        html_node_expected = (
            f"HTMLNode(tag: 'div', children: [{child_expected}], "
            "props: 'prop1=value1 prop2=value2')"
        )
        self.assertEqual(repr(self.html_node), html_node_expected)


if __name__ == "__main__":
    unittest.main()
