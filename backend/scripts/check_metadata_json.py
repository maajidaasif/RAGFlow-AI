"""
test_metadata_json.py  (was test_retriever.py)
==============================================
Tests for the JSON-based FAISS metadata serialization.

Covers:
  - save_database() writes a valid JSON file, not a pickle
  - load_database() round-trips metadata exactly
  - No pickle import remains in vector_database.py, retriever.py,
    or check_metadata.py
  - metadata.json schema: list[dict[str, str]]
  - metadata.pkl has been removed
  - Retriever.__init__ loads JSON without errors

Run from backend/:
    python test_metadata_json.py
"""

import json
import os
import shutil
import sys
import tempfile

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)


# ---------------------------------------------------------------------------
# Minimal test runner
# ---------------------------------------------------------------------------

_passed = []
_failed = []


def test(name, fn):
    try:
        fn()
        _passed.append(name)
        print("  PASS:", name)
    except Exception as exc:
        _failed.append(name)
        print("  FAIL:", name, "->", exc)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_save_load_roundtrip():
    """VectorDatabase.save_database() writes JSON; load_database() restores it exactly."""
    import numpy as np
    import services.vector_database as vdb_mod
    from services.vector_database import VectorDatabase

    tmpdir = tempfile.mkdtemp()
    orig_dir = vdb_mod.VECTOR_DB_DIR
    vdb_mod.VECTOR_DB_DIR = tmpdir

    try:
        sample_meta = [
            {"paper_name": "alpha.pdf", "chunk": "Alpha chunk one."},
            {"paper_name": "alpha.pdf", "chunk": "Alpha chunk two."},
            {"paper_name": "beta.pdf",  "chunk": "Beta chunk one."},
        ]
        embeddings = np.random.rand(3, 384).astype("float32")

        db = VectorDatabase()
        db.create_database(embeddings, sample_meta)
        db.save_database()

        json_path = os.path.join(tmpdir, "metadata.json")
        assert os.path.exists(json_path), "metadata.json was not created"

        # Must be parseable as JSON
        with open(json_path, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)

        assert isinstance(loaded, list), "Top-level must be a list"
        assert len(loaded) == 3, f"Expected 3 entries, got {len(loaded)}"
        assert loaded[0]["paper_name"] == "alpha.pdf"
        assert loaded[2]["paper_name"] == "beta.pdf"

        # Roundtrip: load_database must restore metadata identically
        db2 = VectorDatabase()
        db2.load_database()
        assert db2.metadata == sample_meta, "Metadata did not survive roundtrip"
        assert db2.index.ntotal == 3, "FAISS vector count mismatch after roundtrip"

    finally:
        vdb_mod.VECTOR_DB_DIR = orig_dir
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_metadata_file_is_not_pickle():
    """vector_db/metadata.json must NOT start with a pickle magic byte."""
    json_path = os.path.join("vector_db", "metadata.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Missing: {json_path}")
    with open(json_path, "rb") as fh:
        header = fh.read(2)
    # Pickle streams always start with 0x80; JSON starts with [ or {
    assert header[:1] != b"\x80", "File looks like a pickle stream!"
    assert header[:1] in (b"[", b"{", b" ", b"\n", b"\r"), (
        f"Unexpected file header: {header!r}"
    )


def test_no_pickle_in_vector_database():
    """vector_database.py must not contain 'import pickle'."""
    src = open(
        os.path.join("services", "vector_database.py"), encoding="utf-8"
    ).read()
    assert "import pickle" not in src, "pickle import found in vector_database.py"


def test_no_pickle_in_retriever():
    """retriever.py must not contain 'import pickle'."""
    src = open(
        os.path.join("services", "retriever.py"), encoding="utf-8"
    ).read()
    assert "import pickle" not in src, "pickle import found in retriever.py"


def test_no_pickle_in_check_metadata():
    """check_metadata.py must not contain 'import pickle'."""
    src = open("check_metadata.py", encoding="utf-8").read()
    assert "import pickle" not in src, "pickle import found in check_metadata.py"


def test_metadata_json_schema():
    """Every entry in metadata.json must be a dict[str, str] with paper_name and chunk."""
    json_path = os.path.join("vector_db", "metadata.json")
    with open(json_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, list), "Top-level must be a list"
    assert len(data) > 0, "Metadata list must not be empty"
    for i, entry in enumerate(data):
        assert isinstance(entry, dict), f"Entry {i} is not a dict"
        assert "paper_name" in entry, f"Entry {i} missing 'paper_name' key"
        assert "chunk" in entry, f"Entry {i} missing 'chunk' key"
        assert isinstance(entry.get("paper_name"), str), (
            f"Entry {i}: 'paper_name' must be a string"
        )
        assert isinstance(entry.get("chunk"), str), (
            f"Entry {i}: 'chunk' must be a string"
        )
        if "paper_id" in entry:
            assert isinstance(entry["paper_id"], int), (
                f"Entry {i}: 'paper_id' must be an integer"
            )


def test_metadata_pkl_removed():
    """vector_db/metadata.pkl must not exist after migration."""
    pkl_path = os.path.join("vector_db", "metadata.pkl")
    assert not os.path.exists(pkl_path), (
        f"{pkl_path} still exists. "
        "Delete it — the new codebase never reads or writes this file."
    )


def test_retriever_loads_json():
    """Retriever.__init__ must load metadata.json successfully."""
    index_path = os.path.join("vector_db", "faiss_index.bin")
    json_path  = os.path.join("vector_db", "metadata.json")

    if not (os.path.exists(index_path) and os.path.exists(json_path)):
        print("    SKIP: vector DB files not present")
        return

    from services.retriever import Retriever
    r = Retriever()
    assert isinstance(r.metadata, list), "metadata must be a list"
    assert len(r.metadata) > 0, "metadata must not be empty"
    assert isinstance(r.metadata[0], dict), "metadata entries must be dicts"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print()
    print("Running metadata JSON tests ...")
    print("=" * 50)

    test("save/load roundtrip (VectorDatabase)",   test_save_load_roundtrip)
    test("metadata.json is not a pickle stream",   test_metadata_file_is_not_pickle)
    test("no pickle import in vector_database.py", test_no_pickle_in_vector_database)
    test("no pickle import in retriever.py",       test_no_pickle_in_retriever)
    test("no pickle import in check_metadata.py",  test_no_pickle_in_check_metadata)
    test("metadata.json schema (dict[str, str])",  test_metadata_json_schema)
    test("metadata.pkl has been removed",          test_metadata_pkl_removed)
    test("Retriever loads JSON metadata",          test_retriever_loads_json)

    print()
    print(f"Results: {len(_passed)} passed, {len(_failed)} failed")

    if _failed:
        sys.exit(1)
