from textnode import TextNode, TextType

def hello_world():
    print("hello world")


def main() -> int:
    text_node = TextNode("This is some anchor text", TextType.LINK, url="https://www.boot.dev")
    print(text_node)
    return 0


if __name__ == "__main__":
    SystemExit(main())
