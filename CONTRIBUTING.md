# Contributing Guide — Group 02 HW5

## 分工總覽

| 人員 | 組員 (學號) | 負責項目 | 修改的檔案 |
|------|------------|---------|-----------|
| A    | 彭程 (112550128)   | Repo 架構 + 本體骨架 | `ontology/group-ontology.ttl`（骨架）✅ |
| B    | 周宇彥 (112550148) | GraspableObject 推論規則 | `ontology/group-ontology.ttl`（Person B 區塊）✅ |
| C    | 張紹安 (112550166) | 杯子疊放實例 | `ontology/group-ontology.ttl`（Person C 區塊）✅ |
| D    | 余逸翔 (112550027) | Baseline 物件實例 | `ontology/group-ontology.ttl`（Person D 區塊）✅ |
| E    | 張盛瑋 (112550117) | OWL 推論 + SPARQL | `src/reason_and_query.py`、`ontology/inferred-results.ttl`、`queries/`、`results/` ✅ |
| F    | 張祐廷 (112550116) | README + 報告 | `README.md`、`report.md` ✅ |

---

## 工作流程

### Step 1：Clone repo
```bash
git clone <repo-url>
cd semantic-affordance-grounding
```

### Step 2：建立自己的 branch
命名規則：`feature/person-<letter>-<topic>`

```bash
# 範例
git checkout -b feature/person-b-inference
git checkout -b feature/person-c-cup-instances
git checkout -b feature/person-d-baseline-instances
git checkout -b feature/person-e-reasoning-sparql
git checkout -b feature/person-f-report
```

### Step 3：完成工作後開 Pull Request
- PR 目標：`main` branch
- 由 **Person A** 負責 review 並 merge
- PR title 格式：`[Person X] 簡短說明`

---

## 各人員詳細說明

### Person B — GraspableObject 推論規則

**修改檔案**：`ontology/group-ontology.ttl`

找到 `# TODO: Person B` 區塊，填入以下內容（參考 PDF Section 11）：

```turtle
cap:GraspableObject
    a owl:Class ;
    rdfs:label "graspable object"@en ;
    rdfs:comment
        "A physical object inferred to afford grasping by a robot end effector."@en ;
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

**確認重點**：
- 用 `owl:equivalentClass`，不要手動 assert `rdf:type cap:GraspableObject`
- 推論器（HermiT/Pellet）會自動推出哪些 individual 是 GraspableObject

---

### Person C — 杯子疊放實例

**修改檔案**：`ontology/group-ontology.ttl`

找到 `# TODO: Person C` 區塊，填入以下內容（替換實際的 pose frame ID）：

```turtle
# Affordance individuals
g02:blueCupGrasping
    a cap:GraspingAffordance ;
    rdfs:label "blue cup grasping affordance"@en ;
    rdfs:comment "Grasping affordance for the blue cup in the cup-stacking task."@en .

g02:pinkCupGrasping
    a cap:GraspingAffordance ;
    rdfs:label "pink cup grasping affordance"@en ;
    rdfs:comment "Grasping affordance for the pink cup in the cup-stacking task."@en .

# Object instances
g02:blueCup01
    a cap:Cup ;
    rdfs:label "blue cup 01"@en ;
    rdfs:comment "The blue cup instance in Group 02's cup-stacking task environment."@en ;
    cap:hasAffordance g02:blueCupGrasping ;
    cap:hasTaskRole cap:TargetObject ;
    cap:hasColor "blue" ;
    cap:hasObjectLabel "blue_cup" ;
    cap:hasPoseFrame "world/object_blue_cup" .   # <-- 替換成你們實際的 pose frame ID

g02:pinkCup01
    a cap:Cup ;
    rdfs:label "pink cup 01"@en ;
    rdfs:comment "The pink cup instance in Group 02's cup-stacking task environment."@en ;
    cap:hasAffordance g02:pinkCupGrasping ;
    cap:hasTaskRole cap:TargetObject ;
    cap:hasColor "pink" ;
    cap:hasObjectLabel "pink_cup" ;
    cap:hasPoseFrame "world/object_pink_cup" .   # <-- 替換成你們實際的 pose frame ID
```

**確認重點**：
- `cap:hasPoseFrame` 的值請替換成你們 project 實際使用的 frame identifier
- `cap:hasObjectLabel` 填你們 perception/simulation 用的 label string

---

### Person D — Baseline 物件實例

**修改檔案**：`ontology/group-ontology.ttl`

找到 `# TODO: Person D` 區塊，填入以下內容：

```turtle
# Knife
g02:knifeGrasping
    a cap:GraspingAffordance ;
    rdfs:label "knife grasping affordance"@en ;
    rdfs:comment "Grasping affordance for the knife."@en .

g02:knife01
    a cap:Knife ;
    rdfs:label "knife 01"@en ;
    rdfs:comment "Baseline knife instance for the cutlery-arrangement task."@en ;
    cap:hasAffordance g02:knifeGrasping ;
    cap:hasTaskRole cap:TargetObject ;
    cap:hasObjectLabel "knife" .

# Fork
g02:forkGrasping
    a cap:GraspingAffordance ;
    rdfs:label "fork grasping affordance"@en ;
    rdfs:comment "Grasping affordance for the fork."@en .

g02:fork01
    a cap:Fork ;
    rdfs:label "fork 01"@en ;
    rdfs:comment "Baseline fork instance for the cutlery-arrangement task."@en ;
    cap:hasAffordance g02:forkGrasping ;
    cap:hasTaskRole cap:TargetObject ;
    cap:hasObjectLabel "fork" .

# Plate
g02:plateSupport
    a cap:SupportAffordance ;
    rdfs:label "plate support affordance"@en ;
    rdfs:comment "Support affordance for the plate."@en .

g02:plate01
    a cap:Plate ;
    rdfs:label "plate 01"@en ;
    rdfs:comment "Baseline plate instance used as reference object in cutlery-arrangement task."@en ;
    cap:hasAffordance g02:plateSupport ;
    cap:hasTaskRole cap:ReferenceObject ;
    cap:hasObjectLabel "plate" .

# Toy Block
g02:toyBlockGrasping
    a cap:GraspingAffordance ;
    rdfs:label "toy block grasping affordance"@en ;
    rdfs:comment "Grasping affordance for the toy block."@en .

g02:toyBlock01
    a cap:ToyBlock ;
    rdfs:label "toy block 01"@en ;
    rdfs:comment "Baseline toy block instance for the toy-block-collection task."@en ;
    cap:hasAffordance g02:toyBlockGrasping ;
    cap:hasTaskRole cap:CollectableObject ;
    cap:hasObjectLabel "toy_block" .

# Basket
g02:basketContainment
    a cap:ContainmentAffordance ;
    rdfs:label "basket containment affordance"@en ;
    rdfs:comment "Containment affordance for the basket."@en .

g02:basket01
    a cap:Basket ;
    rdfs:label "basket 01"@en ;
    rdfs:comment "Baseline basket instance as container target in the toy-block-collection task."@en ;
    cap:hasAffordance g02:basketContainment ;
    cap:hasTaskRole cap:ContainerTarget ;
    cap:hasObjectLabel "basket" .
```

---

### Person E — OWL 推論 + SPARQL

**需要的工具**：Protégé（建議，附 HermiT reasoner）

**步驟**：
1. 用 Protégé 開啟 `ontology/group-ontology.ttl`
2. 在 Reasoner 選單選 HermiT，點 Start Reasoner
3. 確認 `g02:blueCup01`、`g02:pinkCup01` 等被推論為 `cap:GraspableObject`
4. File → Export inferred axioms as ontology → 存到 `ontology/inferred-results.ttl`
5. 截圖存到 `results/screenshots/`

**SPARQL 查詢**（填到 `queries/graspable_objects.rq`）：
```sparql
PREFIX cap: <https://hcis.io/ontology/aicapstone/2026/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?obj ?label ?role
WHERE {
  ?obj rdf:type cap:GraspableObject .
  OPTIONAL { ?obj cap:hasObjectLabel ?label . }
  OPTIONAL { ?obj cap:hasTaskRole ?role . }
}
ORDER BY ?obj
```

查詢結果存到 `results/graspable_objects_output.txt`。

---

### Person F — README + 報告

**修改檔案**：`README.md`、`report.md`

README 必須包含（PDF Section 16.2）：
1. Project title and group members
2. Selected task(s)
3. Ontology design explanation
4. Table of modeled objects and affordances
5. Namespace policy
6. Instructions for running the query
7. Expected query output
8. What is inferred vs. asserted
9. How inferred-results.ttl was generated
10. Links to all files

選擇性：跑 Widoco 產生 `docs/` 文件
```bash
java -jar widoco-<version>-jar-with-dependencies_JDK-17.jar \
  -ontFile ontology/group-ontology.ttl \
  -outFolder docs \
  -rewriteAll \
  -uniteSections
```
