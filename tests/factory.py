import difflib
import os
import io
import webbrowser


class SnapshotChanged(Exception):
    pass


def compare_snapshot(html, save_path):
    existing = None
    if os.path.isfile(save_path):
        with io.open(save_path, "r", encoding="utf8") as tmp:
            existing = tmp.read()
    if existing == html:
        return True
    with open(save_path, "wb") as tmp:
        if isinstance(html, str):
            tmp.write(html.encode("utf8", errors="ignore"))
        else:
            # html response from django is in bytes
            tmp.write(html)

    if existing is None:
        existing = ""

    # calculate diff to show in logs too
    for line in difflib.unified_diff(
        existing.splitlines(),
        html.splitlines(),
        fromfile="Existing",
        tofile="New Snapshot",
    ):
        print(line)

    abs_path = "file://{}".format(os.path.abspath(save_path))
    webbrowser.open(abs_path)
    raise SnapshotChanged("Snapshot has been updated")
