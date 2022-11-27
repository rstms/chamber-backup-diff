# diff tests

import shlex
import subprocess

import pytest

from chamber_backup_diff.diff import ChamberDiff


@pytest.fixture(scope="module")
def lines():
    def _lines(text_string):
        lines = text_string.split("\n")
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]
        return lines

    return _lines


@pytest.fixture(scope="module")
def run(lines):
    def _run(cmd, **kwargs):
        _lines = kwargs.pop("lines", True)
        _strip = kwargs.pop("strip", True)
        _check = kwargs.pop("check", True)
        kwargs.setdefault("text", True)
        kwargs.setdefault("capture_output", True)
        cmd = shlex.split(cmd)
        proc = subprocess.run(cmd, **kwargs)
        if _check:
            assert proc.returncode == 0
        assert not proc.stderr, proc.stderr
        ret = proc.stdout
        if _strip:
            ret = ret.strip()
        if _lines:
            ret = lines(ret)
        return ret

    return _run


@pytest.fixture(scope="module")
def untar(run):
    def _untar(tarball):
        return run("tar xzfv " + str(tarball), cwd=tarball.parent)

    return _untar


# @pytest.fixture(autouse=True, scope="module")
# def preserve_state(run):
#    before = run('chamber list-services')
#    backup_tarball = run("chamber backup", lines=False)
#    yield True
#    run('chamber restore -f ' + backup_tarball)
#    after = run('chamber list-services')
#    assert before == after


def test_diff_tarballs(shared_datadir, untar, lines, run):
    untar(shared_datadir / "old.tgz")
    untar(shared_datadir / "new.tgz")
    diff_lines = run("diff -r old new", cwd=shared_datadir, check=False)
    print()
    for line in diff_lines:
        print(line)


def test_diff_object(shared_datadir):
    d = ChamberDiff()
    old = shared_datadir / "old.tgz"
    new = shared_datadir / "new.tgz"
    # name, profile, tarball, name, profile, tarball
    d.compare("old", "testnet", old, "new", "testnet", new)


def test_diff_object_none(shared_datadir):
    d = ChamberDiff()
    old = shared_datadir / "old.tgz"
    new = shared_datadir / "new.tgz"
    d.compare("old", None, old, "new", None, new)
