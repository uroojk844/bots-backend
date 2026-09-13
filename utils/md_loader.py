from pathlib import Path


def load_markdown(file_path: str) -> str:
    """
    Load a Markdown file and return its contents as text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    if path.suffix.lower() != ".md":
        raise ValueError(f"Expected a .md file, got: {path.suffix}")

    return path.read_text(encoding="utf-8")


def load_markdown_folder(folder_path: str) -> str:
    """
    Load all Markdown files from a folder and combine them.
    """

    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    documents = []

    for file in sorted(folder.glob("*.md")):
        content = file.read_text(encoding="utf-8")

        documents.append(f"\n\n===== {file.name} =====\n\n" f"{content}")

    return "".join(documents)
