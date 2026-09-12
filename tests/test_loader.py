from io import BytesIO
from pathlib import Path

from app.loaders.pandas_loader import load_data


class Upload(BytesIO):
    name = "persian.csv"


def test_loads_persian_csv_with_unusual_delimiter():
    upload = Upload("سن\x1bحقوق\n30\x1b100\n40\x1b200".encode())
    frame = load_data(upload)

    assert frame.columns.tolist() == ["سن", "حقوق"]
    assert frame.shape == (2, 2)


def test_loads_the_versioned_csv_fixtures():
    samples = list((Path(__file__).parent / "fixtures").glob("*.csv"))
    assert samples
    assert all(not load_data(path).empty for path in samples)
