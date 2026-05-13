"""Run a SPARQL query against a local RDF/Turtle file.

Examples:
    python run-sparql.py alice.ttl scratch.rq
    python run-sparql.py alice.ttl --query "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"
Docs: https://rdflib.readthedocs.io/en/7.1.1/intro_to_sparql.html
"""

from __future__ import annotations

import argparse
from pathlib import Path

from rdflib import Graph
from rdflib.query import Result


def term_text(term, graph: Graph) -> str:
    """Format RDF terms with readable prefixes when possible."""
    if term is None:
        return ""
    return term.n3(graph.namespace_manager)


def print_select_results(results: Result, graph: Graph) -> None:
    headers = [str(var) for var in results.vars]
    rows = [[term_text(term, graph) for term in row] for row in results]

    widths = [
        max(len(header), *(len(row[i]) for row in rows)) if rows else len(header)
        for i, header in enumerate(headers)
    ]

    print(" | ".join(header.ljust(widths[i]) for i, header in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))

    for row in rows:
        print(" | ".join(value.ljust(widths[i]) for i, value in enumerate(row)))

    print(f"\n{len(rows)} result{'s' if len(rows) != 1 else ''}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a SPARQL query against a local RDF graph."
    )
    parser.add_argument("data", help="Path to an RDF data file, usually .ttl")
    parser.add_argument(
        "query_file",
        nargs="?",
        help="Path to a .rq SPARQL query file. Omit when using --query.",
    )
    parser.add_argument(
        "--query",
        help="SPARQL query text supplied directly on the command line.",
    )
    parser.add_argument(
        "--format",
        default="turtle",
        help="RDF parser format for the data file. Default: turtle",
    )
    args = parser.parse_args()

    if not args.query and not args.query_file:
        parser.error("provide either a query_file or --query")

    data_path = Path(args.data)
    graph = Graph()
    graph.parse(data_path, format=args.format)

    query_text = args.query
    if query_text is None:
        query_text = Path(args.query_file).read_text(encoding="utf-8")

    results = graph.query(query_text)

    if results.type == "SELECT":
        print_select_results(results, graph)
    elif results.type == "ASK":
        print(bool(results))
    elif results.type == "CONSTRUCT":
        print(results.graph.serialize(format="turtle"))
    else:
        print(results.serialize(format="txt").decode("utf-8"))


if __name__ == "__main__":
    main()
