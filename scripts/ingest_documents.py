#!/usr/bin/env python3
"""
Run this script to ingest all PDFs from knowledge/pdfs/ into the vector store.

Usage:
    python -m scripts.ingest_documents
    python -m scripts.ingest_documents --reset
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag.ingest import ingest_all


def main():
    parser = argparse.ArgumentParser(description="Ingest Ramayana & Mahabharata PDFs")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Attempt to reset / clear existing collection before adding",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Itihasa Bot – Document Ingestion")
    print("=" * 60)

    count = ingest_all(reset=args.reset)

    print("=" * 60)
    if count > 0:
        print(f"Done! {count} chunks are now in the vector store.")
    else:
        print("No chunks were added. Check that PDFs exist in knowledge/pdfs/")
    print("=" * 60)


if __name__ == "__main__":
    main()
