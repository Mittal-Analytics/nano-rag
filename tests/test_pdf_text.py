from functools import lru_cache
import pytest
from tests.factory import compare_snapshot
from intelli_chunks import find_chunk, get_intelli_chunks, get_intelli_pages


def test_pages():
    pages = get_intelli_pages("test_files/mini.pdf")
    output = "\n\n----\n\n".join("\n\n".join(paragraphs) for paragraphs in pages)
    compare_snapshot(output, "test_files/mini.txt")


get_chunks = lru_cache(get_intelli_chunks)


@pytest.mark.parametrize(
    "text,snapshot",
    [
        ("India has been witnessing robust", "test_files/chunk-india.txt"),
        (
            "In FY 2023-24, NGL’s total sales revenue",
            "test_files/chunk-financial-overview.txt",
        ),
        ("Details of business activities", "test_files/chunk-business-activites.txt"),
    ],
)
def test_chunks(text, snapshot):
    chunks = get_chunks("test_files/ngl.pdf")
    assert len(chunks) > 500

    output = find_chunk(chunks, text)
    compare_snapshot(output, snapshot)
