import re
import sublime
import sublime_plugin
import webbrowser

from typing import Any, Dict, List

PACKAGE_NAME = __package__.split(".")[0]


def cut_off_string(s: str, max_length: int = 160) -> str:
    if len(s) <= max_length:
        return s

    delimiters_c = ",，.。、'\"＂ 　\t\r\n"
    delimiters_l = "{｛[［<＜“「『《〈(（"
    delimiters_r = "}｝]］>＞”」』》〉)）"

    spliter_re = re.compile(r"[{}]".format(delimiters_c + delimiters_l + delimiters_r))

    cut = 0
    for part in spliter_re.split(s):
        cut_new = cut + len(part)
        if cut_new > max_length:
            break
        cut = cut_new + 1  # 1 for delimiter

    return s[:cut].rstrip(delimiters_c + delimiters_l) + "..."


class IntelliDocsCommand(sublime_plugin.TextCommand):
    last_found = {}  # type: Dict[str, Any]
    cache = {}  # type: Dict[str, Dict[str, Dict[str, Any]]]
    menu_links = {}  # type: Dict[int, str]

    def __init__(self, view: sublime.View) -> None:
        self.view = view
        self.settings = sublime.load_settings("{}.sublime-settings".format(PACKAGE_NAME))

    def run(self, edit: sublime.Edit) -> None:
        # find db for lang
        lang = self.get_lang()

        if lang not in self.cache:
            try:
                self.cache[lang] = sublime.decode_value(  # type: ignore
                    sublime.load_resource("Packages/{}/db/{}.json".format(PACKAGE_NAME, lang))
                )
            except Exception:
                self.cache[lang] = {}

        completions = self.cache[lang]

        # find in completions
        if completions:
            found = {}  # type: Dict[str, Any]

            for function_name in self.find_function_names_from_caret():
                completion = completions.get(function_name)
                if completion:
                    found = completion
                    break

            if not found:
                self.view.erase_status("hint")
                return

            self.view.set_status("hint", found["syntax"] + " | ")
            menus = []

            # Syntax
            menus.append(found["syntax"])

            # Description
            if found["descr"]:
                for descr in re.sub(r"(.{80,100}[\.]) ", r"\1|||", cut_off_string(found["descr"], 350)).split(
                    "|||"
                ):  # Spit long description lines
                    menus.append(" " + descr)

            # Parameters
            if found["params"]:
                menus.append("Parameters:")
            for parameter in found["params"]:
                # fmt: off
                menus.append(
                    " - {name}: {descr}".format(
                        name=parameter["name"],
                        descr=cut_off_string(parameter["descr"]),
                    )
                )
                # fmt: on

            self.last_found = found
            self.append_links(menus, found)
            self.view.show_popup_menu(menus, self.action)

    def get_lang(self) -> str:
        docs = self.settings.get("docs")  # type: Dict[str, str]

        # try to match against the current scope
        scope = self.view.scope_name(self.view.sel()[0].b)
        for match, lang in docs.items():
            if re.search(match, scope):
                return lang

        # no match in predefined docs, return from syntax filename
        self.debug(scope)

        return re.search(
            r"/(?P<syntax>[^/]+)\.(?:tmLanguage|sublime-syntax)$",
            str(self.view.settings().get("syntax")),
        ).group("syntax")

    def find_function_names_from_caret(self) -> List[str]:
        # find function name
        word = self.view.word(self.view.sel()[0])
        word.a = word.a - 100  # Look back 100 character
        word.b = word.b + 1  # Ahead word +1 char
        buff = self.view.substr(word).strip()

        # keep only last line
        buff = " " + buff.split("\n")[-1]

        # find function names ending with "("
        matches = reversed(re.findall(r"(?:[0-9_\].$)]+\.[a-z0-9_.$]+|[A-Za-z0-9_.$]+)(?=\s*\()", buff, re.IGNORECASE))

        function_names = []
        for function_name in matches:
            function_name = function_name.strip(".()[] ")
            if len(function_name) < 2:
                continue
            function_names.append(function_name)
            if "." in function_name:
                function_names.append(re.sub(r".*\.(.*?)$", r"\1", function_name))

        # append current word
        function_names.append(self.view.substr(self.view.word(self.view.sel()[0])))

        self.debug(function_names)

        return function_names

    def append_links(self, menus: List[str], found: Dict[str, Any]) -> None:
        help_links = self.settings.get("help_links")  # type: Dict[str, str]

        self.menu_links = {}
        for pattern, link in sorted(help_links.items()):
            if re.match(pattern, found["path"]):
                host = re.search(r"//(.*?)/", link).group(1)
                self.menu_links[len(menus)] = link.format_map(found)
                menus.append(" > Goto: %s" % host)

    def action(self, item: int) -> None:
        if item in self.menu_links:
            webbrowser.open_new_tab(self.menu_links[item])

    def debug(self, *args, **kargs) -> None:
        if self.settings.get("debug"):
            print(*args, **kargs)
