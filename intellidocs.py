import io
import json
import os
import re
import sublime
import sublime_plugin
import webbrowser

__DIR__ = os.path.dirname(os.path.abspath(__file__))


def cut_off_string(s: str, max_length: int = 160) -> str:
    length = len(s)

    if length <= max_length:
        return s

    length = 0
    words = s.split(" ")

    for i, word in enumerate(words):
        length += len(word) + 1  # 1 for space
        i += 1

        if length >= max_length:
            break

    return " ".join(words[0:i]).rstrip(",，.。、 \t\r\n") + "..."


class IntelliDocsCommand(sublime_plugin.TextCommand):
    last_function_name = None
    last_found = False
    cache = {}
    menu_links = {}

    def __init__(self, view: sublime.View) -> None:
        self.view = view
        self.settings = sublime.load_settings("IntelliDocs.sublime-settings")

    def run(self, edit: sublime.Edit) -> None:
        # find db for lang
        lang = self.getLang()
        if lang not in self.cache:  # DEBUG disable cache: or 1 == 1
            path_db = __DIR__ + "/db/%s.json" % lang
            self.debug("Loaded intelliDocs db:", path_db)
            if os.path.exists(path_db):
                with io.open(path_db, encoding="UTF-8") as f:
                    self.cache[lang] = json.load(f)
            else:
                self.cache[lang] = {}

        completions = self.cache[lang]

        # find in completions
        if completions:
            function_names = self.getFunctionNames(completions)
            found = False
            for function_name in function_names:
                completion = completions.get(function_name)
                if completion:
                    found = completion
                    break

            if found:
                self.view.set_status("hint", found["syntax"] + " | ")
                menus = []

                # Syntax
                menus.append(found["syntax"])

                # Description
                for descr in re.sub(
                    r"(.{80,100}[\.]) ", r"\1|||", cut_off_string(found["descr"], 350)
                ).split(
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
                self.appendLinks(menus, found)
                self.view.show_popup_menu(menus, self.action)
            else:
                self.view.erase_status("hint")

    def getLang(self) -> str:
        # try to match against the current scope
        scope = self.view.scope_name(self.view.sel()[0].b)
        for match, lang in self.settings.get("docs").items():
            if re.search(match, scope):
                return lang

        # no match in predefined docs, return from syntax filename
        self.debug(scope)

        return re.search(
            r"/(?P<syntax>[^/]+)\.(?:tmLanguage|sublime-syntax)$",
            self.view.settings().get("syntax"),
        ).group("syntax")

    def getFunctionNames(self, completions: dict) -> list:
        # find function name
        word = self.view.word(self.view.sel()[0])
        word.a = word.a - 100  # Look back 100 character
        word.b = word.b + 1  # Ahead word +1 char
        buff = self.view.substr(word).strip()

        # keep only last line
        buff = " " + buff.split("\n")[-1]

        # find function names ending with "("
        matches = reversed(
            re.findall(
                r"(?:[0-9_\].$)]+\.[a-z0-9_.$]+|[A-Za-z0-9_.$]+)(?=\s*\()", buff, re.IGNORECASE
            )
        )

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

    def appendLinks(self, menus: list, found: dict) -> None:
        self.menu_links = {}
        for pattern, link in sorted(self.settings.get("help_links").items()):
            if re.match(pattern, found["path"]):
                host = re.search(r"//(.*?)/", link).group(1)
                self.menu_links[len(menus)] = link.format(**found)
                menus.append(" > Goto: %s" % host)

    def action(self, item: str) -> None:
        if item in self.menu_links:
            webbrowser.open_new_tab(self.menu_links[item])

    def debug(self, *text) -> None:
        if self.settings.get("debug"):
            print(*text)
