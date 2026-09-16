from pathlib import Path

from flysim.review import compile_reviewed_graph, write_ingestion_report


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    tables = __import__("json").loads(
        (root / "backend" / "tests" / "fixtures" / "synthetic-tables.json").read_text()
    )
    compiled = compile_reviewed_graph(tables)
    path = write_ingestion_report(compiled, root / "reports" / "ingestion.json")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
