import re
from functools import lru_cache
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


def get_block_paragraphs_pymupdf(page: pymupdf.Page):
    # https://pymupdf.readthedocs.io/en/latest/app1.html#blocks
    # "The lines within each block are concatenated by a new-line character."
    blocks = page.get_text("blocks")

    # block[4]: content of the block.
    # block[6]: 1 if the content is an image.
    paragraphs = [block[4] for block in blocks if block[6] != 1]
    return paragraphs


def _is_mixed_case(w):
    # strip any prefixes which are not alphanumeric
    while w and (not w[0].isalnum()):
        w = w[1:]
    return any(c.isupper() for c in w[1:]) and not w.isupper()


def _is_non_ascii(w):
    # do `ord()` to see ord value
    # do `chr()` to see char at particuar ord value
    return any(
        ((oc := ord(c)) >= 128) and not (8216 <= oc <= 8223) and (oc not in [8211])
        for c in w
    )


def _is_gibberish(para):
    if not para.strip():
        return False

    words = para.split()
    bad_words = sum(1 for w in words if _is_mixed_case(w) or _is_non_ascii(w))
    if bad_words > 4 and (bad_words / len(words) > 0.1):
        return True
    return False


def debug_gibberish(para):
    """
    from utils import debug_gibberish
    """
    # handle paste from terminal
    lines = para.splitlines()
    if all(line.startswith("-") for line in lines):
        para = "\n".join(line.removeprefix("-") for line in lines)

    words = para.split()
    bad_words = [w for w in words if _is_mixed_case(w) or _is_non_ascii(w)]
    print("bad words:", bad_words)


def remove_non_english_paras(pages):
    pages = ([para for para in page if not _is_gibberish(para)] for page in pages)
    return [page for page in pages if page]


@lru_cache
def _get_hash(paragraph):
    "get paragraph without spaces and numbers"
    paragraph = re.sub(r"\s", "", paragraph)
    paragraph = "".join(ch for ch in paragraph if not ch.isdigit())
    return paragraph


def _get_common_paragraph(selected_paragraphs, min_page_count):
    for paragraph in selected_paragraphs:
        if selected_paragraphs.count(paragraph) >= min_page_count:
            return paragraph


def _get_header(pages, min_page_count):
    top_paragraphs = [_get_hash(paragraphs[0]) for paragraphs in pages if paragraphs]
    return _get_common_paragraph(top_paragraphs, min_page_count)


def _get_footer(pages, min_page_count):
    last_paragraphs = [_get_hash(paragraphs[-1]) for paragraphs in pages if paragraphs]
    return _get_common_paragraph(last_paragraphs, min_page_count)


def _remove_paragraph(pages, paragraph_hash, pos):
    for paragraphs in pages:
        if paragraphs and _get_hash(paragraphs[pos]) == paragraph_hash:
            paragraphs.pop(pos)


def trim_headers_footers(pages):
    for paragraphs in pages:
        # remove empty paragraphs in the beginning and end
        while paragraphs and paragraphs[0].strip() == "":
            paragraphs.pop(0)
        while paragraphs and paragraphs[-1].strip() == "":
            paragraphs.pop(-1)

    # common paragraph is present in more than 2/3 of the pages
    no_of_pages = len(pages)
    min_page_count = (
        2
        if no_of_pages <= 2
        else (2 / 3 * no_of_pages)
        if no_of_pages <= 50
        else no_of_pages * 0.4
    )
    while (paragraph := _get_header(pages, min_page_count)) is not None:
        _remove_paragraph(pages, paragraph, 0)
    while (paragraph := _get_footer(pages, min_page_count)) is not None:
        _remove_paragraph(pages, paragraph, -1)
