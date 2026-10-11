"""Extract the executed notebook's embedded PNG figures for the LaTeX report."""

import base64
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "notebooks" / "political_violence_exam_results_twfe.ipynb"
OUTPUT_DIR = ROOT / "reports" / "latex" / "figures"

NAMES = {
    (17, 0): "average_pass_rate_by_year.png",
    (18, 0): "districts_exposed_by_year.png",
    (25, 0): "main_twfe_estimates.png",
    (30, 0): "ssc_robustness.png",
    (30, 1): "hsc_robustness.png",
}


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    for cell_index, cell in enumerate(notebook["cells"]):
        image_index = 0
        for output in cell.get("outputs", []):
            encoded = output.get("data", {}).get("image/png")
            if encoded is None:
                continue
            key = (cell_index, image_index)
            if key not in NAMES:
                raise RuntimeError(f"No report filename configured for image {key}")
            path = OUTPUT_DIR / NAMES[key]
            if isinstance(encoded, list):
                encoded = "".join(encoded)
            path.write_bytes(base64.b64decode(encoded))
            written.append(path)
            image_index += 1

    expected = set(NAMES.values())
    actual = {path.name for path in written}
    if actual != expected:
        raise RuntimeError(f"Expected {sorted(expected)}, extracted {sorted(actual)}")

    for path in written:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
