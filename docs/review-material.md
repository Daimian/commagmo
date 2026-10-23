# material 模块审查：试点

2026-10-23。按 `docs/review-criteria.md` 逐条过。**只审查，不改 YAML**；每条要改的地方等逐条拍板。

试点对象（用户 2026-10-23 确认）：`Crystallography`、`MicrostructureComponent`、`Phase`、`emmo:Material`，
连同它们**直接参与**的关系（进出两个方向）一起审。邻接子树里顺带碰到的问题记在各节的"附带"条目里，
不给结论。

YAML 行号指 `ontology/src/material.yaml`（commit `852899d`，与梳理报告所用的 `709de1d` 相同）。
上游原文取自 EMMO 1.0.4 模块化缓存（`commagmo-legacy/reference/emmo/modules-1.0.4/`，不含 units），
下文 `emmo:X` 均按 `skos:prefLabel` 解析，IRI 写在首次出现处。

## 0 · 对所有概念都成立的两条

- **H10 / H6 的 definition 条款：四个本地概念全部触发，但不在逐节里重复记。**
  YAML 用 `definition:` 字段，build 输出 `skos:definition`（§6 已记），没有一个带 `owl:equivalentClass`。
  这几句释义说的都是必要条件或说明，不是充要条件，按 H6 应当输出为 `emmo:elucidation`。
  落实 §6 那条 build 改动即可，不需要逐类改 YAML。
- **注释核对（程序规矩 1）发现两处过时或不实的注释**，不影响公理，记在对应概念下：
  `Phase` 那条 VolumeFraction 账里的"后代一个都不受影响"（§3）、`emmo:MaterialByStructure` 那条父类边（§4）。

---

### Crystallography

- 位置：`material.yaml:554`；父类链：`Crystallography ⊑ emmo:Language`
  （`EMMO_d8d2144e_5c8d_455d_a643_5caf4d8d9df8`）`⊑ Symbolic ⊑ DiscreteData ⊑ … ⊑ Data ⊑ Contrast ⊑ Perspective`。
- 关系（§2）：本身没有 restriction。参与的关系只有 10 条入边 is-a，逐条按"子类该不该挂在这里"判（H1/H6）：

  | 子类 | 行 | 释义指的是 | 判定 |
  |---|---|---|---|
  | `CrystalStructure` | 573 | 描述本身（"language construct"） | 通过 |
  | `UnitCell` | 606 | "a periodic unit in a crystal structure"，而 CrystalStructure 在符号侧 | 通过 |
  | `Site` | 645 | 晶胞里的位点，跟着 UnitCell 走 | 通过 |
  | `WyckoffSymbol` | 737 | 符号（letter） | 通过 |
  | `CrystalSystem` | 729 | 名称（"the name of the system"） | 通过 |
  | `FractionalPosition` | 751 | "a position **expressed in** fractional coordinates"，是表达式 | 通过 |
  | `Spacegroup` | 640 | "**the symmetry group** that represents…"，是群本身，不是写下来的符号 | **H6 不过** |
  | `CellVolume` | 719 | "**the volume** of the unit cell"，是量 | **H1 不过** |
  | `SymmetryMultiplicity` | 744 | "**the number** of different sites…"，是量（纯数） | **H1 不过** |
  | `LatticeParameter` | 650 | "**the 6 parameters**…"，是量，而且长度和角度混在一个类里 | **H1 不过** |

  H1 的判法：问 B（能抄下来吗？要看指的是描述还是被描述的东西），后三个的释义指的都是被描述的量；
  再问 C（挂得上恰好一个单位吗？），`CellVolume` 是 m³，`SymmetryMultiplicity` 是 1，所以落在 `Property`（`Quantity`）。
  `LatticeParameter` 把 a、b、c（长度）和 α、β、γ（角度）捆在一个类里，挂不上"恰好一个"单位。
  YAML 在 650 行的 rationale 里写明这是**有意偏离** cryst（cryst 把这几个放在 `PureNumberQuantity` / `RatioQuantity` 那一支），
  理由是"同一份描述的零件不该分居两支"。这个理由可以成立，但前提是这些类指的是**写下来的值**，
  而它们的释义说的是**量**。上游给这件事留好了位置：`emmo:QuantityValue`（`EMMO_f658c301_ce93_46cf_9639_4eace2c5d1d5`）
  的 elucidation 是 "A symbolic that has parts a numerical object and a reference"，它 `⊑ Metrological ⊑ Language`，
  与 Crystallography 同在 Language 下。所以有两条路，**待裁决**：
  (a) 照 cryst 搬到量侧（`Quantity` 的子类）；
  (b) 留在符号侧，释义改成"写下来的值"（例如 "The written value of the volume of a unit cell, as a quantity value."），
  并考虑同时 `⊑ emmo:QuantityValue`。
- 类（§3）：
  - H1：Language 是符号侧，与释义一致，**通过**。
  - H6：释义写的是 "The language of the crystallographic domain"，说的是**整门语言**；
    而 `emmo:Language` 的个体是单个语言对象（"a discrete data entity respecting specific language syntactic rules
    (a well-formed formula)"）。上游的兄弟类就是按个体来写的，例如 `emmo:Chemical`："A language object that
    follows the syntactic rules used in the chemical field."。释义和位置在单复数上对不上，**H6 不过**，应改成
    "A language object that follows the syntactic rules used in crystallography."
  - S-isa：区分条件是"遵循晶体学的语法规则"，与上游 Chemical、Mathematical 的区分口径一致。**通过**（只在释义里，没有公理，与上游同档）。
  - S-exist：不是叶子，有 10 个子类。删掉它，① 会丢掉"取出全部晶体学描述"这个查询；② 10 个子类没有共同的父节点可挂；
    ③ "这是晶体学写法"这个区分会退回注释。**保留**。
  - S-disj：
    - 与上游兄弟类（Chemical、Mathematical、Metrological、ComputerScience）之间：**已声明不互斥**。
      反例：CIF 里的 `0.25 0.25 0.25` 既是晶体学写法，也是数学向量。
    - 10 个子类之间：**未表态，算问题**。YAML 自己记着这个洞（`:2762`，`:692` 引用了它；`:692` 原文写的“第 528–534 行”已过时）：UnitCell、Spacegroup、Site 之间没有
      `disjointWith`，一个个体同时属于三类，HermiT 不报错。至少 `UnitCell`、`Spacegroup`、`Site`、`CrystalSystem`、
      `WyckoffSymbol` 两两之间可以写互斥。如果 H1 那四个按 (a) 搬走，就不在这组兄弟里了。
- 没有边（§4）：
  - **6 个零件和 3 个整体之间没有边，第 3 档（真缺口）。**
    `LatticeParameter`、`CellVolume` 是 `UnitCell` 的零件；`WyckoffSymbol`、`FractionalPosition`、`SymmetryMultiplicity`
    是 `Site` 的零件；`CrystalSystem` 是 `Spacegroup` 的零件。现在 9 个类在一层 is-a 里平铺，部分和整体的关系看不出来。
    想按第 1 档（刻意留空）处理，需要一个真实材料作反例，但这里举不出来：每个晶胞都有晶格参数，
    每个位点都占据某个 Wyckoff 位置（一般位置也算一个 Wyckoff 位置）。
    YAML 650 行不写这些边的两个理由，都不能当第 1 档的反例：
    ① "会加深互斥漏洞"，这是成本论证，不是"连上就错"；② "`=6` 对四方、六方晶系为假"，这只说明不该写基数，
    `∃` 照样为真。
    补边的形制可以照上游 `ChemicalFormula ⊑ ∃hasSpatialTile.ChemicalElement` 来写。
  - **Crystallography 子树与 Phase 一侧，公理层面只有一处连接**，见 Phase 那一节的 §4。
- 探针：无。
- 附带（CrystalStructure，`material.yaml:573`，不在试点内，不下结论）：
  - `hasSpatialTile`（`EMMO_b2282816_b7a3_44c6_b2cb_3feff1ceb7fe`）的 range 是 `SpatialTile`
    （`EMMO_4cf484af_082a_40f5_9f11_930bf4634482`），而 `UnitCell`、`Spacegroup`、`Site` 都不在它之下。
    按 H2 字面判是不过的，但这个判法同样会判上游自己的 `ChemicalFormula ⊑ ∃hasSpatialTile.ChemicalElement`
    （`EMMO_9236d0aa_cb39_43a1_bbdd_6a2a714951c8`）和 `Vector ⊑ ∃hasSpatialTile.Number` 不过。
    `SpatialTile ⊑ Tile ⊑ Reductionistic ⊑ Perspective`，而各个 Perspective 之间没有互斥公理，
    所以"作为瓦片"本来就是由这条关系推出来的身份，不是一个会被填错的类别。**判据缺陷 D1。**
  - H5：把 hasSpatialTile 的 elucidation（"A relation between the whole and one of its tiles, where the tile is only spatially
    connected with the other tiles forming the tessellation"）套到"一份晶体结构描述 → 其中的空间群符号"上，
    读出来是真话：一段 CIF 文本确实可以切成空间群、晶胞、位点几段，互不重叠。
    所以梳理报告观察 6 的疑点（"空间群是对称群，不是空间上的一块"）**不在谓词上，在 `Spacegroup` 的释义上**，
    也就是上表里那一条 H6。
- 结论：**改公理或释义**。依据是 H6，即本类释义的单复数（`material.yaml:556`）。
  另外子树里有三件事待裁决：入边上的 H1（3 个类）和 H6（`Spacegroup`）；S-disj（10 个子类未表态）；
  §4 第 3 档（6 条零件边缺失）。
- 判据缺陷：D1（H2 怎么判视角型 range）。

---

### MicrostructureComponent

- 位置：`material.yaml:2037`；父类链：`MicrostructureComponent ⊑ emmo:Component`（`EMMO_f76884f7_964e_488e_9bb7_1b2453e9e817`）
  `⊑ Role`（`EMMO_4f226cf3_6d02_4d35_8566_a9e641bc6ff3`）`⊑ QualifiedRole ⊑ Holistic ⊑ Perspective`；
  另一条是 `Component ⊑ Constituent ⊑ ObjectByContext ⊑ Object ⊑ Persistence`。
  继承的上游公理：`Component ⊑ ∃hasComponent⁻.HolisticSystem`，`Role ⊑ ∃hasRole⁻.Whole`。
- 关系（§2）：
  - 出 `⊑ emmo:Component`：H5 要求上溯的 elucidation 都成立。
    Component 是 "A constituent of a system"；Constituent 是 "An object which is a spatial part of another object"；
    Role 是 "…contributes to it according to an holistic criterion, where the type of the whole is not the type of the part"。
    晶粒、析出物、孔、晶界各自都是显微组织的空间部分，而且都不是"显微组织"这个类型。**通过**。
  - 入 `Microstructure ⊑ ∃hasComponent.MicrostructureComponent`（`material.yaml:832`）：
    - H2：hasComponent（`EMMO_3c7f239f_e833_4a2b_98a1_c88831770c1b`）的 range 是 `Component`，**通过**。
      domain 是 `HolisticSystem`，Microstructure 经 `HolisticArrangement` 已在其下。
    - H3：两端都在物质或整体视角一侧，**通过**。
    - H5：hasComponent 是 "Relation a holistic system to one of its components"；
      hasRole（`EMMO_8e52c42b_e879_4473_9fa1_4b23428b392b`）是 "…a proper part of the whole that scale down to the point which it
      lose the characteristics of the whole and become something else"，一颗晶粒单独拿出来就不再有显微组织；
      hasConstituent 是 "…one of its holistic part that contributes to the object under some spatial-based criteria"。
      三句都成立，**通过**。
  - 入 is-a × 4（Grain 2083、GrainBoundary 2162、Pore 2167、Precipitate 2172）：每个都有可检验的释义，**S-isa 通过**。
- 类（§3）：
  - H1：问 A（把材料切一半，它也被切一半吗？），会；Holistic 视角按 §3 的表算物质侧。
    本类刻意**不** `⊑ emmo:Material`（mstr 那一版有这个父类，见 rationale）。理由是 Pore 不是"一定量的物质"，
    这正好对上 PMDco 的探针（缺陷和界面是位置，不是物质）。**通过**。
  - H6：释义 "A part (component) of a microstructure…" 与 Component 的位置一致，**通过**。
  - S-isa：相对 Component 的区分条件是"它所在的整体是显微组织"，**只写在释义里**。上游继承的公理只说整体是 `HolisticSystem`。
    mstr 有一条收紧版公理 `∃hasComponent⁻.Microstructure`，本文件没取（rationale："那笔账没量"）。
    按 S-isa，区分条件写在释义里也算通过，但这正是 §4 里的一条缺口。
  - S-exist：不是叶子。删掉它，① 会丢掉 `Microstructure ⊑ ∃hasComponent.MicrostructureComponent` 推出的
    "这是显微组织组件"；② 4 个子类只能直接挂在 Component 下，失去分组；③ "显微组织组件"这个区分只能写进注释。**保留**。
  - S-disj（4 个子类）：**未表态，算问题**。逐对判断如下：

    | 兄弟对 | 判断 | 理由或反例 |
    |---|---|---|
    | Grain / Precipitate | **不互斥** | 反例：奥氏体中析出的先共析晶界铁素体（allotriomorph），既是析出产物，又是一颗取向一致的铁素体晶粒 |
    | Grain / GrainBoundary | 可写互斥 | 晶界是晶粒之间的界面区，不是晶粒的一部分 |
    | Grain / Pore | 可写互斥 | |
    | GrainBoundary / Pore | 可写互斥 | 晶界上的蠕变空洞落在晶界处，但它是另一个区域 |
    | GrainBoundary / Precipitate | 可写互斥 | 同理，晶界析出物坐落在晶界上，但不是晶界本身 |
    | Pore / Precipitate | 可写互斥 | |
- 没有边（§4）：
  - 本类 → `emmo:Material`：**第 1 档（刻意留空）**。反例：真空烧结的 Al₂O₃ 里残余的闭孔，它不是任何一定量的物质。
  - 本类 → `Phase`：**第 1 档**，反例同上，真空闭孔不属于任何相。
    注意：如果孔里有残余气体，按上游 PhaseOfMatter 的 note（"the humid air is a third phase"），那团气体本身就是一个相。
    所以反例只能用真空孔。
  - 本类 → `Microstructure`（部分到整体方向，`∃hasComponent⁻.Microstructure`）：**第 3 档（真缺口）**。
    举不出反例：组件的定义就依赖于它在某个显微组织里，mstr 的 note 原话是
    "single microstructure components does not exists"。整体到部分方向已经有边，这一条补上之后，S-isa 的区分条件就进了公理。
    rationale 不补的理由是"孤立晶粒个体会被强制推出一个显微组织后继，账没量"，这是成本论证，不是反例。
- 探针：
  - **OntoClean 刚性**：Role 是反刚性的，挂在它下面的 `GrainBoundary` 是刚性的吗？
    判据说探针的答案要回到 EMMO 公理里找。EMMO 在 Role 上写的不是模态意义的刚性，而是**存在依赖**：
    `Role ⊑ ∃hasRole⁻.Whole`，再加上 elucidation 里那句 "the type of the whole is not the type of the part"。
    所以问题翻译成：**GrainBoundary 能不能不作为某个异类整体的部分而存在？** 不能，晶界离开两侧晶粒就不存在。
    Grain 也不能：一颗晶粒单独拿出来就是一块单晶，不再是晶粒。Pore 和 Precipitate 同理，
    比如用电解把基体溶掉、取出来的析出物，就成了一个颗粒，不再是析出物。**四个子类都通过。**
    这个翻译是我在审查中做的，判据里没有写，**判据缺陷 D3**。
  - **PMDco 物质/非物质判法**：Pore、GrainBoundary 是位置或界面，不是物质。本类不 `⊑ Material`，与这个判法一致。
- 结论：**保留**，依据 H1、H5、S-exist 全部通过。另有两项建议改，待裁决：
  ① S-disj，给 5 对兄弟类写互斥，Grain/Precipitate 声明不互斥；
  ② §4 第 3 档，补 `MicrostructureComponent ⊑ ∃hasComponent⁻.Microstructure`。
- 判据缺陷：D3。

---

### Phase

- 位置：`material.yaml:997`；父类链：`Phase ⊑ emmo:PhaseOfMatter`（`EMMO_668fbd5b_6f1b_405c_9c6b_d6067bd0595a`）
  `⊑ ContinuumSubstance`（`EMMO_8b0923ab_b500_477b_9ce9_8b3a3e4dc4f2`）`⊑ Substance ⊑ … ⊑ Matter`。
  另外由于 hasProperty 的 domain，本类被推成 `Referent`，再推出 SemioticEntity、Semiotics、Perspective。
- 关系（§2）：
  - 出 `Phase ⊑ ∃hasProperty.VolumeFraction`：
    - H2：VolumeFraction（`EMMO_a8eb87b5_4d10_4137_a75c_e04ee59ca095`）⊑ RatioQuantity ⊑ … ⊑ Property，**通过**。
    - H5：hasProperty（`EMMO_e1097637_70d2_4895_973f_2396f04fa204`）的 elucidation 是 "A semiotic relation that connects a semiotic
      object to a property in a declaration process"，这一句成立。
      **但宾语的 elucidation 套不上**。VolumeFraction 的原文是 "Volume of a constituent of a mixture divided by the sum of volumes of all
      constituents **prior to mixing**"，这是 IUPAC 对混合物的定义。冶金里的相分数是体视学的 V_V，
      即这个相的体积除以**现有**组织的总体积（Delesse 原理）。析出形成的相（例如 Precipitate 所在的那个相）
      **根本没有"混合前"这个状态**。把宾语换进去读："这块 θ′ 相的体积分数，等于它的体积除以混合前各组分体积之和"，
      这不是真话。**H5 不过**。
    - YAML rationale 自己还记着另一处别扭：体积分数是关系量，要相对于一个整体才有意义，公理里没写分母。
      这是同一个毛病的另一面，不另判。
  - 入 `Microstructure ⊑ ≥1 hasPhase.Phase`：
    - H2：range 是 Phase，**通过**。H7：hasPhase ⊑ hasSpatialPart（`EMMO_dc57d998_23db_4d8e_b2cd_f346b195b846`），**通过**。H9：**通过**。
    - H3：两端都在物质侧，**通过**。
    - H5：hasSpatialPart 的原文是 "A proper part of a whole, whose parts always cover the full temporal extension of the whole within
      a spatial interval"，一块组织里的某相物质满足这一句。**通过**。
  - 入 `Precipitate ⊑ ∃isPartOfPhase.Phase`：
    - H2、H7、H9：**通过**。isPartOfPhase ⊑ isPartOf（`EMMO_a8bd7094_6b40_47af_b1f4_a69d81a3afbd`）。
    - H5：isPartOf 只说 "The inverse relation of hasPart"，而且允许改进部分（improper part）。
      析出物是它所属那个相的一部分，**通过**。
    - H4：这条边让 Phase 有了一个析出物作部分。按聚合读法（同一相的全部物质算一个 Phase 个体），不越过下限。
      按连通读法，单颗细小析出物所在的那块相，可能逼近 ContinuumSubstance 的 `n·dV ≫ 1`。
      GP 区是边界情形：一个 GP 区约含 10²～10³ 个原子，有些教材把它当亚稳相（它有 solvus）。
      所以 H4 **只在聚合读法下通过**。读法本身是 isPartOfPhase rationale 里已经记下的待决（报告 51 §8），这里不重复裁决。
  - 入 `Grain ⊑ ∃overlaps.Phase`：H2，overlaps 没有 range，**通过**。H5，overlaps 是 "share at least one of their parts"，**通过**。
    这条边弱，但 Grain 的 rationale 已经说明理由：晶粒可能含有另一相的小颗粒，所以不能说它是某一个相的部分。
    这个理由与上游 mstr 的 note 核对过，一致。
  - 入 is-a `CrystallinePhase ⊑ Phase`（1032）：S-isa 有区分条件（晶态，加一条缺陷公理），**通过**。
- 类（§3）：
  - H1：问 A（把材料切一半，相也被切一半吗？），会，物质侧，**通过**。
  - H6：释义与位置不矛盾，**通过**。
  - **S-isa：说不出区分条件。** 本类的释义 "A region of matter throughout which all physical properties are essentially uniform"
    几乎逐字照搬父类 PhaseOfMatter 的 elucidation："A matter object throughout which all physical properties of a material are
    essentially uniform"。相对父类，唯一多出来的东西是 `∃hasProperty.VolumeFraction` 那条公理，而它的 H5 刚才不过。
    rationale 里另一个候选区分条件是"本类是 token，不是 type"，但 PhaseOfMatter 的个体本来就是 token。
  - H8（人判部分）：本类和上游类近乎同义。H8 字面上是机判（"重新声明"），查不出这种近义重复，**判据缺陷 D4**。
  - S-exist，删掉它、改用 PhaseOfMatter：
    ① 丢掉的推理只有 VolumeFraction 那条义务，以及它带来的 Referent 身份，而那条义务的 H5 不过；
    ② 数据都有地方放：hasPhase 和 isPartOfPhase 的 range、Grain 的 overlaps、CrystallinePhase 的父类，都可以直接改用 PhaseOfMatter；
    ③ 没有哪个区分会退回注释。
    **三问基本答不上来。** 唯一能举出的理由是为将来留一个本地挂钩：rationale 记着"相最该带化学组成"这条待决，
    如果没有本地类，就只能写到上游类身上。这一点又碰到判据缺陷 D2。
  - S-disj：Phase 与上游兄弟类（Fluid、Solid、StateOfMatter、Mixture，都在 ContinuumSubstance 下）之间：**已声明不互斥**。
    反例：一块单相固溶体既是 Phase 也是 Solid。这属于上游的分面结构，不是本文件的责任。
- 没有边（§4）：
  - **Phase 和 Crystallography 子树之间**，公理层面唯一的连接是 `CrystallineMagneticPhase ⊑ ∃hasProperty.MagneticStructure`（1158）。分开看：
    - `Phase` → `CrystalStructure`：**第 1 档（刻意留空）**。反例：Fe–B 金属玻璃的非晶相、液相，都没有点阵，也没有空间群。
    - `CrystallinePhase` → `CrystalStructure`：**第 3 档（真缺口）**。每个晶态相都有一个晶体结构，举不出反例。
      2026-08-22 删掉 `emmo:Crystal` 那个节点时，`∃hasProperty.CrystalStructure` 这条边跟着一起没了，之后一直没有补。
    - 附带（不在试点内）：唯一那条连接本身**按 H2 不过**。MagneticStructure ⊑ CrystalStructure ⊑ Language ⊑ Data，
      不在 `Property` 之下，推理机却会推出"一份磁结构描述是一个 Property"。
      而上游 Property 的 note 说 Property 是**原子的**（"aimed to deliver one and one only aspect"）；
      非原子的那一档是它的兄弟类 `Description`（"A coded that is not atomic"，`EMMO_35d4c439_fcb6_4399_a855_a89a207b41e9`）。
      这正是 legacy 17 号 §4 说的那种静默错误。补 CrystallinePhase 那条边时也会碰到同一个选择：
      谓词该用 `isRepresentedBy` 系，而不是 hasProperty。
  - Phase → 化学组成：rationale 里的待决。没有反例，每个相都有成分，所以是**第 3 档**，与 D2 一起裁决。
- 探针：无。
- 注释核对：VolumeFraction 那条账（1004 起）写着"Phase 的后代一个都不受影响，它们经 emmo:Crystal ⊑ … ⊑ emmo:Material
  早就在闸门内侧了"，但同日 `CrystallinePhase ⊑ emmo:Crystal` 那条父类边已经删掉（见 `:44` 那一节的墓碑）。
  现在后代是经由 Phase 本身拿到 Referent 的，这句注释**已过时**。
- 结论：**降级为参考**（推荐），依据 S-isa（说不出区分条件）、S-exist（三问基本答不上来）、H5（唯一那条公理的宾语释义不符）。
  另一条路是**改公理或释义**：给出真正的区分条件，并把 VolumeFraction 换成能表达"相对于整体的分数"的写法。**待裁决。**
- 判据缺陷：D2、D4。

---

### emmo:Material

- 位置：上游类（`EMMO_4207e895_8b83_4318_996a_72cfb32acd94`），本文件在 `material.yaml:2372` 写了两条公理。
  上游父类：`OrdinaryMatter ⊓ Substance`。elucidation 是 "The class of individuals standing for an amount of ordinary matter substance."
- 审查范围：上游的定义不审，只审 **commagmo 挂在它身上的边**。
- 关系（§2）：
  - 出 `emmo:Material ⊑ ∃hasChemicalComposition.ChemicalComposition`（本地写的）：
    - H2：range 是 ChemicalComposition，**通过**。domain 是 Substance，Material 已在其下。
    - H3：hasChemicalComposition（`EMMO_51f426a6_af4a_4e91_a392_2b0bb635e2d5`）⊑ hasConvention ⊑ isRepresentedBy，是表示关系，不是部分关系。**通过**。
    - H5：hasChemicalComposition 的 "Relates a substance to chemical composition" 成立。往上是 hasConvention 的
      "…connects a declared semiotic object to a conventional sign in a declaration process"，"declared" 这个词看似是问题。
      但 Referent 的上游 note 说 "An 'object' does not exists per se, but it's always part of an interpretation"，
      也就是说，本体里谈到的每一份材料都已经在某个符号过程里了。而且 `∃` 在开放世界下不要求 ABox 里真写出那条断言。
      rationale 举的反例（"一份刚命名、还没写属性的材料"）在 OWL 语义下不构成反例。**通过**。
  - 出 `emmo:Material ⊑ ∃hasProperty.Property`（本地写的）：H2 **通过**（range 就是 Property）。H5 同上，**通过**。
    S-exist 意义上它几乎不加信息：一份物质"有某个属性"。**它实际的作用是把 Material 推成 Referent。**
  - 入 `Microstructure ⊑ emmo:Material`（832）：问 A，显微组织被切一半也是一半，物质侧。
    把 Material 的 elucidation 套进去，"一块样品作为一定量的普通物质"，读得通。**通过**。
  - 入 `emmo:MaterialByStructure ⊑ emmo:Material`（2622）：**与上游不符**。上游是
    `MaterialByStructure ⊑ MaterialByClassicalMaterialsScience`（`EMMO_39348191_08fd_4bb6_9b1e_012d5b2f1ff6`）`⊑ Material`。
    本文件写的是一条**被蕴涵的捷径边**，不是逐字重述，零新增蕴涵，但改写了上游的直接父类。
    文件开头 `:36` 那条 note 说"两个上游节点之间那条 ⊑ 是逐字重述"，指的是 `CrystallineMaterial ⊑ MaterialByStructure`，
    那一条核对过确实是逐字的；**这一条不是**。按 H8 的精神（不复制上游），应删掉或改成逐字的两跳。
    H8 字面上管不管"重述上游的类层级"，不清楚，归入 D2。
- 类（§3）：上游类，H1、H6、S-isa、S-exist 都不由本文件负责。S-disj 同样不适用。
- 没有边（§4）：无值得说明的空缺。
- 探针：无。
- **核心问题不在任何一条判据里：给上游类写公理。** 本文件给上游类写了三条公理：Material 上两条，
  `emmo:CrystallineMaterial ⊑ ∃hasPhase.CrystallinePhase`（2626）一条。任何 import 本模块的下游拿到的上游类都比 EMMO 原版紧。
  rationale 自己记着"要退回本地口径，就铸本地类"，而且这两条公理在 `simulation.yaml` 里还有一份手写副本，要两边同步。
  现有判据只有 H8 管"重新声明"，**没有问到"往上游类上加公理"这个维度**，**判据缺陷 D2**。
- 结论：**改公理**（暂定），依据 D2，判据给不出答案。概念本身（上游类）保留；
  捷径边 `MaterialByStructure ⊑ Material` 按 H8 精神删除。两条本地公理是留在上游类上，还是退回本地类，**待裁决**。
- 判据缺陷：D2。

---

## 判据缺陷汇总（同步记进 `review-criteria.md` §7）

- **D1**：H2 没有区分两种 range。一种是视角型 range，比如 `SpatialTile`、`Tile`、`Role`、`Component`，设计上就是靠关系推出身份的；
  另一种是范畴型 range，比如 `Property`，填错了就是范畴错误。按字面判，上游自己的 `ChemicalFormula ⊑ ∃hasSpatialTile.ChemicalElement`
  也不过 H2。（失效类型：判据给错答案。）
- **D2**：判据没有问到"在上游类上写公理，或者重述上游的类层级"这个维度。H8 只管重新声明类和关系。
  本模块有 3 条写在上游类上的公理，1 条捷径父类边。（失效类型：没问到这个维度。）
- **D3**：OntoClean 刚性探针没有写明怎么翻译成 EMMO 的说法。试点里的翻译是：刚性问题 → 存在依赖
  （`Role ⊑ ∃hasRole⁻.Whole`，再加"整体与部分类型不同"）。（失效类型：给不出答案。）
- **D4**：H8 标的是机判，只能查出同名或同 IRI 的重复，查不出**近义重复**，比如 `Phase` 和 `emmo:PhaseOfMatter`
  的释义几乎逐字相同。近义重复现在要靠 S-isa 加 S-exist 间接兜住。（失效类型：没问到这个维度。）

## 待裁决汇总

| # | 概念 | 问题 | 推荐 |
|---|---|---|---|
| 1 | Crystallography | 释义的单复数（H6） | 改成 "A language object that follows the syntactic rules used in crystallography." |
| 2 | Crystallography 子树 | CellVolume、SymmetryMultiplicity、LatticeParameter 三个类的 H1 | (b) 留在符号侧，释义改成"写下来的值"，并 ⊑ `emmo:QuantityValue`；LatticeParameter 拆成长度和角度两类 |
| 3 | Crystallography 子树 | Spacegroup 的释义说的是群，不是符号（H6） | 改成"写下来的空间群符号" |
| 4 | Crystallography 子树 | 6 条零件边缺失（§4 第 3 档） | 补 `∃hasSpatialTile`，形制照 ChemicalFormula |
| 5 | Crystallography 子树 | 兄弟类之间未表态（S-disj） | UnitCell、Spacegroup、Site、CrystalSystem、WyckoffSymbol 两两互斥 |
| 6 | MicrostructureComponent | 4 个子类之间未表态（S-disj） | 写 5 对互斥；Grain/Precipitate 声明不互斥 |
| 7 | MicrostructureComponent | 部分到整体方向的缺口（§4 第 3 档） | 补 `∃hasComponent⁻.Microstructure` |
| 8 | Phase | 说不出区分条件（S-isa、S-exist），唯一那条公理 H5 不过 | 降级为参考，改用 `emmo:PhaseOfMatter` |
| 9 | Phase 一侧 | CrystallinePhase 与 CrystalStructure 之间缺边（第 3 档）；现有的磁结构边 H2 不过 | 改用 `isRepresentedBy` 系的谓词 |
| 10 | emmo:Material | 上游类上的公理（D2）；捷径父类边 | 先修判据 D2，再裁决；捷径边删除 |
