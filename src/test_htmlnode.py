import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


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


class TestLeafNode(unittest.TestCase):
    def setUp(self) -> None:
        self.props = {
            "prop1": "value1",
            "prop2": "value2",
        }
        self.leaf_node = LeafNode("p", "Hello, world!", props=self.props)

    def test_props_to_html(self) -> None:
        self.assertEqual(self.leaf_node.props_to_html(), "prop1=value1 prop2=value2")

    def test_to_html(self) -> None:
        expected = "<p>Hello, world!</p>"
        self.assertEqual(self.leaf_node.to_html(), expected)

    def test_to_html_no_value(self) -> None:
        leaf_node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            leaf_node.to_html()

    def test_to_html_no_tag(self) -> None:
        leaf_node = LeafNode(None, "some value")
        expected = "some value"
        self.assertEqual(leaf_node.to_html(), expected)

    def test_repr(self) -> None:
        expected = (
            "LeafNode(tag: 'p', value: 'Hello, world!', "
            "props: 'prop1=value1 prop2=value2')"
        )
        self.assertEqual(repr(self.leaf_node), expected)

    def test_init_with_children(self) -> None:
        with self.assertRaises(TypeError):
            LeafNode("p", "some value", children=[])


class TestParentNode(unittest.TestCase):

    def setUp(self) -> None:
        self.props = {
            "prop1": "value1",
            "prop2": "value2",
        }
        self.leaf_node = LeafNode("p", "Hello, world!", props=self.props)
        self.parent_node = ParentNode("div", children=None, props=self.props)

    def tearDown(self) -> None:
        self.parent_node.children = None

    def test_to_html_blank(self) -> None:
        expected = "<div></div>"
        self.parent_node.children = []
        self.assertEqual(self.parent_node.to_html(), expected)

    def test_to_html_leaf_single(self) -> None:
        self.parent_node.children = [self.leaf_node]
        expected = "<div><p>Hello, world!</p></div>"
        self.assertEqual(self.parent_node.to_html(), expected)

    def test_to_html_leaf_many(self) -> None:
        self.parent_node.children = [self.leaf_node, self.leaf_node]
        expected = "<div><p>Hello, world!</p><p>Hello, world!</p></div>"
        self.assertEqual(self.parent_node.to_html(), expected)

    def test_to_html_nested(self) -> None:
        child = ParentNode("div", children=[self.leaf_node])
        self.parent_node.children = [child]
        expected = "<div><div><p>Hello, world!</p></div></div>"
        self.assertEqual(self.parent_node.to_html(), expected)

    def test_to_html_leaf_and_nested(self) -> None:
        child = ParentNode("div", children=[self.leaf_node])
        self.parent_node.children = [self.leaf_node, child]
        expected = "<div><p>Hello, world!</p><div><p>Hello, world!</p></div></div>"
        self.assertEqual(self.parent_node.to_html(), expected)


if __name__ == "__main__":
    unittest.main()
