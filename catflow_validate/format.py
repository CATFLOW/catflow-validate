from typing import List, Union, Type
import abc

from tabulate import tabulate


class BaseFormatter(abc.ABC):
    @abc.abstractmethod
    def heading(self, msg: str, level: int = 1) -> str:
        pass

    def tabular(self, rows: List[List[Union[str, int]]], header: List[Union[str, int]] = None) -> str:
        pass

    def link(self, body: str, href: str = None) -> str:
        return body


class TextFormatter(BaseFormatter):
    def heading(self, msg: str, level: int = 1) -> str:
        c = "=" if level == 1 else "-"
        l = f"+{c * (len(msg) + 2)}+"

        if level < 3:
            return f"{l}\n| {msg} |\n{l}"
        else:
            return f"{msg}\n{l[1:-1]}"
    
    def tabular(self, rows: List[List[Union[str, int]]], header: List[Union[str, int]] = None) -> str:
        if header is None:
            # produce empty headers
            header = ['' for _ in max([len(r) for r in rows])]
        else:
            # format the header
            header = [f"{h}: " for h in header]
        return "\n".join(["\t\t".join([f"{h}{r}" for r, h in zip(row, header)]) for row in rows])
    
    def link(self, body: str, href: str = None) -> str:
        return super().link(body, href)


class MarkdownFormatter(BaseFormatter):
    def heading(self, msg: str, level: int = 1) -> str:
        return f"{'#' * level} {msg}"

    def tabular(self, rows: List[List[Union[str, int]]], header: List[Union[str, int]] = None) -> str:
        if header is None:
            header = rows.pop(0)
        
        # # print the header
        # md = f"| {' | '.join([f' {h} ' for h in header])} |\n"
        # md += f"|{'-' * (len(md) - 2)}|"
        # md += '\n'.join([f"|{' | '.join([str(r) for r in row])}|" for row in rows])
        md = tabulate(rows, headers=header, tablefmt='github')

        return md
    
    def link(self, body: str, href: str = None) -> str:
        return f"[{body}]({href if href is not None else body})"


def register_formatter(formatter: Type[BaseFormatter], formats: Union[str, List[str]]):
    # check  formatter
    if not issubclass(formatter, BaseFormatter):
        raise RuntimeError("Formatter have to inherit from catflow_validate.formatters.BaseFormatter")
    
    # check formats
    if isinstance(formats, str):
        formats = [formats]
    
    for fmt in formats:
        AVAILABLE_FORMATTERS[fmt] = formatter


def get_formatter(fmt: str, default = None) -> BaseFormatter:
    # check if exists
    if fmt.lower() not in AVAILABLE_FORMATTERS.keys():
        return default
    
    # return instance
    return AVAILABLE_FORMATTERS[fmt.lower()]()


AVAILABLE_FORMATTERS = {
    'txt': TextFormatter,
    'text': TextFormatter,
    'md': MarkdownFormatter,
    'markdown': MarkdownFormatter
}