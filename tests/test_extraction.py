import pytest
from tests.factory import compare_snapshot
from intelli_chunks import get_intelli_pages


@pytest.mark.parametrize(
    "pdf,snapshot",
    [
        ("test_files/ngl.pdf", "test_files/ngl.txt"),
        ("test_files/pnb.pdf", "test_files/pnb.txt"),
    ],
)
def test_pages(pdf, snapshot):
    pages = get_intelli_pages(pdf)
    output = "\n\n----\n\n".join("\n\n".join(paragraphs) for paragraphs in pages)
    compare_snapshot(output, snapshot)
