"""Generate a Fabric-compatible notebook directory from a list of cells.

Usage:
    python generate_notebook.py --name my_notebook --output /tmp --cells cells.json

Or import as a module:
    from generate_notebook import create_notebook_dir
    create_notebook_dir("my_notebook", cells, "/tmp")
"""

import json
import os
import argparse


def create_notebook_dir(name: str, cells: list[dict], output_dir: str) -> str:
    """Create a Fabric-compatible notebook directory.

    Args:
        name: Notebook display name (without .Notebook suffix)
        cells: List of cell dicts with keys: cell_type, source, metadata
        output_dir: Parent directory where <name>.Notebook/ will be created

    Returns:
        Path to the created notebook directory
    """
    nb_dir = os.path.join(output_dir, f"{name}.Notebook")
    os.makedirs(nb_dir, exist_ok=True)

    # Build ipynb content
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernel_info": {"name": "synapse_pyspark"},
            "kernelspec": {"name": "synapse_pyspark", "display_name": "Synapse PySpark"},
            "language_info": {"name": "python"},
            "microsoft": {"language": "python", "language_group": "synapse_pyspark"},
        },
        "cells": cells,
    }

    with open(os.path.join(nb_dir, "notebook-content.ipynb"), "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)

    # Build .platform file
    platform = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Notebook", "displayName": name},
        "config": {"version": "2.0", "logicalId": "00000000-0000-0000-0000-000000000000"},
    }

    with open(os.path.join(nb_dir, ".platform"), "w", encoding="utf-8") as f:
        json.dump(platform, f, indent=2)

    return nb_dir


def make_code_cell(source: str) -> dict:
    """Create a code cell from a source string."""
    lines = [line + "\n" for line in source.split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": "code",
        "metadata": {"microsoft": {"language": "python", "language_group": "synapse_pyspark"}},
        "source": lines,
        "outputs": [],
        "execution_count": None,
    }


def make_markdown_cell(source: str) -> dict:
    """Create a markdown cell from a source string."""
    lines = [line + "\n" for line in source.split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": lines,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Fabric notebook directory")
    parser.add_argument("--name", required=True, help="Notebook name")
    parser.add_argument("--output", default="/tmp", help="Output parent directory")
    parser.add_argument("--cells", required=True, help="Path to cells JSON file")
    args = parser.parse_args()

    with open(args.cells, "r") as f:
        cells = json.load(f)

    result = create_notebook_dir(args.name, cells, args.output)
    print(f"Created: {result}")
