# material 跨本体对比

2026-10-23。从 material 这个概念出发，看其他材料本体怎么处理它，再定 ComMagMO 的 Material 怎么处理。
**只对比，不改 YAML**；第 4 节的问题等逐条拍板。

对比对象（用户 2026-10-23 确认）：

- EMMO 1.0.4 和三个近亲：mstr（microstructure v0.4.0）、mammos（magnetic-materials v0.0.5）、chameo
- 其他 EMMO 系 domain 本体：battinfo、crystallography、chemical-substance（本地副本 0.14.2）、manufacturing
- BFO 系：pmdco（v3.1.0）、mseo

对比维度：类型还是物质份；父类和所属一侧；分类轴；关系和复用。

文件路径都相对 `~/workplace/commagmo-legacy/reference/`，E 指 `emmo/emmo-inferred-1.0.4.ttl`。
`emmo:X` 按 `skos:prefLabel` 解析。旧报告指 `commagmo-legacy/research/reports/`，只在事实与本地 ttl 一致时引用。

---

## 0 · 我们现在的样子

- 不铸本地 Material，直接用 `emmo:Material`（`EMMO_4207e895_8b83_4318_996a_72cfb32acd94`）。
- 在上游类上写了三条公理：
  - `emmo:Material ⊑ ∃hasChemicalComposition.ChemicalComposition`（`material.yaml:2372`，`simulation.yaml` 有手写副本）
  - `emmo:Material ⊑ ∃hasProperty.Property`（同上）
  - `emmo:CrystallineMaterial ⊑ ∃hasPhase.CrystallinePhase`（`material.yaml:2626`）
- 一条捷径父类边：`emmo:MaterialByStructure ⊑ emmo:Material`（`material.yaml:2622`），上游中间还隔着 `MaterialByClassicalMaterialsScience`。
- 本地 ⊑ `emmo:Material` 的类只有两个：
  - `Microstructure ⊑ emmo:Material ⊓ emmo:HolisticArrangement`
  - `CrystallineMagneticMaterial ⊑ emmo:CrystallineMaterial ⊓ ∃hasPhase.CrystallineMagneticPhase`。
    释义写的是 "A magnetic material with a crystalline structure"，但**没有任何"磁性材料"父类**。
- `hasSimulatedMaterial` 的 range 是 `emmo:Material`。
- 没有 Sample 或 Specimen 类。

## 1 · EMMO 1.0.4 本身

**类型还是物质份：物质份。**
- elucidation 原文："The class of individuals standing for an **amount** of ordinary matter substance"。
  note 举的例子是氮气，同一份氮可以处于任何物态。
- 父类 Substance 的 example 是 "A litre of water"。
- 实例是一份物质，"一种材料"用子类表达。
- E 里没有 Sample、Specimen、PortionOfMatter 类。

**父类：物质侧，不在任何 perspective 之下。**
- 两条父类链：
  - `Material ⊑ OrdinaryMatter ⊑ MatterByType ⊑ Matter ⊑ PhysicalObject`
  - `Material ⊑ Substance ⊑ MatterByStructure / CompositePhysicalObject ⊑ … ⊑ PhysicalObject`
- 它不是角色，也不是质，原版也不在 `Referent` 之下。
- `Substance` 的直接子类有 4 个：ChemicalSubstance、ContinuumSubstance、Material、MesoscopicSubstance。
  也就是说 **`ChemicalSubstance` 与 `Material` 是兄弟类**，`PhaseOfMatter`（⊑ ContinuumSubstance）也不在 Material 之下。
- Material 树里只有一支被拉到了产品或角色那一侧：`ManufacturedMaterial ≡ ManufacturedProduct ⊓ ArtificialMaterial`，
  下面是 `WorkPiece`。

**分类轴：6 个分面并行，彼此之间没有 disjoint 声明。**

| 轴 | 子类 |
|---|---|
| MaterialByClassicalMaterialsScience | → MaterialByStructure（Amorphous / Crystalline → Crystal）；→ MaterialByType（Ceramic / Composite / Metallic / Polymeric） |
| MaterialByCompactness | Compact、Granular → Powder |
| MaterialByOrigin | Natural、Artificial → ManufacturedMaterial → WorkPiece |
| MaterialBySize | NanoMaterial |
| MaterialByForceResponse | **空** |
| MaterialByFunction | **空** |

EMMO **没有 MagneticMaterial**。

**关系：上游 Material 自己没有任何 restriction。**
- 没有属性以 Material 为 domain 或 range。
- 以 Material 子树为填充的 restriction 只有两条：`ManufacturedMaterial` 的等价式，以及 `Manufacturing ⊑ ∃hasOutput.WorkPiece`。
- `hasChemicalComposition`：domain 是 Substance，range 是 ChemicalComposition（符号构造）。
  Material 本来就在这个 domain 里。
- `hasProperty`：domain 是 **Referent**，range 是 Property。
- EMMO 里没有 Microstructure 类。MaterialsProcessing、MaterialTreatment 与 Material 之间也没有公理连接。

## 2 · 各家对比

### 2.1 类型还是物质份

| 本体 | 读法 | 依据 |
|---|---|---|
| EMMO | 物质份 | 见 §1 |
| mstr | 物质份 | Microstructure 的 elucidation："Being nominalistic, the microstructure is the material itself" |
| mammos | 物质份 | Magnet、BulkMagnet 的 elucidation 都是 "Piece of matter"。旧报告 07 §3.1 指出 BulkMagnet 带 "=1 SampleGeometry"，有类型和个体塌缩的味道 |
| chameo | 没有 Material 类 | `Sample`（altLabel Specimen）的定义是 "Portion of material selected from a larger quantity of material"；**⊑ `emmo:Object`，不 ⊑ Material** |
| battinfo、manufacturing | 没有 Material 类 | battinfo.ttl:81 原文是 "No domain terms are defined here"；manufacturing 本地只有过程类和设备类 |
| crystallography | 没有 Material 类 | 只有 `Crystal ⊑ Solid`，是一份物质 |
| chemical-substance | 类是物质种类，实例是一份物质 | 677 个类挂在 `emmo:ChemicalSubstance` 下面，**只有 StainlessSteel 挂在 `emmo:Material` 下** |
| pmdco | 物质份 | `Material`（PMD_0000000）的 altLabel 是 "Portion of Material"，定义是 "a portion of matter … whose shape is not relevant for its participation in the manufacturing process" |
| mseo | 没有 Material 类 | 只有 `Specimen ⊑ iof-core:MaterialArtifact`，属人造物侧 |

**结论：所有铸了或用了 material 的本体都读作"一份物质"。没有一家把 Material 当作"材料种类"的个体。**
"一种材料"在各家都用**类**表达，例如 pmdco 的 `steel`（PMD_0020096）、chems 的 `Iron`。
pmdco 有 `material specification`（PMD_0060007，⊑ directive information entity），但这个类是孤立的。
没有一家把牌号做成信息实体。

**试样和材料的区分方式有三种：**
- chameo：Sample 是另一个 Object，用 `SampleExtraction ⊑ ∃hasInput.Material ⊓ ∃hasOutput.Sample` 连接。
- pmdco：没有 sample 类，只有角色（`Probe-Rolle` PMD_0000919 ⊑ evaluant role）。
  同一个个体可以同时是 object（例如 ingot）和 material（例如 steel），这叫二重性，示例在
  `pmdco/patterns/duality object material/`。两种身份的分工靠两条：
  - extensive 性质挂在 object 上，intensive 性质挂在 portion of matter 上。
  - 形状和加工过程有关，就是 object；无关，就是 material。
- mseo：Specimen 是人造物。

### 2.2 父类和所属一侧

| 本体 | 物质 | 角色 | 质或符号 | 备注 |
|---|---|---|---|---|
| EMMO | ✔ Material | — | — | 只有 ManufacturedMaterial 同时属于 Product 一侧 |
| mstr | ✔ | ✔ | — | `MicrostructureComponent ⊑ emmo:Material ⊓ emmo:Component`，且 `Component ⊑ Role` |
| mammos | ✔ | — | ✔ | 24 个类**显式**写了 `⊑ emmo:Referent`，与 hasProperty 的 domain 对齐 |
| electrochemistry（battinfo 的依赖） | ✔ | ✔ | — | `ActiveMaterial` 和 `Electrolyte` 同时 ⊑ ElectrochemicalComponent（⊑ Component ⊑ Role）与 Material 一侧 |
| chemical-substance | ✔ | 推理出来的 | — | Solvent、Solute ⊑ ChemicalCompound，又经 `isComponentOf` 的 domain 被推成 Role |
| pmdco | ✔ portion of matter ⊑ material entity | 角色挂在 Material 上 | — | matrix / filler / laminate ply role ⊑ ∃role of.Material；Material 本身不是角色 |
| mseo | — | — | — | Specimen 是人造物（IOF MaterialArtifact） |

**结论：大家都把 material 本身放在物质侧。**
- 分歧在"功能性的材料"，例如活性材料、溶剂、基体：
  - EMMO 系 domain 本体做法不一，有的双挂，有的推理出来是角色。
  - pmdco 把角色做成依附在 Material 上的实体。
- 与 ComMagMO 直接相关的副发现：**我们的 `MicrostructureComponent ⊑ emmo:Component`，而 `Component ⊑ Role`**（E 中已核对）。
  所以它在角色侧。它刻意不 ⊑ Material，这和 `review-material.md` 的判断一致；但它是角色这一点，那份文档没写明。

### 2.3 分类轴

| 本体 | 做法 |
|---|---|
| EMMO | 6 个分面并行（§1），其中两个是空的 |
| mstr | 不扩展分类轴。Alloy ⊑ MetallicMaterial，Grain ⊑ CrystallineMaterial |
| mammos | `MagneticMaterial ⊑ MaterialByStructure`（elucidation 原文："Magnetically ordered solids"），`Magnet ⊑ MaterialByFunction`，BulkMagnet / ThinFilmMagnet ⊑ MaterialBySize。mammos 的 `CrystallineMagneticMaterial ⊑ MagneticMaterial ⊓ GranularStructure`，后者 ⊑ CrystallineMaterial |
| electrochemistry | 按电化学功能分（ActiveMaterial、Binder、Electrolyte…）；ManufacturedMaterial 下按形态分（Foil、Mesh…） |
| chemical-substance | 按化学成分和键型分；不碰 Material 的轴 |
| crystallography、manufacturing、chameo | 不适用 |
| pmdco | 15 个直接子类，多个分面并行，而且大量多继承：有序度、化学类别、来源、功能、性质、加工；深度到 5。comment 规定子类按"结构、性能、加工"三方面属加种差。部分子类用 ≡ 定义，可以自动归类 |
| mseo | 没有材料分类，只有 MaterialStructure 按尺度分 |

**磁性材料放在哪：没有共识。**
- EMMO 没有这个类。
- mammos 放在结构轴下。
- pmdco 只有 `magnetic ceramic`（≡ electroceramic ⊓ ∃has disposition.electromagnetic property）和 `magnetic glass`，
  也就是按性质（disposition）定义的。

**pmdco 的反面教训（已在 pmdco.ttl 中核对）：**
- `semiconductor ≡ ∃has disposition.Halbleitfähigkeit`：等价式里没有 Material，任何带这种 disposition 的东西都会被推为 Material。
- `crystalline material` 是叶子，`metal` 没有挂在它下面。
- `superconducting ceramic` 挂在 `magnetic ceramic` 下面。

多分面加 ≡ 定义虽然强，但很容易写错。

### 2.4 关系和复用

**组成、相、显微组织、属性、加工：**

| 本体 | 组成 | 相 / 显微组织 | 属性 | 加工 |
|---|---|---|---|---|
| EMMO | `hasChemicalComposition`（domain Substance），上游没有写成 restriction | PhaseOfMatter 是 Material 的兄弟；没有 Microstructure | `hasProperty`（domain Referent），Material 上 0 条 | 只有 `Manufacturing ⊑ ∃hasOutput.WorkPiece` |
| mstr | `Alloy ⊑ ∃hasProperty.ChemicalComposition`（不用 hasChemicalComposition） | Microstructure ⊑ ∃hasComponent.MicrostructureComponent | 8 条 inverse(hasProperty) only | `CompositionMeasurement ⊑ ∃hasInput.Material` |
| mammos | `MagneticMaterial` 上有 hasProperty =1 ChemicalComposition | 用 hasSpatialPart 连到 MainMagneticPhase | 大量 hasProperty 基数限制 | 把 MaterialsProcessing 当作 hasProperty 的填充（min 0） |
| chameo | — | — | 属性挂在 Sample 上 | SampleExtraction 连接 Material 和 Sample |
| electrochemistry | — | — | **在 emmo:Material 上**写了 4 条 ∃hasProperty（Density、ThermalConductivity…） | — |
| chemical-substance | 只有注解（分子式、InChI） | — | — | — |
| pmdco | chemical composition 是 **quality**（⊑ ∃quality of.(Material ⊓ ∃has part.portion of pure chemical element)）；物质层用 has part 连到各元素那一份；数据层另有 data item 链 | microstructure、phase 是 portion of matter 或 material entity，**与 Material 没有公理连接** | has quality、has disposition、has characteristic | Material ⊑ **∃output of.process**；但 Herstellungsprozess 的输入输出限定为 object ⊔ object aggregate |
| mseo | MaterialComposition ⊑ quality，0 条 restriction | MaterialStructure ⊑ fiat object part | — | — |

**是铸本地 Material 类，还是给上游类加公理：**

| 本体 | 本地 Material 根类 | 以上游类为主语写的公理 |
|---|---|---|
| mstr | 无，直接 ⊑ emmo:Material | 0 条 |
| mammos | 无 | 383 条 subClassOf 写进 EMMO 命名空间，都在单位和数据类上；Material 子树里没有 |
| chameo | 无 | 2 条 disjointWith |
| battinfo | 无，一个类都不铸 | 只对属性写了 prov 映射 |
| electrochemistry | 无 | **`emmo:Material ⊑ ∃hasProperty.{4 种}`**（`electrochemistry-reference.ttl:310`，0.35.0） |
| chemical-substance | 无 | Solution、AqueousSolution、ManufacturedProduct 上有公理；Material 上没有 |
| crystallography、manufacturing | 无 | 0 条 |
| pmdco | **自铸** PMD_0000000 | 给 CHEBI 类加了公理，例如 `chemical substance ⊑ portion of matter` |

**结论：**
- EMMO 系没有一家铸本地 Material 根类。
- 给 emmo:Material 本身写公理的，只有 electrochemistry 和我们。两家写的都是 ∃hasProperty，后果相同：
  上游类对所有下游都被推成 Referent。
- mammos 也是 Referent，但它是在**本地子类**上显式写的。
- ∃hasChemicalComposition 这条，没有任何一家写过。

## 3 · 对 ComMagMO 的含义

1. **"一份物质"这个读法没有争议。**
   - 我们用 emmo:Material，`Microstructure ⊑ Material` 和 `hasSimulatedMaterial` 都按物质份理解，与所有对比对象一致。
   - 旧报告里 Material 是种类还是个体来回翻过三次（07 → 12/13 → sample-restore）。那是旧仓库本地 `mat:Material` 的问题，
     不适用于直接用上游类的现状。
2. **上游类上的公理只有一个先例（electrochemistry），而且后果在那边同样存在。**
   - ∃hasProperty.Property：几乎不带信息（"一份物质有某个属性"），但会把整个上游 Material 推成 Referent。
   - ∃hasChemicalComposition.ChemicalComposition：它自己声明的 domain 是 Substance，与 Material 一致；
     但父谓词 `hasConvention ⊑ isRepresentedBy` 的 domain 是 Referent，所以**它同样会把上游 Material 推成 Referent**
     （`material.yaml` 旧账记的 HermiT 实测：祖先 18 → 22）。它断言"每一份材料都有成分"，
     这句话为真，但 import 我们的下游也会被迫接受。
     （本条初稿写成"不产生新的分类推论"，有误，2026-10-23 改正。）
   - 注意：删掉这两条，不影响在个体上使用这两个属性，hasProperty 的 domain 照样会对用到它的个体推出 Referent。
3. **组成和相：pmdco 与 EMMO 的路线差别最大。**
   - pmdco 的成分是 quality，相和显微组织都与 Material 没有公理连接。
   - EMMO 的成分是符号构造。
   - 我们沿用 EMMO 的做法，不需要向 pmdco 靠拢；但 pmdco 的二重性（同一个体既是工件又是材料）值得记住，
     等将来需要试样或工件时再用。
4. **磁性材料需要一个家。**
   - EMMO 没有 MagneticMaterial，MaterialByFunction 是空的。
   - mammos 放在结构轴下，pmdco 按性质（disposition）定义。
   - 我们的 `CrystallineMagneticMaterial` 释义里说"a magnetic material"，却没有对应的父类。
5. **化合物不在 Material 下。**
   - chems 的化合物（例如将来可能复用的 Fe3O4）在 `emmo:ChemicalSubstance` 下，是 Material 的兄弟。
   - 复用它们时，我们写在 Material 上的公理够不到它们。
   - 反过来，如果在 Material 下另铸同名类，就和 chems 重复了。
6. **试样：目前不在范围内。**
   - EMMO 1.0.4 和 EMMO 系 domain 本体里，只有 chameo 有 Sample（⊑ Object，不 ⊑ Material）。
   - 将来需要时，直接复用 chameo:Sample + SampleExtraction 即可。

## 4 · 待裁决（已于 2026-10-23 裁决，见 §5）

下表是 grilling 之前的初稿，保留作记录。裁决结果以 §5 为准：M1–M5、M7 按推荐；
M3 的理由更正见 §3 第 2 条；M6 选了 (d) 的变体，即铸 MagneticMaterial，但直接挂 emmo:Material，
不挂 MaterialByFunction（§5 H7）。

| # | 问题 | 选项 | 推荐 |
|---|---|---|---|
| M1 | Material 的读法 | (a) 沿用 EMMO 的"一份物质"，种类用子类表达；(b) 另铸种类级的本地类 | (a)。所有对比对象一致 |
| M2 | 铸不铸本地 Material 根类 | (a) 不铸，直接用 emmo:Material；(b) 铸 `commagmo:Material ⊑ emmo:Material` 承载本地公理 | (a)。EMMO 系没有先例；需要承载的公理见 M3 |
| M3 | 上游 Material 上的两条公理 | (a) 保留；(b) 两条都删；(c) 只留 ∃hasChemicalComposition | (b)。∃hasProperty 几乎不带信息，却把上游类推成 Referent；∃hasChemicalComposition 只断言"有成分"，又强加给所有下游。删掉后两个属性照样能用。simulation.yaml 的副本一起删 |
| M4 | `emmo:CrystallineMaterial ⊑ ∃hasPhase.CrystallinePhase` | (a) 保留；(b) 删除，因为 CrystallineMagneticMaterial 已经有 ∃hasPhase.CrystallineMagneticPhase | (b) |
| M5 | 捷径边 `MaterialByStructure ⊑ Material` | 删除 | 删除（review-material.md 已经给出同样的推荐） |
| M6 | 磁性材料放在哪 | (a) 铸 `commagmo:MagneticMaterial ⊑ emmo:MaterialByFunction`；(b) 照 mammos 放在 MaterialByStructure 下；(c) 直接复用 mammos:MagneticMaterial；(d) 暂不铸，只修 CrystallineMagneticMaterial 的释义 | 待议，见下文 |
| M7 | 试样和工件 | (a) 现在不建，需要时复用 chameo:Sample；(b) 现在就建 | (a) |

M6 的说明：
- (c) 会带进 mammos 钉的 EMMO 1.0.3，以及 Referent 和 =1 基数限制，不推荐。
- (a) 和 (b) 的区别在于"磁性"是功能还是结构：
  - 磁有序本身是一种物理状态，离结构轴更近。
  - "软磁材料""永磁材料"是按用途分的，属于功能轴。
- 如果铸 MagneticMaterial，`CrystallineMagneticMaterial` 应当同时 ⊑ MagneticMaterial 和 emmo:CrystallineMaterial，
  与 mammos 的形状一致。

## 5 · 决议（grilling，2026-10-23）

用户在讨论 Material 之前先把树根上移到本体目标。以下逐条由用户拍板，均已落实（I1 维持现状，只改 README）。

### 本体目标

| # | 问题 | 决议 |
|---|---|---|
| G1 | 本体要回答什么 | 核心是**单次模拟的记录**和**多尺度链路**；PSPP 作为组织框架；跨数据源对齐只保留现有的 ModelValidation，不扩展 |
| G2 | PSPP 哪几段 | S→P 全做；P→S 只做"模拟工艺"，即相场模拟的输入参数和组织演化，真实工艺不建实体；Performance 只到材料级品质因数（(BH)max、Hc、Br、损耗），作为 Property 的子类；器件不进来 |
| G3 | 多尺度怎么分 | 两条正交轴：尺度挂在单个模型上，耦合方式挂在多模型模拟上。这一版只认真做顺序（层级）耦合，并发耦合只保留 EMMO 类名 |
| G4 | 尺度按什么定义 | 按模型里的实体（RoMM / EMMO），长度和时间数值只作注解 |
| G5 | 材料在各尺度怎么展现 | **两层并存**：物质侧是材料和它的结构层级（相、晶粒、缺陷、磁畴，即 PSPP 的 S）；符号侧是各尺度模型的表示（超胞、原子构型、网格、场）。**Material 在物质侧，是各尺度模型共同的指称对象**。（§6 K5 补充）物质侧只放实际存在的或被提议制造的物质；无限大、周期性、0 K、无缺陷等理想化都是模型假设，属于符号侧，由边界条件、原子构型、晶体结构和温度设置记录 |
| G6 | 跨尺度参数怎么传 | 铸 `ScaleBridging ⊑ emmo:DataProcessing`，换算公式归这一步；直接照搬的情况算恒等桥接 |
| G7 | 整条链要不要容器 | 铸 `MultiscaleSimulation ⊑ emmo:Simulation`；与 LinkedModelsSimulation 的关系只写注释 |

### Material

| # | 问题 | 决议 |
|---|---|---|
| H1 | 被模拟的材料可以不存在吗 | 可以，但只限**尚未制成的、被提议的材料**（§6 K2 收窄）；理想化不算在内（§6 K1）。不另设计算样品 |
| H2 | 链里每次模拟指向哪份材料 | 各自指向它所计算的那份（真实的或被提议的）物质：DFT 通常指向某个相，例如主相；微磁指向显微组织（§6 K5 改写，原文是「DFT 指向理想晶体」） |
| H3′ | "NdFeB"这类种类 | **属于 ABox，不放进 TBox**；种类本身不建实体。（§6 L2–L4 改写）**相的种类 = 名义成分 + 晶体结构**，由共享的具名符号个体表达（`hasNominalComposition` 与 CrystalStructure），只放在相这一层；材料层面的种类（工艺 + 组织，例如烧结磁体牌号）留待将来升级。原文是「由共享的 `ChemicalComposition` 个体表达」 |
| H4 | 本地 Material 根类 | 不铸，直接用 `emmo:Material` |
| H5 | 捷径边 `MaterialByStructure ⊑ Material` | 删除 |
| H6 | `CrystallineMaterial ⊑ ∃hasPhase.CrystallinePhase` | 删除 |
| H7 | 磁性材料 | 铸 `MagneticMaterial ⊑ emmo:Material`，不挂任何分面；释义写"能出现自发长程磁有序"；本版不写公理。`CrystallineMagneticMaterial` 同时 ⊑ MagneticMaterial 和 emmo:CrystallineMaterial |
| H8 | 试样和工件 | 现在不建；接实验数据时复用 chameo:Sample 和 SampleExtraction |
| H9 | 上游 Material 上的两条公理 | 两条都删，`simulation.yaml` 里的副本一起删。"材料必须写成分"交给 SHACL |
| H10 | 理想晶体和磁体主相的关系 | （§6 L1 改写）**链内各步经部分关系落在同一块材料上**：MultiscaleSimulation 的子模拟指向这块材料的显微组织或它的部分（如主相）；外来、被复用的结果不是子模拟，只经 ScaleBridging 的数据流进来。原文是「不直接连，靠共享成分和桥接链关联」，其前提已被 K1 推翻 |

### 收尾

| # | 问题 | 决议 |
|---|---|---|
| I1 | 微磁模型的尺度 | **维持 emmo:MesoscopicModel**。此前按"G4 微磁应为连续"批准的 ContinuumModel 作废：`simulation.yaml` 的 MicromagneticModel 节点记有 RoMM（§3.4 列在 Mesoscopic 章，正文称 "the mesoscopic formalism"）和 OSMO（M.5 在介观的 disjointUnionOf 里）三条证据。README 补一句：微磁用连续场形式，但按 RoMM/OSMO 归为介观 |
| I2 | 模型侧和物质侧要不要单独连边 | 不加；模拟个体就是连接点（hasMaterialsModel / hasSimulatedMaterial / hasDiscretisation） |
| I3 | SHACL | 本轮只记为待办 |

### 待办

- SHACL：被模拟的材料必须写 hasChemicalComposition（H9 / H3′）。
- 并发耦合（G3）、真实工艺端（G2）、种类实体的升级条件（H3′）。
- ScaleBridging 的换算方法要不要写成公理（候选 `isRepresentedBy some emmo:Equation`）。
- MultiscaleSimulation 要不要同时 ⊑ emmo:SerialWorkflow。
- MagneticMaterial 的公理化，前提是先有表示磁有序倾向的类。
- 新加的类没有用 HermiT 测过：本机没有 Java 运行时。
- 点、线、面三档缺陷从 CrystallographicDefect 下解绑，改成直接 ⊑ Defect（§6 J8）。
- 畴壁分隔畴的边：将来要写就用 ≥1，不用 =2（§6 J11）。
- SHACL：`hasSimulatedMaterial` 的宾语必须显式声明为 emmo:Material，且不能是 Data，防止误填超胞等表示（§6 K4）。
- 材料是已存在还是被提议：将来接实验数据（H8，chameo:Sample）时再考虑（§6 K3）。
- SHACL：`hasNominalComposition` 的宾语和用作种类键的 CrystalStructure 必须是具名 IRI，不能是空白节点（§6 L3）。
- SHACL：MultiscaleSimulation 子模拟的被模拟材料，须是整链材料本身或它的部分（§6 L1）。
- 相的种类不铸实体，「种类相同」只能靠两个键的个体同一性判；需要时再考虑升级（§6 L2）。

## 6 · 挑刺（2026-10-26）

对 §5 决议逐个靶子挑刺。每条由用户拍板。

### 靶子 5：物质侧的结构层级（G5）

起因：G5 说物质侧有一个结构层级（相、晶粒、缺陷、磁畴），但这些类在 TBox 里挂在 EMMO 的不同分支下：
Phase ⊑ PhaseOfMatter（Substance），Grain 等 ⊑ emmo:Component（Role ⊓ Constituent，没有 Matter 祖先），
缺陷 ⊑ SpatialContrast（Contrast），而 MagneticDomain ⊑ CrystallineMagneticPhase，即把磁畴当成了相。
核对过：EMMO 1.0.4 里 Substance、Role、Contrast 之间没有任何互斥公理（disjointWith、AllDisjointClasses、disjointUnionOf 都查了），
同一个个体可以同时属于多个视角。

| # | 问题 | 决议 |
|---|---|---|
| J1 | 结构层级在 TBox 里靠什么成立 | **以 Microstructure 为根的部分关系图**（hasPhase、hasComponent 等），父类按 EMMO 视角分开挂，不要求共同祖先。没接进这张图的结构特征算缺口。这一条是对 G5 的补充 |
| J2 | 磁畴是不是相 | **不是。** 畴壁两侧是同一个热力学相；畴壁扫过原子全换、畴还是那个畴；继承来的「必含缺陷」与「畴内均匀」相悖；TopologicalDefect ⊓ MagneticDomain 挡不住 |
| J3 | 相上的两条「必有缺陷」公理 | **都删。** ∃hasTopologicalDefect 对单畴、饱和样品是假话。∃hasCrystallographicDefect 原先的理由是与理想晶体冲突，已被 K1 取代（理想化移到模型侧后，真实相在 T > 0 下确实含平衡空位）；**维持删除的理由改为**：这条 ∃ 只推出一个匿名缺陷，回答不了任何问题，与 H9 同理（§6 K7）。有没有缺陷交给 ABox |
| J4 | CrystallinePhase 要不要恢复 ⊑ emmo:Crystal | **不恢复**（legacy v1.2.0 起就没有这条边），只订正 rationale 里过时的说法 |
| J5 | 磁畴挂到哪里 | `MagneticDomain ⊑ MicrostructureComponent ⊓ ∃overlaps.Phase`。用 overlaps 而不用 isPartOfPhase，是因为纳米复合磁体里一个畴可以跨相；填充用 Phase 而不用 CrystallineMagneticPhase，是因为非晶软磁也有畴 |
| J6 | 晶粒没有 Matter 祖先算不算缺口 | **不算。** 晶粒长大时原子会换掉，同一性不靠物质承载，和磁畴是同一条理由 |
| J7 | 晶界要不要同时 ⊑ PlaneDefect | **要**：`GrainBoundary ⊑ MicrostructureComponent ⊓ PlaneDefect`。不补 mstr 的 PhaseBoundary 链（同相晶粒之间的晶界不是相界） |
| J8 | 点、线、面三档缺陷从 CrystallographicDefect 下拆出来 | 本版不拆，记为待办。G1 的核心问题用不到「缺陷是几维的」 |
| J9 | 要不要铸 MagneticDomainStructure 容器 | **不铸**，它的角色由 Microstructure 承担 |
| J10 | 畴壁要不要 ⊑ MicrostructureComponent | **要**，补上它没有宿主的缺口，和晶界对称 |
| J11 | 畴壁「恰好分隔两个畴」的边 | 本版不铸。360° 畴壁两侧可以是同一个畴，闭合畴里一面畴壁可以邻接多个畴，所以将来写也用 ≥1 |
| J12 | 畴壁是否都是拓扑缺陷 | **不是。** 180° 畴壁（单轴，π₀ = ℤ₂）是，360° 畴壁拓扑平凡。改成 `MagneticDomainWall ⊑ Defect ⊓ MicrostructureComponent`，释义里去掉 "topological"；TopologicalDefect 的 SCOPE 注释同步修改 |

落实：都已写进 `material.yaml`，没有新增类或谓词，`build.py --check` 通过。改动过的类都**没有经过 HermiT 实测**，因为本机没有 Java。
rdflib 核对过：MagneticDomain、MagneticDomainWall、GrainBoundary 的祖先里都有 MicrostructureComponent，
CrystallinePhase 和 CrystallineMagneticPhase 上已经没有缺陷公理。

### 靶子 1：假设材料放在物质侧（H1 与 G5 的冲突）

起因：EMMO 的 Material 是「一份普通物质」，而 EMMO 是唯名论的 4D 本体，个体都是实际存在的时空实体，
其中没有表示假设物理对象的类（唯一的 `Hypothesis` 是 Theory，属于符号侧）。H1 和 H2 却让「无限大、0 K、无缺陷的理想晶体」
成了一个 Material 个体。可参照的另外两家：CMSO 的 Material 注释写着 "a theoretical entity and not necessarily a tangible object"，
并另设 `ComputationalSample`（"a representative system of a material"）；EMMO 的 Referent 释义说 object 总是相对于一次解释而言。

| # | 问题 | 决议 |
|---|---|---|
| K1 | DFT 模拟的对象是什么 | **真实的那份材料或相**（例如某块烧结磁体的 Nd₂Fe₁₄B 主相）。无限大、周期性、0 K、无缺陷都是模型假设，放在符号侧（PeriodicBoundaryCondition、AtomicConfiguration、CrystalStructure、温度设置）。不采用 CMSO 的 ComputationalSample |
| K2 | 确实还不存在的材料 | 仍然是一个 emmo:Material 个体。H1 收窄为「可以是尚未制成的、被提议的材料」 |
| K3 | 要不要记录「已存在 / 被提议」 | **不记录。** ModelValidation 的参考值可以来自文献或另一种方法，用不上这个区分。记为待办，等接入实验数据时再考虑 |
| K4 | 防止把超胞等表示填进 hasSimulatedMaterial | 交给 SHACL：宾语必须显式声明为 emmo:Material，且不能是 Data。TBox 不加互斥（核对过，EMMO 里 Material 和 Data 的各级祖先之间都没有互斥公理；本机也跑不了 HermiT） |
| K5 | G5 和 H2 的措辞 | G5 补一句「理想化属于符号侧」；H2 改为「DFT 通常指向某个相，微磁指向显微组织」；H10 标为前提失效，留给靶子 2 |
| K6 | DFT 指向一个相时，hasSimulatedMaterial 的 range | **接受推断**：相个体会被推成 emmo:Material。EMMO 说 Material 可以是连续体物质，相和 Material 之间也没有互斥。不放宽 range，不另铸 hasSimulatedPhase |
| K7 | J3 的依据被 K1 削弱，要不要恢复 CrystallinePhase ⊑ ∃hasCrystallographicDefect | **不恢复**，J3 的理由已更正（见上） |

落实：只改了 rationale，公理没有变化。`simulation.yaml` 改的是 hasSimulatedMaterial，`material.yaml` 改的是 CrystallinePhase 删除缺陷公理那一段。

### 靶子 2：用成分代替「种类」（H3′、H10、H2）

起因：H3′ 用共享的 ChemicalComposition 个体给材料分组，但同一成分可以对应不同的种类：FePt 的 L1₀ 相是硬磁，A1 相是软磁；
MnBi 有低温相和高温相；同名义成分的 Nd-Fe-B 有烧结和热变形两种。另外，EMMO 的惯用写法是每份物质各写一组成分
（空白节点，上游甚至推荐一个组分挂一条），并没有共享成分个体的写法。H10 的前提也已被 K1 推翻。
核对过：emmo:ChemicalComposition 完全在符号侧（祖先有 Language、Data，没有 Matter），所以拿它做分组键并不越界，用描述来分组本来就合理。

| # | 问题 | 决议 |
|---|---|---|
| L1 | 链上各步在物质侧怎么关联 | **部分关系**：只有专门为这块材料做的模拟才算 MultiscaleSimulation 的子模拟，它们指向这块材料的显微组织或它的部分（如主相）。外来、被复用的结果（如文献中的 K₁）不是子模拟，只作为 SimulatedProperty 进 ScaleBridging。这条规则只是约定，OWL 写不出来，记入 SHACL 待办 |
| L2 | 跨链的种类分组用什么做键 | **名义成分 + 晶体结构**（相的种类的经典判据），两者都是共享的具名符号个体。材料层面的种类仍然留待将来升级 |
| L3 | 怎样保证分组键真的被共享 | 铸 `hasNominalComposition ⊑ emmo:hasChemicalComposition`，range 是 `emmo:TotalComposition`，不写 domain，以便和实测成分区分（实测成分仍用父谓词）。具名约束交给 SHACL。晶体结构不另铸谓词 |
| L4 | 种类查询落在哪一层 | **只在相这一层。** 磁体整体的名义成分（如烧结磁体约 Nd₁₄Fe₇₉B₇）不是种类键 |

落实：`material.yaml` 新增谓词 hasNominalComposition 和上游引用节点 emmo:TotalComposition，Phase 的 rationale 补了相的种类说明；
`simulation.yaml` 在 MultiscaleSimulation 的 rationale 里补了 L1 的规则；README 里 material 模块的对象属性数从 4 改为 5。新增的谓词**没有经过 HermiT 实测**。

## 附 · 核对记录

以下说法在本 session 中直接对 ttl 查询核对过，不只依赖子报告：

- `emmo:Component ⊑ Role ⊓ Constituent`（E）
- `Substance` 的 4 个直接子类
- `hasProperty` 的 domain 是 Referent，`hasChemicalComposition` 的 domain 是 Substance（E）
- MaterialByFunction 和 MaterialByForceResponse 没有子类；E 里没有任何 label 匹配 magnetic material
- electrochemistry 在 `emmo:Material` 上写的 4 条 ∃hasProperty（`electrochemistry-reference.ttl` 第 310 行起）
- mammos 中 MagneticMaterial、CrystallineMagneticMaterial、GranularStructure、Magnet 的父类
- pmdco 中 semiconductor、magnetic ceramic、crystalline material、metal、microstructure、chemical composition、
  Herstellungsprozess 的公理
