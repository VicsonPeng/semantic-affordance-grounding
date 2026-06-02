#!/usr/bin/env python3
"""Person E — reason over the Group 02 ontology and retrieve graspable objects.

Workflow (Python / RDFLib + owlrl, with an explicit OWL reasoning layer):

  1. Load the course vocabulary (ontology/imports/course-affordance.ttl) and the
     group ontology (ontology/group-ontology.ttl) into one RDF graph.
  2. Materialise entailed triples with the ``owlrl`` OWL 2 RL reasoner — the
     documented reasoning mechanism required for a Python workflow (spec §13.3):
     cap:GraspableObject membership is DERIVED, not asserted on individuals.
  3. Export the inferred graph to ontology/inferred-results.ttl.
  4. Run the SPARQL queries in queries/ over the inferred graph; save to results/.

This reproduces, on the command line, what Protégé + HermiT would show in its
inferred class hierarchy. Why the cups/knife/fork/blocks become graspable:
  cap:GraspableObject = cap:PhysicalObject AND (hasAffordance some GraspingAffordance)
  cax-sco  : an individual typed cap:Cup (etc.) is also a cap:PhysicalObject
  cls-svf1 : an individual with hasAffordance to a cap:GraspingAffordance
             individual is a member of the existential restriction class
  cls-int1 : being in both conjuncts -> member of the intersection class
  cax-eqc1 : the intersection is owl:equivalentClass cap:GraspableObject
The plate (support only) and basket (containment only) never satisfy cls-svf1
for grasping, so they are correctly left out.
"""

from pathlib import Path

import rdflib
from rdflib import Graph
import owlrl

SRC_DIR = Path(__file__).resolve().parent
ROOT = SRC_DIR.parent
COURSE_TTL = ROOT / "ontology" / "imports" / "course-affordance.ttl"
GROUP_TTL = ROOT / "ontology" / "group-ontology.ttl"
INFERRED_TTL = ROOT / "ontology" / "inferred-results.ttl"
QUERIES_DIR = ROOT / "queries"
RESULTS_DIR = ROOT / "results"

CAP = rdflib.Namespace("https://hcis.io/ontology/aicapstone/2026/")
G02 = rdflib.Namespace("https://hcis.io/ontology/aicapstone/2026/group02/")


def load_asserted_graph() -> Graph:
    g = Graph()
    g.parse(COURSE_TTL, format="turtle")
    g.parse(GROUP_TTL, format="turtle")
    return g


def bind_prefixes(g: Graph) -> None:
    g.bind("cap", CAP)
    g.bind("g02", G02)
    g.bind("owl", rdflib.OWL)
    g.bind("rdfs", rdflib.RDFS)
    g.bind("xsd", rdflib.XSD)


def run_query(g: Graph, query_file: Path):
    return g.query(query_file.read_text(encoding="utf-8"))


def strip_trivial(g: Graph) -> Graph:
    """Drop OWL RL boilerplate so the export shows meaningful entailments only."""
    out = Graph()
    for s, p, o in g:
        if p == rdflib.OWL.sameAs and s == o:
            continue
        if p == rdflib.RDFS.subClassOf and s == o:
            continue
        if p == rdflib.RDF.type and o in (rdflib.RDFS.Resource, rdflib.OWL.Thing):
            continue
        if p == rdflib.RDFS.subClassOf and o in (rdflib.RDFS.Resource, rdflib.OWL.Thing):
            continue
        out.add((s, p, o))
    bind_prefixes(out)
    return out


def fmt_results(results) -> str:
    cols = [str(v) for v in results.vars]
    rows = [[("" if row[i] is None else str(row[i])) for i in range(len(cols))]
            for row in results]
    widths = [len(c) for c in cols]
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(cell))
    line = lambda cells: " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells))
    out = [line(cols), "-+-".join("-" * w for w in widths)]
    out += [line(r) for r in rows]
    out.append(f"\n({len(rows)} row(s))")
    return "\n".join(out)


def main() -> None:
    asserted = load_asserted_graph()
    bind_prefixes(asserted)
    n_asserted = len(asserted)
    print(f"Loaded asserted graph: {n_asserted} triples "
          f"({COURSE_TTL.name} + {GROUP_TTL.name})")

    pre = run_query(asserted, QUERIES_DIR / "graspable_objects.rq")
    print(f"graspable_objects.rq over the RAW asserted graph: "
          f"{len(list(pre))} row(s)  <- inference is required\n")

    inferred = load_asserted_graph()
    bind_prefixes(inferred)
    owlrl.DeductiveClosure(
        owlrl.RDFS_OWLRL_Semantics,
        axiomatic_triples=False,
        datatype_axioms=False,
    ).expand(inferred)
    print(f"After OWL RL closure: {len(inferred)} triples "
          f"(+{len(inferred) - n_asserted} inferred)")

    graspable = sorted(
        str(s) for s in inferred.subjects(rdflib.RDF.type, CAP.GraspableObject)
        if "/group02/" in str(s)
    )
    print("Inferred cap:GraspableObject individuals:")
    for s in graspable:
        print(f"  - {s}")
    print()

    export = strip_trivial(inferred)
    export.serialize(destination=INFERRED_TTL, format="turtle")
    print(f"Wrote inferred graph -> {INFERRED_TTL.relative_to(ROOT)} "
          f"({len(export)} triples after stripping trivial closure axioms)\n")

    RESULTS_DIR.mkdir(exist_ok=True)
    for qfile, ofile in [("graspable_objects.rq", "graspable_objects_output.txt"),
                         ("task_objects.rq", "task_objects_output.txt")]:
        res = run_query(inferred, QUERIES_DIR / qfile)
        table = fmt_results(res)
        header = (f"# Query: queries/{qfile}\n"
                  f"# Executed over the OWL RL inferred model.\n\n")
        (RESULTS_DIR / ofile).write_text(header + table + "\n", encoding="utf-8")
        print(f"=== {qfile} ===")
        print(table)
        print(f"(saved to results/{ofile})\n")


if __name__ == "__main__":
    main()
