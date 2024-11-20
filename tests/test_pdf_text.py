from tests.factory import compare_snapshot
from intelli_chunks import find_chunk, get_intelli_chunks, get_intelli_pages


def test_pages():
    pages = get_intelli_pages("test_files/mini.pdf")
    output = "\n\n----\n\n".join("\n\n".join(paragraphs) for paragraphs in pages)
    compare_snapshot(output, "test_files/mini.txt")


def test_chunks():
    chunks = get_intelli_chunks("test_files/ngl.pdf")

    assert len(chunks) > 500

    output = find_chunk(chunks, "India has been witnessing robust")
    compare_snapshot(output, "test_files/chunk-india.txt")

    output = find_chunk(chunks, "In FY 2023-24, NGL’s total sales revenue")
    compare_snapshot(output, "test_files/chunk-financial-overview.txt")

    output = find_chunk(chunks, "Details of business activities")
    compare_snapshot(output, "test_files/chunk-business-activites.txt")
