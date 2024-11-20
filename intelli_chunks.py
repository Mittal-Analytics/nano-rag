import sys
import pymupdf
import pathlib
from chonkie import SDPMChunker

from utils import (
    get_formatted_paragraphs_pymupdf,
    get_paragraphs_pymupdf,
    trim_headers_footers,
)


def get_intelli_pages(filepath):
    print("parsing pdf using pymupdf")
    doc = pymupdf.open(filepath)
    pages = [get_formatted_paragraphs_pymupdf(page) for page in doc]
    print("trimming headers footers")
    trim_headers_footers(pages)
    return pages


class LineSemanticChunker(SDPMChunker):
    def _split_sentences(self, text: str) -> [str]:
        return [st for s in text.split("\n\n") if (st := s.strip())]


def get_chunks(text):
    # https://www.sbert.net/docs/sentence_transformer/pretrained_models.html
    # https://huggingface.co/models?library=sentence-transformers
    print("preparing chunker")
    chunker = LineSemanticChunker(
        embedding_model="all-minilm-l6-v2",
        max_chunk_size=8000,
        similarity_threshold=0.3,
        initial_sentences=1,
        skip_window=1,
    )
    print("grouping chunks by similarity")
    chunks = chunker.chunk(text)
    return chunks


def get_chunk_text(chunk):
    return "\n\n".join(c.text for c in chunk.sentences)


def find_chunk(chunks, needle, is_print=False):
    for i, chunk in enumerate(chunks):
        if needle in chunk.text:
            text = get_chunk_text(chunk)
            if is_print:
                return print(f"\n\n\nchunk {i}:\n{text}")
            else:
                return text


def get_intelli_chunks(filepath, output=None):
    pages = get_intelli_pages(filepath)
    text = "\n\n".join("\n\n".join(paragraphs) for paragraphs in pages)

    if output:
        pathlib.Path(output).write_text(text)

    chunks = get_chunks(text)
    return chunks


def main():
    FILEPATH = "samples/ngl.pdf"
    OUTPUT = "outputs/ngl-intelli.md"
    chunks = get_intelli_chunks(FILEPATH, output=OUTPUT)
    find_chunk(chunks, "What operational", is_print=True)
    find_chunk(chunks, "Acquired Macrotech", is_print=True)
    find_chunk(chunks, "Management Discussion", is_print=True)
    find_chunk(chunks, "Economy", is_print=True)

    while no := input("Debug Chunk No / ipdb / exit:"):
        if no.isdigit():
            no = int(no)
            print(get_chunk_text(chunks[no]))
        elif no == "ipdb":
            __import__("ipdb").set_trace()
        else:
            sys.exit()


if __name__ == "__main__":
    main()
