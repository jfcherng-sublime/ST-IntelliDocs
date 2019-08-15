import html
import io
import json
import os
import re
import sys

# Update DB from local devdocs.io dump:
#
#     https://github.com/Thibaut/devdocs
#
# Devdocs offline packages:
#
#     http://dl.devdocs.io/dom.tar.gz
#     http://dl.devdocs.io/go.tar.gz
#     http://dl.devdocs.io/javascript.tar.gz
#     http://dl.devdocs.io/jquery.tar.gz
#     http://dl.devdocs.io/love.tar.gz
#     http://dl.devdocs.io/php.tar.gz
#     http://dl.devdocs.io/python~3.7.tar.gz
#
# Download above tarballs and decompress them to have the following directory structure:
#
#    docs/
#    |-- dom/
#    |-- javascript/
#    |-- jquery/
#    |-- php/
#    |-- python/

__DIR__ = os.path.dirname(os.path.abspath(__file__))
os.chdir(__DIR__)

docs_dir = "docs"

docs = {
    "dom": "Javascript",
    "go": "Go",
    "javascript": "Javascript",
    "jquery": "Javascript",
    "php": "PHP",
    "python": "Python",
    "love": "Lua (Love)",
}

PATTERNS = {
    "Go": {
        "alias": r"^(?:bufio|builtin|bytes|context|crypto|encoding|errors|expvar|flag|fmt|hash|html|image|io|log|math|mime|net|os|path|plugin|reflect|regexp|runtime|sort|strconv|strings|sync|syscall|testing|time|unicode|unsafe)\.",
        "descr": r"<p>(.*?)</p>",
        "doc": r'\sid="{name}">(.*?)<(?:h[1234]|div)\b',
        "syntax": r"<pre\b[^>]*>(.*?)</pre>",
    },
    "PHP": {
        # "skip" : r".*::",
        "descr": r"rdfs-comment.*?>(.*?)</p>",
        "params": r"<dt>(.*?)<dd>(.*?)</dd>",
        "syntax": r"methodsynopsis.*?>(.*?)</pre>",
    },
    "Python": {
        "alias": r"^(?:str|dict|int|float|list|bytes|bytearray|array\.array|array|re\.match)\.",
        "descr": r"<p>(.*?)</p>",
        "doc": r'\sid="{name}">(.*?)</dd>',
        "syntax": r"<code>(.*?)</code>",
    },
    "Javascript": {
        "alias": r"^(?:[aA]rray|[sS]tring|[dD]ate|[fF]unction|[oO]bject|[rR]egExp|[nN]umber|window)\.",
        "descr": r"<h1[\s>].*?<p>(.*?)</p>",
        "params": r"(?:<dt>(.*?)<dd>(.*?)</dd>|<li>.{5,30}<strong>(.*?)</strong>(.*?)</li>)",
        "syntax": r"(?:[sS]yntax|section).*?<(?:code|pre|span).*?>(.*?\).*?)</(?:p|pre|code|h2)>",
    },
    "Lua (Love)": {
        # "skip" : r".*::",
        "doc": r'((?:.(?!"Function_2"))+)',
        "alias": r"^(?:enet|love\.audio|love\.event|love\.filesystem|love\.font|love\.graphics|love\.image|love\.joystick|love\.keyboard|love\.math|love\.mouse|love\.physics|love\.sound|love\.system|love\.thread|love\.timer|love\.touch|love\.video|love\.window|love|Lua)\.",
        "descr": r"<p>(.*?)</p>",
        "params": r'<dt>\s*<code>\s*<a [^>]+>((?:.(?!<dd>))*.)<dd>(.*?)</dd>',
        "syntax": r'Synopsis</h3>\s*<pre [^>]+>([^<]+)',
    },
}


def print_now(*args, **kargs) -> None:
    print(*args, **kargs)
    sys.stdout.flush()


def html_to_plain_text(s: str) -> str:
    # replace all (consecutive) whitespaces with a single space
    s = re.sub(r"\s+", " ", s)
    # remove html tags
    s = re.sub(r"</?[^>]*>", "", s)

    return html.unescape(s).strip()


class LanguageParser:
    def __init__(self, language: str, st_syntax: str):
        # such as javascript, jquery
        self.language = language
        # such Javascript (both javascript and jQuery belong to)
        self.st_syntax = st_syntax

        self.doc_dir = os.path.join(docs_dir, language)
        self.output_db_path = st_syntax + ".json"
        self.patterns = PATTERNS[st_syntax]
        self.file_caches = {}

        self.update_doc()

    def get_pattern(self, pattern_name: str):
        return self.patterns[pattern_name]

    def get_descr(self, doc: str) -> str:
        match_descr = re.search(self.patterns["descr"], doc, re.DOTALL)

        if match_descr:
            descr = match_descr.group(1)
        else:
            descr = ""

        return html_to_plain_text(descr).strip()

    def get_params(self, doc: str) -> list:
        params = []

        if "params" not in self.patterns or not self.patterns["params"]:
            return params

        for match in re.findall(self.patterns["params"], doc, re.DOTALL):
            name, descr = [group for group in match if group]
            descr = re.sub(r"^(.{30,200}?)(\. |$).*", r"\1\2", html_to_plain_text(descr))
            params.append({"name": html_to_plain_text(name), "descr": descr})

        return params

    def get_doc_file_content(self, entry_path: str) -> str:
        doc_file = re.sub(r"#.*", "", entry_path.replace("*", "_")) + ".html"
        doc_path = os.path.join(self.doc_dir, doc_file)

        try:
            if doc_path not in self.file_caches:
                with io.open(doc_path, "r", encoding="UTF-8") as f:
                    self.file_caches[doc_path] = f.read()

            doc = self.file_caches[doc_path]
        except Exception as err:
            print(err)
            doc = ""

        return doc

    def get_doc_index_info(self) -> dict:
        with io.open(os.path.join(self.doc_dir, "index.json"), "r", encoding="UTF-8") as f:
            return json.load(f)

    def update_doc(self):
        doc_index_info = self.get_doc_index_info()

        try:
            # open the previous db so that we can append docs between different language
            # such append jQuery docs to Javascript docs
            with io.open(self.output_db_path, "r", encoding="UTF-8") as f:
                db = json.load(f)
        except Exception:
            db = {}

        no_match = []

        for entry in doc_index_info["entries"]:
            if "/" in entry["name"]:
                print_now("S", end="")
                continue

            entry["name"] = (
                entry["name"]
                .replace(" constants", "")
                .replace(" variables", "")
                .replace(" (class)", "")
                .strip("().")
            )

            if "skip" in self.patterns and re.search(self.patterns["skip"], entry["name"]):
                print_now("S", end="")
                continue

            doc = self.get_doc_file_content(entry["path"])

            # get the real doc part from the HTML content
            if "doc" in self.patterns:
                if "#" in entry["path"]:
                    html_id = re.search(r"#(.*)", entry["path"]).group(1)
                else:
                    html_id = entry["name"]

                m = re.search(self.patterns["doc"].format(name=re.escape(html_id)), doc, re.DOTALL)

                doc = m.group(1) if m else ""

            m = re.search(self.patterns["syntax"], doc, re.DOTALL)

            # Add to db
            if m:
                syntax = html_to_plain_text(m.group(1))
                syntax = syntax.replace(")Returns:", ") Returns:")  # jQuery doc returns fix

                # multiple syntax possible
                if ");" in syntax:
                    parts = syntax.split(");")
                    syntax = ");\n or ".join([part for part in parts if part.strip()]) + ");"

                db[entry["name"]] = {
                    "name": entry["name"],
                    "path": self.language + "/" + entry["path"],
                    "type": entry["type"],
                    "syntax": syntax,
                    "descr": self.get_descr(doc),
                    "params": self.get_params(doc),
                }

                # Create alias like str.replace -> replace
                if "alias" in self.patterns:
                    name_alias = re.sub(self.patterns["alias"], "", entry["name"])
                    if name_alias != entry["name"]:
                        db[name_alias] = db[entry["name"]]

                        print("A", end="")

                # jQuery.* -> $.* alias
                if entry["name"].startswith("jQuery"):
                    name_alias = entry["name"].replace("jQuery.", "$.")
                    db[name_alias] = db[entry["name"]]

                print_now(".", end="")

            else:
                no_match.append(entry["name"])

                print_now("-", end="")

        with io.open(self.output_db_path, "w", encoding="UTF-8", newline="\n") as f:
            json.dump(db, f, sort_keys=True, indent=4, ensure_ascii=False)

        if no_match:
            print("No match:", no_match)

        print("Done!")


for language, st_syntax in docs.items():
    print(" * Updating {} -> {}".format(language, st_syntax))
    LanguageParser(language, st_syntax)
