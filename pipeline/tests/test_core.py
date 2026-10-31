
from pipeline import core
from pipeline.core import Source, ValidationError, run_source


def make_source(fetch, rows=100, group="monthly", rolling=False):
    def build(p):
        return {"x.json": {"v": list(range(rows))}}, {"rows": rows, "last_point": "now"}

    return Source(
        id="t", name="T", provider="P", group=group, urls=["u"], homepage="h", license="l", citation="c", frequency="f",
        caveats="k", fetch=fetch, parse=lambda raw: raw, build=build, rolling=rolling,
    )


def test_write_json_only_when_changed(tmp_path):
    assert core.write_json("a.json", {"a": 1}, tmp_path) is True
    assert core.write_json("a.json", {"a": 1}, tmp_path) is False
    assert core.write_json("a.json", {"a": 2}, tmp_path) is True


def test_nan_becomes_null(tmp_path):
    core.write_json("n.json", {"a": [float("nan"), 1.5]}, tmp_path)
    assert core.read_json("n.json", tmp_path) == {"a": [None, 1.5]}


def test_failed_source_keeps_last_good_and_marks_stale(tmp_path):
    manifest = {"sources": {}}
    ok = run_source(make_source(lambda: {}), manifest, tmp_path)
    assert ok["status"] == "ok" and (tmp_path / "x.json").exists()
    good_text = (tmp_path / "x.json").read_text()

    def boom():
        raise ValidationError("kilden er nede")

    bad = run_source(make_source(boom), manifest, tmp_path)
    assert bad["status"] == "stale" and "nede" in bad["error"]
    assert bad["fetched_at"] == ok["fetched_at"]  # siste gode tidspunkt beholdes
    assert (tmp_path / "x.json").read_text() == good_text  # data urørt


def test_dramatic_row_drop_is_rejected(tmp_path):
    manifest = {"sources": {}}
    run_source(make_source(lambda: {}, rows=100), manifest, tmp_path)
    res = run_source(make_source(lambda: {}, rows=50), manifest, tmp_path)
    assert res["status"] == "stale" and "Radantall" in res["error"]
    # rullerende serier er unntatt
    res = run_source(make_source(lambda: {}, rows=50, rolling=True), manifest, tmp_path)
    assert res["status"] == "ok"


def test_first_failure_without_previous_is_failed_not_crash(tmp_path):
    def boom():
        raise RuntimeError("x")

    res = run_source(make_source(boom), {"sources": {}}, tmp_path)
    assert res["status"] == "failed"
