# HW5: Ontology-based Semantic Grounding — Group 02

> NYCU AI Capstone 2026, Spring 2026

Ontology-based semantic grounding for a gripper-equipped robot. The ontology
grounds the perceived objects of the course tasks and lets an OWL reasoner answer
the central question: **which objects are graspable, and why?**

Repository: https://github.com/VicsonPeng/semantic-affordance-grounding

## Group Members

| Member | Student ID | Role |
|--------|-----------|------|
| 彭程 (Person A) | 112550128 | Repo setup, ontology skeleton |
| 周宇彥 (Person B) | 112550148 | GraspableObject inference rule |
| 張紹安 (Person C) | 112550166 | Cup stacking instances |
| 余逸翔 (Person D) | 112550027 | Baseline object instances |
| 張盛瑋 (Person E) | 112550117 | OWL reasoning, SPARQL queries |
| 張祐廷 (Person F) | 112550116 | Report, documentation |

---

## Selected Task

Primary task: **Cup Stacking** (blue cup and pink cup).

Baseline tasks also included as required: **Cutlery Arrangement** (knife, fork,
plate) and **Toy Block Collection** (toy blocks, basket).

---

## Repository Structure

```
semantic-affordance-grounding/
├── README.md
├── report.md / report.pdf
├── ontology/
│   ├── group-ontology.ttl           # Group 02 authored ontology (main file)
│   ├── inferred-results.ttl         # inferred graph after OWL reasoning
│   └── imports/
│       ├── course-affordance.ttl    # provided course ontology (imported)
│       └── course-alignment.ttl     # provided SKOS alignment (imported)
├── queries/
│   ├── graspable_objects.rq         # required: inferred graspable objects
│   └── task_objects.rq              # contrast: task relevance vs graspability
├── results/
│   ├── graspable_objects_output.txt
│   ├── task_objects_output.txt
│   └── screenshots/
├── src/
│   └── reason_and_query.py          # reasoning + query driver
└── hw5_documents/                   # homework spec
```

- **Group-authored:** `ontology/group-ontology.ttl`, `queries/*.rq`,
  `src/reason_and_query.py`, `README.md`, `report.md`.
- **Imported (not authored by the group):** everything under `ontology/imports/`.
- **Generated:** `ontology/inferred-results.ttl`, `results/*.txt`.

---

## Namespace Policy

| Prefix | URI | Usage |
|--------|-----|-------|
| `cap:` | `https://hcis.io/ontology/aicapstone/2026/` | Shared course vocabulary — reused, not redefined |
| `g02:` | `https://hcis.io/ontology/aicapstone/2026/group02/` | Group 02 instances and extensions |

Group-specific individuals (e.g. `g02:blueCup01`) and the two group schema terms
(`g02:hasMaxGripWidth`, `g02:hasContainerTarget`) use `g02:`. Shared classes and
properties (`cap:Cup`, `cap:hasAffordance`, …) use `cap:`. `cap:GraspableObject`
is a reserved course term (spec §8); the course file ships it without a defining
axiom, so the group supplies the OWL `equivalentClass` definition (spec Listing 5)
as the reasoning target.

---

## Ontology Design

The design keeps four layers separate so that "graspable" is **inferred**, never
hard-coded:

| Layer | What it is | Examples |
|---|---|---|
| Object type | shared course class | `cap:Cup`, `cap:Knife`, `cap:Plate`, `cap:Basket` |
| Task role | shared course role class | `cap:TargetObject`, `cap:ReferenceObject`, `cap:ContainerTarget`, `cap:CollectableObject` |
| Affordance | shared course affordance class | `cap:GraspingAffordance`, `cap:StackabilityAffordance`, `cap:SupportAffordance`, `cap:ContainmentAffordance` |
| Instance | group individual | `g02:blueCup01`, `g02:knife01`, `g02:toyBlock01` … |
| Inferred class | reasoner-derived | `g02:blueCup01 a cap:GraspableObject` |

Each instance is linked to **explicit affordance individuals** (e.g.
`g02:blueCupGraspingAffordance a cap:GraspingAffordance`). This grounds the
affordance layer as data and keeps the ontology inside the OWL 2 RL profile, so
the graspability inference is reproducible with a free Python toolchain (and
equally with Protégé + HermiT).

The defining axiom (Person B):

```turtle
cap:GraspableObject
    owl:equivalentClass [
        a owl:Class ;
        owl:intersectionOf (
            cap:PhysicalObject
            [ a owl:Restriction ;
              owl:onProperty cap:hasAffordance ;
              owl:someValuesFrom cap:GraspingAffordance ]
        )
    ] .
```

i.e. `GraspableObject ≡ PhysicalObject ⊓ ∃ hasAffordance.GraspingAffordance`.

---

## Modeled Objects and Affordances

| Instance | Type | Task role | Affordances | **Graspable?** |
|----------|------|-----------|-------------|----------------|
| `g02:blueCup01` | `cap:Cup` | TargetObject | Grasping, Stackability | Yes (inferred) |
| `g02:pinkCup01` | `cap:Cup` | TargetObject | Grasping, Stackability | Yes (inferred) |
| `g02:knife01` | `cap:Knife` | TargetObject | Grasping | Yes (inferred) |
| `g02:fork01` | `cap:Fork` | TargetObject | Grasping | Yes (inferred) |
| `g02:toyBlock01` | `cap:ToyBlock` | CollectableObject | Grasping | Yes (inferred) |
| `g02:toyBlock02` | `cap:ToyBlock` | CollectableObject | Grasping | Yes (inferred) |
| `g02:plate01` | `cap:Plate` | ReferenceObject | Support | No (no grasping affordance) |
| `g02:basket01` | `cap:Basket` | ContainerTarget | Containment | No (no grasping affordance) |

**Design choice:** the plate and basket are deliberately modeled *without* a
grasping affordance. They are relevant to their tasks (placement reference /
container) but are not grasp targets, so the reasoner correctly leaves them out
of `cap:GraspableObject` — demonstrating task relevance ≠ graspability (spec §6).

---

## Reasoning Workflow

`cap:GraspableObject` membership is derived by a reasoner, then queried with
SPARQL. Two equivalent ways to reproduce it:

**A. Python (used to generate the committed `inferred-results.ttl`)**

```bash
pip install rdflib owlrl
python src/reason_and_query.py
```

`src/reason_and_query.py` loads `ontology/imports/course-affordance.ttl` +
`ontology/group-ontology.ttl`, materialises the OWL 2 RL closure with `owlrl`,
exports `ontology/inferred-results.ttl`, and writes the query output to
`results/`. `ontology/inferred-results.ttl` is that closure with trivially-true
triples (reflexive `owl:sameAs`/`subClassOf`, universal `rdf:type rdfs:Resource`
/`owl:Thing`) stripped, so the meaningful entailments — including the inferred
`cap:GraspableObject` type assertions — stay readable.

**B. Protégé + HermiT** — open `ontology/group-ontology.ttl`, start HermiT,
confirm the six grasp targets appear under `cap:GraspableObject`, then
File → Export inferred axioms → `ontology/inferred-results.ttl`.

---

## Running the SPARQL Query

```bash
# Over the inferred graph (recommended)
arq --data ontology/inferred-results.ttl --query queries/graspable_objects.rq

# Or end-to-end (reason + query) in one step:
python src/reason_and_query.py
```

---

## Expected Query Output

`queries/graspable_objects.rq` over the **inferred** model
(`results/graspable_objects_output.txt`):

```
obj                                                | label     | role
---------------------------------------------------+-----------+-----------------------------
.../group02/blueCup01  | blue_cup  | .../TargetObject
.../group02/fork01     | fork      | .../TargetObject
.../group02/knife01    | knife     | .../TargetObject
.../group02/pinkCup01  | pink_cup  | .../TargetObject
.../group02/toyBlock01 | toy_block | .../CollectableObject
.../group02/toyBlock02 | toy_block | .../CollectableObject

(6 row(s))
```

`queries/task_objects.rq` (`results/task_objects_output.txt`):

```
object     | type     | role              | affordances                                | graspable
-----------+----------+-------------------+--------------------------------------------+----------
basket01   | Basket   | ContainerTarget   | ContainmentAffordance                      |
blueCup01  | Cup      | TargetObject      | GraspingAffordance, StackabilityAffordance | yes
fork01     | Fork     | TargetObject      | GraspingAffordance                         | yes
knife01    | Knife    | TargetObject      | GraspingAffordance                         | yes
pinkCup01  | Cup      | TargetObject      | GraspingAffordance, StackabilityAffordance | yes
plate01    | Plate    | ReferenceObject   | SupportAffordance                          |
toyBlock01 | ToyBlock | CollectableObject | GraspingAffordance                         | yes
toyBlock02 | ToyBlock | CollectableObject | GraspingAffordance                         | yes
```

---

## What is Inferred vs. Asserted

- **Asserted**: each object instance's type, affordance individuals, task role,
  color, label, pose frame, width.
- **Inferred**: `cap:GraspableObject` membership — derived by the reasoner from
  the `owl:equivalentClass` axiom, **not** manually written.

Proof it is inferred: `src/reason_and_query.py` first runs the query over the
**raw asserted graph** and gets **0 rows**; only after OWL reasoning do the six
grasp targets appear (spec pitfall #5). The chain that fires per grasp target:
`cax-sco` (Cup ⊑ PhysicalObject) → `cls-svf1` (has a GraspingAffordance value) →
`cls-int1` (in both conjuncts) → `cax-eqc1` (intersection ≡ GraspableObject).
The plate and basket never satisfy `cls-svf1` for grasping, so they are excluded.

---

## How `ontology/inferred-results.ttl` was generated

It is the OWL 2 RL closure of `course-affordance.ttl` + `group-ontology.ttl`,
produced by `owlrl.DeductiveClosure(owlrl.RDFS_OWLRL_Semantics)` in
`src/reason_and_query.py` and serialised to Turtle (trivial closure triples
stripped). Equivalent to exporting HermiT's inferred axioms from Protégé.

---

## Links

- [Group Ontology](ontology/group-ontology.ttl)
- [Inferred Results](ontology/inferred-results.ttl)
- [SPARQL Query — graspable objects](queries/graspable_objects.rq) · [task objects](queries/task_objects.rq)
- [Query Output](results/graspable_objects_output.txt) · [task objects output](results/task_objects_output.txt)
- [Reasoning Script](src/reason_and_query.py)
- [Report](report.md) · [PDF](report.pdf)
- [Course Ontology (imported)](ontology/imports/course-affordance.ttl)
