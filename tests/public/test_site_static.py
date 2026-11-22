"""Tests statiques du site publié `public/` (cas S1 à S15 de la fiche W1)."""

import hashlib
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PUBLIC = ROOT / "public"
PAGES = ("index.html", "network.html", "404.html", "unsupported.html")
MAX_LINE = 95
MAX_LINES = 750
EM_DASH = chr(0x2014)
POLICY = (
    "default-src 'none'; script-src 'self'; style-src 'self'; "
    "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
    "base-uri 'none'; form-action 'none'; object-src 'none'"
)
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
EXTERNAL = re.compile(r"https?://|//[a-z0-9.-]+\.[a-z]{2,}|@import")
INJECTION = re.compile(
    r"innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval\(|new Function"
)
FORBIDDEN_LOADING = re.compile(
    r'type="module"|fetch\(|XMLHttpRequest|^import ',
    re.MULTILINE,
)
DEMO_PARAM = re.compile(r"params\.(has|get)\('demo'\)")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}")
CSS_URL = re.compile(r"url\(\s*(['\"]?)(?P<target>[^'\")]*)\1\s*\)")
SCRIPT_TAG = re.compile(r"<script\b[^>]*\bsrc=[^>]*>", re.IGNORECASE)
HASHES = {
    "vendor/three.min.js": (
        "f34446bf875b5fb0dcd93819ffe1d9e182d46634ee855f5d904c6c4ac7cdbc95"
    ),
    "vendor/OrbitControls.js": (
        "b4c6e53f98538535b11fd6655627d47fb5877b3ad972568bff0a7026c4b6d5c4"
    ),
}
LICENSES = (
    "fonts/LICENSE-barlow.txt",
    "fonts/LICENSE-chakra-petch.txt",
    "vendor/LICENSE",
)
LONG_LINE_EXEMPT = ("data.js", "js/sound-data.js")


class TagCollector(HTMLParser):
    """Relève les balises d'une page : (nom, dictionnaire d'attributs)."""

    def __init__(self):
        super().__init__()
        self.tags = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, {name: value or "" for name, value in attrs}))
        self._in_title = tag == "title"

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def read(relative):
    """Lit un fichier de `public/` en UTF-8 ; échoue s'il est absent."""
    path = PUBLIC / relative
    if not path.is_file():
        raise AssertionError(f"fichier absent : {path}")
    return path.read_text(encoding="utf-8")


def parse_page(name):
    """Renvoie le TagCollector de la page `public/<name>`."""
    collector = TagCollector()
    collector.feed(read(name))
    return collector


def own_files(*suffixes, exempt=()):
    """Fichiers de `public/` de ces suffixes, hors `vendor/` et fichiers exemptés.

    Échoue si `public/` n'a aucun fichier de ce genre (jamais de succès vide).
    """
    if not (PUBLIC / "index.html").is_file():
        raise AssertionError(f"site absent : {PUBLIC / 'index.html'}")
    files = [
        path
        for path in sorted(PUBLIC.rglob("*"))
        if path.is_file()
        and path.suffix in suffixes
        and "vendor" not in path.relative_to(PUBLIC).parts
        and path.relative_to(PUBLIC).as_posix() not in exempt
    ]
    if not files:
        raise AssertionError(f"aucun fichier {suffixes} sous {PUBLIC}")
    return files


def matches(files, pattern, transform=lambda text: text):
    """Liste les occurrences `fichier:ligne: texte` d'un motif dans ces fichiers."""
    found = []
    for path in files:
        text = transform(path.read_text(encoding="utf-8"))
        for number, line in enumerate(text.split("\n"), start=1):
            if pattern.search(line):
                found.append(f"{path.relative_to(PUBLIC)}:{number}: {line.strip()}")
    return found


class SiteStaticTest(unittest.TestCase):
    """Constats sur les fichiers de `public/`."""

    def test_S1(self):
        for name in PAGES:
            with self.subTest(page=name):
                page = parse_page(name)
                tags = page.tags
                html = [attrs for tag, attrs in tags if tag == "html"]
                self.assertEqual(html[0].get("lang"), "fr")
                self.assertTrue(page.title.strip(), "titre vide")
                metas = [attrs for tag, attrs in tags if tag == "meta"]
                self.assertIn("viewport", [meta.get("name") for meta in metas])
                policies = [
                    " ".join(meta.get("content", "").split())
                    for meta in metas
                    if meta.get("http-equiv", "").lower() == "content-security-policy"
                ]
                self.assertEqual(policies, [POLICY])
                robots = [
                    meta.get("content", "")
                    for meta in metas
                    if meta.get("name") == "robots"
                ]
                self.assertTrue(any("noindex" in value for value in robots))
                links = [attrs.get("href", "") for tag, attrs in tags if tag == "link"]
                self.assertTrue(any(href.endswith("favicon.svg") for href in links))

    def test_S2(self):
        files = own_files(".html", ".css", ".js")
        found = matches(
            files,
            EXTERNAL,
            lambda text: text.replace(SVG_NAMESPACE, ""),
        )
        self.assertEqual(found, [])

    def test_S3(self):
        found = matches(own_files(".html", ".css", ".js"), INJECTION)
        self.assertEqual(found, [])

    def test_S4(self):
        found = matches(own_files(".html", ".css", ".js"), FORBIDDEN_LOADING)
        self.assertEqual(found, [])

    def test_S5(self):
        references = []
        for name in PAGES:
            for tag, attrs in parse_page(name).tags:
                for key in ("src", "href"):
                    if key in attrs:
                        references.append((PUBLIC / name, attrs[key]))
        for css in own_files(".css"):
            for found in CSS_URL.finditer(css.read_text(encoding="utf-8")):
                references.append((css, found.group("target")))
        self.assertTrue(references, "aucune adresse relevée")
        for source, target in references:
            if target.startswith(("#", "data:")):
                continue
            with self.subTest(source=source.name, target=target):
                self.assertNotRegex(target, r"^(/|[a-z][a-z0-9+.-]*:)")
                local = target.split("#")[0].split("?")[0]
                resolved = (source.parent / local).resolve()
                self.assertTrue(resolved.exists(), f"introuvable : {resolved}")
                self.assertTrue(resolved.is_relative_to(PUBLIC.resolve()))

    def test_S6(self):
        self.assertTrue((PUBLIC / "js" / "demo.js").is_file(), "js/demo.js absent")
        scripts = [
            attrs
            for tag, attrs in parse_page("index.html").tags
            if tag == "script" and "src" in attrs
        ]
        sources = [attrs["src"].removeprefix("./") for attrs in scripts]
        self.assertIn("js/demo.js", sources)
        self.assertIn("js/app.js", sources)
        self.assertLess(sources.index("js/demo.js"), sources.index("js/app.js"))
        self.assertIn("defer", scripts[sources.index("js/demo.js")])
        self.assertNotIn("demo-", read("data.js"))
        self.assertRegex(read("js/app.js"), DEMO_PARAM)

    def test_S7(self):
        css = own_files(".css")
        self.assertTrue(matches(css, re.compile("prefers-reduced-motion")))

    def test_S8(self):
        found = matches(own_files(".html"), re.compile(r'tabindex="[1-9]'))
        self.assertEqual(found, [])

    def test_S9(self):
        files = own_files(".html", ".css", ".js", exempt=LONG_LINE_EXEMPT)
        found = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            for number, line in enumerate(text.split("\n"), start=1):
                if len(line) > MAX_LINE:
                    found.append(f"{path.relative_to(PUBLIC)}:{number}: {len(line)}")
        self.assertEqual(found, [])

    def test_S10(self):
        files = own_files(".css", ".js", exempt=LONG_LINE_EXEMPT)
        too_long = []
        for path in files:
            count = len(path.read_text(encoding="utf-8").splitlines())
            if count > MAX_LINES:
                too_long.append(f"{path.relative_to(PUBLIC)}: {count} lignes")
        self.assertEqual(too_long, [])

    def test_S11(self):
        found = matches(own_files(".html", ".css", ".js"), re.compile(EM_DASH))
        self.assertEqual(found, [])

    def test_S12(self):
        counted = 0
        for name in PAGES:
            text = read(name)
            head_end = text.find("</head>")
            body_start = text.find("<body")
            self.assertGreater(head_end, 0, f"{name} : </head> absent")
            self.assertGreater(body_start, head_end, f"{name} : <body> absent")
            for tag in SCRIPT_TAG.finditer(text):
                counted += 1
                with self.subTest(page=name, script=tag.group(0)):
                    self.assertRegex(tag.group(0), r"\bdefer\b")
                    self.assertGreater(tag.start(), head_end)
                    self.assertLess(tag.start(), body_start)
        self.assertGreater(counted, 0, "aucun script chargé par les pages")

    def test_S13(self):
        links = [
            attrs.get("href")
            for tag, attrs in parse_page("404.html").tags
            if tag == "a"
        ]
        self.assertTrue(any(href in ("./", "index.html") for href in links))

    def test_S14(self):
        text = read("data.js")
        prefix = "window.SYSTEME = "
        self.assertTrue(text.startswith(prefix))
        body = text[len(prefix):].strip().removesuffix(";")
        self.assertIsInstance(json.loads(body), dict)
        self.assertNotIn("/home/", text)
        self.assertIsNone(EMAIL.search(text))

    def test_S15(self):
        for relative, expected in HASHES.items():
            path = PUBLIC / relative
            self.assertTrue(path.is_file(), f"fichier absent : {path}")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.subTest(file=relative):
                self.assertEqual(digest, expected)
        for relative in LICENSES:
            with self.subTest(license=relative):
                self.assertTrue((PUBLIC / relative).is_file())


if __name__ == "__main__":
    unittest.main()
