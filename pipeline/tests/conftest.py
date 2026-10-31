from pathlib import Path

import pytest

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def fx():
    def _read(name: str) -> bytes:
        return (FIX / name).read_bytes()

    return _read
