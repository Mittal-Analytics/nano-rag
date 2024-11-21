import pdftotext
import pymupdf
from statistics import StatisticsError, median


def get_pages_pdftotext(filepath):
    print("parsing using pdftotext")
    with open(filepath, "rb") as f:
        pages = list(pdftotext.PDF(f, physical=True))
    return pages


def spacex(text):
    return text.count(" ") / len(text)


def word_count(text):
    return len(text.split())


def is_dense(text):
    return spacex(text) < 0.4 and word_count(text) > 50


def _get_formatted_text(paragraph, base_size):
    text = "\n".join(
        "".join(span["text"] for span in line["spans"]) for line in paragraph["lines"]
    )
    all_large = all(
        span["size"] > base_size
        or ("-bold" in span["font"].lower() and span["size"] == base_size)
        for line in paragraph["lines"]
        for span in line["spans"]
    )

    if all_large and (st := text.strip()):
        text = f"**{st}**"
    return text


def get_formatted_paragraphs_pymupdf(page: pymupdf.Page):
    # https://pymupdf.readthedocs.io/en/latest/app1.html#blocks
    # "The lines within each block are concatenated by a new-line character."
    data = page.get_text(
        "dict",
        # https://pymupdf.readthedocs.io/en/latest/vars.html#TEXTFLAGS_DICT
        # don't neeed images
        flags=pymupdf.TEXT_PRESERVE_LIGATURES
        | pymupdf.TEXT_PRESERVE_WHITESPACE
        | pymupdf.TEXT_MEDIABOX_CLIP
        | pymupdf.TEXT_CID_FOR_UNKNOWN_UNICODE,
    )

    try:
        base_size = median(
            span["size"]
            for block in data["blocks"]
            for line in block["lines"]
            for span in line["spans"]
        )
    except StatisticsError:
        base_size = 100

    # block[6]: 1 if the content is an image.
    paragraphs = [
        _get_formatted_text(block, base_size)
        for block in data["blocks"]
        if block["type"] != 1
    ]
    return paragraphs


def get_paragraphs_pymupdf(page: pymupdf.Page):
    # https://pymupdf.readthedocs.io/en/latest/app1.html#blocks
    # "The lines within each block are concatenated by a new-line character."
    blocks = page.get_text("blocks")

    # block[4]: content of the block.
    # block[6]: 1 if the content is an image.
    paragraphs = [block[4] for block in blocks if block[6] != 1]
    return paragraphs


def remove_non_english_pages(pages):
    def ascii_ratio(text):
        if not text.strip():
            return 1
        ascii_chars = sum(1 for char in text if ord(char) < 128)
        return ascii_chars / len(text)

    return [[para for para in page if ascii_ratio(para) >= 0.5] for page in pages]


def trim_headers_footers(pages):
    pass
