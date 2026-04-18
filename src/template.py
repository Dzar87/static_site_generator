from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from htmlnode import HTMLNode


if TYPE_CHECKING:
    from pathlib import Path


class ContextDict(TypedDict):
    title: str
    content: HTMLNode


class Template:
    required_subs: tuple[Literal["content"], Literal["title"]] = ("content", "title")

    def __init__(self, path: Path) -> None:
        self._template_path = path.resolve(strict=True)
        self._template: str = ""
        self._is_valid = False

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(file: '{self._template_path.name}' is_valid: {self._is_valid})"
        )

    def _load_template(self) -> None:
        if not self._template:
            self._template = self._template_path.read_text()

    def validate(self) -> None:
        self._load_template()
        if not self._is_valid:
            for sub in self.required_subs:
                value = f"{{{{ {sub} }}}}"
                assert value in self._template, f"{value} not in template"
            self._is_valid = True

    def render(self, context: ContextDict) -> str:
        assert self._is_valid, "template not validated"
        result = self._template
        for sub in self.required_subs:
            assert sub in context
            value: str | HTMLNode = context[sub]
            if isinstance(value, HTMLNode):
                value = value.to_html()
            result = result.replace(f"{{{{ {sub} }}}}", value)
        return result

    def render_to_file(self, dst: Path, context: ContextDict) -> Path:
        dst.write_text(self.render(context=context))
        return dst
