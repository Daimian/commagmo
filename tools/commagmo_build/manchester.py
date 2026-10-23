"""类 Manchester 的限制表达式解析（不用 rdflib，不做名字解析，名字保持字符串）。

只支持现有构造用到的写法：
  restriction := NAME 'some' NAME | NAME ('exactly'|'min') INT NAME
  class_expr  := term ('and' term)*，term := NAME | '(' restriction ')'
其他写法（only / max / or / not / value、嵌套）一律抛 ExprError。
NAME 是任意不含空白和圆括号的字符串（本地名、`emmo:label`、`<完整 IRI>`）。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

_KEYWORDS = {"some", "exactly", "min", "and"}
_UNSUPPORTED = {"only", "max", "or", "not", "value"}
_TOKEN = re.compile(r"[()]|[^\s()]+")


class ExprError(ValueError):
    pass


@dataclass(frozen=True)
class Named:
    name: str


@dataclass(frozen=True)
class Some:
    prop: str
    filler: str


@dataclass(frozen=True)
class Card:
    prop: str
    op: Literal["exactly", "min"]
    n: int
    filler: str


@dataclass(frozen=True)
class And:
    items: list[Named | Some | Card]

    def __post_init__(self):
        if not self.items or (len(self.items) == 1 and isinstance(self.items[0], Named)):
            raise ExprError("And 至少含一个限制或两项")


class _Parser:
    def __init__(self, s: str):
        self.s = s
        self.toks = _TOKEN.findall(s)
        self.i = 0

    def err(self, msg: str) -> ExprError:
        return ExprError(f"{msg}：{self.s!r}")

    def peek(self) -> str | None:
        return self.toks[self.i] if self.i < len(self.toks) else None

    def next(self) -> str:
        t = self.peek()
        if t is None:
            raise self.err("表达式意外结束")
        self.i += 1
        return t

    def name(self) -> str:
        t = self.next()
        if t in ("(", ")"):
            raise self.err(f"此处需要名字，得到 {t!r}（不支持嵌套表达式）")
        if t in _UNSUPPORTED:
            raise self.err(f"不支持的构造 {t!r}")
        if t in _KEYWORDS:
            raise self.err(f"此处需要名字，得到关键字 {t!r}")
        return t

    def restriction(self) -> Some | Card:
        prop = self.name()
        op = self.next()
        if op == "some":
            return Some(prop, self.name())
        if op in ("exactly", "min"):
            n = self.next()
            if not n.isascii() or not n.isdigit():
                raise self.err(f"基数需为非负整数，得到 {n!r}")
            return Card(prop, op, int(n), self.name())
        if op in _UNSUPPORTED:
            raise self.err(f"不支持的构造 {op!r}")
        raise self.err(f"此处需要 some/exactly/min，得到 {op!r}")

    def term(self) -> Named | Some | Card:
        if self.peek() == "(":
            self.next()
            r = self.restriction()
            if self.next() != ")":
                raise self.err("括号内只能是单个限制，缺少 ')'")
            return r
        return Named(self.name())

    def end(self) -> None:
        if self.peek() is not None:
            raise self.err(f"多余内容 {self.peek()!r}")


def parse_restriction(s: str) -> Some | Card:
    p = _Parser(s)
    r = p.restriction()
    p.end()
    return r


def parse_class_expr(s: str) -> Named | And:
    p = _Parser(s)
    items = [p.term()]
    while p.peek() == "and":
        p.next()
        items.append(p.term())
    p.end()
    if len(items) == 1 and isinstance(items[0], Named):
        return items[0]
    return And(items)


def _format_restriction(e: Some | Card) -> str:
    if isinstance(e, Some):
        return f"{e.prop} some {e.filler}"
    return f"{e.prop} {e.op} {e.n} {e.filler}"


def format_expr(e: Named | Some | Card | And) -> str:
    """parse 的逆：规范写法，单空格，限制加括号（And 内）。"""
    if isinstance(e, Named):
        return e.name
    if isinstance(e, (Some, Card)):
        return _format_restriction(e)
    if isinstance(e, And):
        return " and ".join(
            t.name if isinstance(t, Named) else f"({_format_restriction(t)})" for t in e.items)
    raise TypeError(f"不是表达式：{e!r}")
