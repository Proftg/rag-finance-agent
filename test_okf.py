from ingest import parse_okf


def test_okf():
    body, meta = parse_okf("---\ntype: Report\ntags: [a, b]\n---\n# Title\nbody", "x.md")
    assert meta == {"source": "x.md", "type": "Report", "tags": "a, b"}
    assert body == "# Title\nbody"

    # no front-matter: body untouched, only source in metadata
    body, meta = parse_okf("plain text", "y.md")
    assert meta == {"source": "y.md"}
    assert body == "plain text"

    # body containing '---' (markdown rule) is preserved
    body, meta = parse_okf("---\ntype: X\n---\nintro\n---\noutro", "z.md")
    assert meta["type"] == "X"
    assert "---" in body
    print("OK")


def test_fiche_roundtrip():
    from wiki import _fiche_md, _slug

    md = _fiche_md("What is the fraud AUC?", "AUC is 0.945.")
    body, meta = parse_okf(md, "f.md")
    assert meta["type"] == "Generated"
    assert meta["status"] == "unreviewed"
    assert meta["tags"] == "generated"
    assert "0.945" in body
    assert _slug("What is the fraud AUC?")  # non-empty, deterministic slug
    print("OK roundtrip")


if __name__ == "__main__":
    test_okf()
    test_fiche_roundtrip()
