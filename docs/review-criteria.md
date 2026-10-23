# 概念与关系的审查判据

2026-10-23 定稿。审查 `ontology/src/*.yaml` 里的每一个概念时，都按本文逐条过一遍。
审查结果另写（`docs/review-material.md` 等），不写进本文。

文中"legacy NN 号"指归档仓库 `Daimian/commagmo-legacy` 的 `research/reports/NN-*`。

## 0 · 总则

**裁决依据是 EMMO 自己的公理和 elucidation。** commagmo 是 EMMO 的 domain 本体，硬约束只能来自 EMMO。
OntoClean、OOPS!、BFO/PMDco 的判法只当**探针**：它们能提出问题，但答案要回到 EMMO 的公理里去找。

**判据分两层**：

- **硬约束（H）**：违反就是错，必须改。
- **软偏好（S）**：违反了要记账，并写出权衡理由；理由站得住，可以不改。

每条判据都标明**机判**（脚本可查）或**人判**；人判的判据附一个操作问法。

**判据分三组**：§2 关系、§3 类、§4 两个概念之间为什么没有边。审查一个概念时三组都要过，
顺序是**先看它参与的关系，再看它本身**（legacy 17 号：关系先定，类跟着定）。

## 1 · 程序规矩

1. **注释不采信。** YAML 里 `rationale`/`comment` 写的理由，要对着上游 ttl 实际核对过才算数。
   legacy 12 号推翻的那几条结论，恰恰都是注释里写着、事实却相反的。
2. **上游 elucidation 必读。** 每个父类、每个谓词，都要读它在上游的原文，看那句话管着什么。
   逻辑一致不等于对：`∃hasInput.emmo:Material` 推理机零报错，却是范畴错误，因为 `hasInput` 继承自
   `overlaps`，要求两端共享部分。这类错只有读 elucidation 才能发现（legacy 26 号 §3）。
3. **判据不过就先记账。** 审查中遇到判据给不出答案，或者问错了维度，记进 §7"判据缺陷"，
   不在审查中途临时改判据。失效有三种（legacy 44 号）：判据判对了但本体没有类可挂；
   判据给不出答案；判据根本没问到这个维度。

## 2 · 关系判据

### 硬约束

**H2 range 合规**（机判）。每条 restriction 的填充类，都必须落在谓词的 range 内；
range 沿 `subPropertyOf` 继承并取交。
`Property` 与 `Object`/`Process` 之间没有互斥公理，所以填错了推理机不报错，
只会悄悄推出"某个制造过程是一个原子符号"（legacy 17 号 §4，mammos 86 个填充类里有 6 个不合格）。

**H3 parthood 不跨侧**（人判）。parthood 类谓词（`hasPart` 系、`hasSpatialPart` 系）的两端必须同在
物质侧，或同在符号侧。跨侧只能用 `isRepresentedBy` 系的表示关系。
问法：**能说"这份 CIF 是这块相的一部分"吗？** 不能，那就是表示，不是切分
（legacy 17 号 §5 断点一、33 号 §1.3）。

**H4 不越过粒度下限**（人判）。`emmo:ContinuumSubstance` 的后代（例如 `Phase`）带着 `n·dV ≫ 1` 这条父类公理，
不能切到只含几个原胞的尺度。物质侧的切分到连续介质下限为止，原胞和原子是另一层 tessellation
（legacy 17 号 §5 断点二）。

**H5 谓词语义与 elucidation 相符**（人判）。谓词一路上溯到的每个上游 elucidation，对这条边都必须成立。
问法：**把上游那句 elucidation 里的主语和宾语换成这条边的两端，读出来是真话吗？**

**H7 新谓词的父属性**（机判）。新铸的对象属性，必须是 EMMO Core 里某个 mereotopological 或 semiotical
关系的子属性（EMMO governance，"EMMO conventions"）。

**H9 单一 domain/range**（机判）。一个属性最多一条 `rdfs:domain`、一条 `rdfs:range`。
有多条时 OWL 按交集来读，会悄悄收窄范围（OOPS! P19）。

**OOPS! 的逻辑性错误**（机判，均为 critical）：P05 逆关系写错、P14 `allValuesFrom` 误用、
P15 "some not" 与 "not some" 混用、P27 错误的等价属性、P28 错误的对称性、P29 错误的传递性。

### 软偏好

**S-dr domain 与 range 不过度特化**（人判，OOPS! P18）。声明了 domain，主语就会被自动推断成那个类型；
domain 过窄，等于给数据强加一个假类型。
**缺 domain 不算问题**：EMMO 1.0.4 的 246 个对象属性中，116 个没有 domain，94 个连 domain 带 range 都没有，
其中包括 `hasPart`。OOPS! P11（缺 domain/range）、P13（缺逆关系）**豁免**：EMMO 不声明逆关系，用 `inverse(hasX)`。

**S-iso 无孤立元素**（机判，OOPS! P04）。没有任何关系边的类要过 §3 的存在性三问。

## 3 · 类判据

### 硬约束

**H1 视角唯一**（人判）。一个类只能站在一侧。两侧都需要，就拆成两个类。
按顺序跑以下三问，命中即停（legacy 17 号 §3）：

| 判据 | 操作问法 | 命中则 |
| --- | --- | --- |
| A | 把材料切一半，它也被切一半吗？ | 物质侧（`Holistic`/`Matter`），用 mereological 关系，不用 `hasProperty` |
| B | 能抄下来吗？写在纸上、存成文件而内容不变？要看这个类指的是**描述本身**还是**被描述的东西** | 符号侧（`Data`/`Language`），用 `isRepresentedBy` 系 |
| C | 挂得上恰好一个单位、测量程序或标准物质吗？ | `Property`，用 `hasProperty`；值和单位在 Data 侧，不能塞进 Property 的位置 |

反例：`MagneticStructure` 原先既当理想磁序用，又当实际畴构型用，后来拆成 `MagneticStructure`（符号侧）
与 `MagneticDomainStructure`（物质侧）。

**H6 释义与位置一致**（人判）。释义说的东西不能和它在层级里的位置矛盾。
反例：PMDco 的 `unit cell` 释义写着 "smallest volume element"，却直接挂在 `immaterial entity` 下（legacy 33 号 §7）。
**声称是 definition（充要条件），就必须有 `owl:equivalentClass`**；只是说明的，用 elucidation。

**H8 不复制上游**（机判）。不得重新声明 EMMO top/mid 层已有的类或关系（EMMO governance，"Domain Ontologies"）。

**H10 有 elucidation**（机判）。每个类至少带 `emmo:elucidation`、`emmo:definition`、`emmo:conceptualisation` 之一，
这是 emmocheck `test_description` 的要求。当前 build 输出的是 `skos:definition`，见 §6。

**OOPS! 的层级错误**（机判，均为 critical）：P06 类层级成环，P31 错误的等价类。

### 软偏好

**S-isa 类属加种差**（人判）。子类相对父类，必须有一条能说出来的区分条件：要么是一条公理，
要么是释义里一个能检验的条件。说不出区分的子类就是"凑数的 is-a"，转去过 S-exist。
相关的还有 OOPS! P17（层级过度特化）。

**S-exist 存在性三问**（计数可机判，裁决靠人判，legacy 12 号 §7）。删掉这个类：

1. 会丢掉什么推理？
2. 什么数据会无处安放？
3. 什么区分只能退回注释里？

三问都答不上来，就是凑数的类。**没有公理的叶子类**，要同时满足下面两点才保留：
① 上游没有现成的类可以直接拿来打标签；② 能说出一个具体的数据落点（一个能力问题，或者论文、代码里的一个真实字段）。
满足不了就**降级为参考**：类名和释义写进父类注释，消费方直接用上游 IRI。

**S-disj 兄弟类互斥**（人判，OOPS! P10）。没有互斥公理的本体几乎不可证伪：推理机找不到可以矛盾的东西
（legacy 57 号 §5.3）。每组兄弟类记为三档之一：

- **可推出互斥**：由公理导出，或已声明 `disjointWith`。
- **已声明不互斥**：配一个两者重叠的实例作反例。
- **未表态**：只有这一档算问题。

### 探针（不裁决）

- **OntoClean 刚性约束**：反刚性（~R）的类不能包含刚性（+R）的类。
  例：`MicrostructureComponent ⊑ Role`，而 Role 是反刚性的，那么挂在它底下的 `GrainBoundary` 是刚性的吗？
- **OntoClean unity 约束**：父类带 unity 判据，子类必须带同一个；反 unity（~U）的类不能包含 +U 的类。
- **PMDco 的物质/非物质判法**（legacy 33 号）：任一时刻是否以物质为部分；缺陷是位置和界面，不是物质。

OntoClean 原文用模态逻辑定义刚性（Guarino & Welty, *Handbook on Ontologies*, 2009, pp. 201–221）。
用到 EMMO 这种 4D 唯名论本体上没有文献支撑，所以只用来提问。

## 4 · "没有边"的判据

两个概念之间没有边，要先说清是哪一档（legacy 12 号 §6.2）：

| 档 | 含义 | 必须附上 |
| --- | --- | --- |
| 0 可推出的互斥 | 两者不相容 | 推导链（例：`Data ⊥ NonEncodedContrast` ⟹ `Defect ⊓ CrystalStructure = ⊥`） |
| 1 刻意留空 | 连上就是错的 | **一个真实材料作反例**（例：铜有微结构但没有畴结构） |
| 2 经路径可达 | 直接连是冗余 | 那条路径 |
| 3 真缺口 | 该连而没连 | — |

**拿不出推导链、反例或路径的，一律归第 3 档。** 物理上站不站得住，用材料学知识核实。

另一种排斥是**释义层面的排斥**：释义明文排除了某类对象（例：`MagneticStructure` 写着 "ideal, periodic"，
所以无序磁态不在其内）。这算一种判定，不是遗漏。

## 5 · 审查结论

每个概念的结论取以下五种之一：

| 结论 | 通常由哪条判据触发 |
| --- | --- |
| 保留 | 全部通过 |
| 改公理或释义 | H2–H6、H9、H10，S-dr |
| 拆分 | H1 |
| 降级为参考 | S-exist、H8 |
| 删除 | S-exist 三问全空，且没有可保留的论证 |

每条结论都写明**由哪条判据导出**，引用到 YAML 行号或上游 IRI。

每个概念一节，按以下格式：

```
### <概念>
- 位置：<yaml 行号>；父类链：…
- 关系（§2）：逐条边，标 H2/H3/H5/H7/H9 的结果
- 类（§3）：H1 归属、H6、S-isa、S-exist、S-disj 的结果
- 没有边（§4）：值得说明的空缺各属哪一档
- 探针：提出了什么问题，在 EMMO 里怎么裁决的
- 结论：<五选一>，依据 <判据编号>
- 判据缺陷：（如有，同时记进 §7）
```

## 6 · 尚未落实

- build 当前把 YAML 的 `definition` 输出为 `skos:definition`（`tools/commagmo_build/emit.py:139`），过不了 H10。
  计划改为默认输出 `emmo:elucidation`，只有带 `equivalentClass` 的类才输出 `emmo:definition`。
- 机判条目（H2、H7、H8、H9、H10、OOPS! 的逻辑性与层级错误、S-iso）还没有接进 `build.py --check`。

## 7 · 判据缺陷

审查中发现判据给不出答案或问错维度时，记在这里。

以下四条来自 2026-10-23 的 material 试点（`docs/review-material.md`），**尚未修订判据**。

- **D1 · H2 没有区分两种 range（判据给错答案）。** 一种是视角型 range，比如 `SpatialTile`、`Tile`、`Role`、`Component`，
  身份本来就是由关系推出来的，而各个 Perspective 之间没有互斥公理；另一种是范畴型 range，比如 `Property`，填错了就是范畴错误。
  按 H2 字面判，上游自己的 `ChemicalFormula ⊑ ∃hasSpatialTile.ChemicalElement` 也不过。
- **D2 · 没有问到"在上游类上写公理"（没问到这个维度）。** H8 只管重新声明类和关系。
  本模块在上游类上写了 3 条公理（`emmo:Material` 两条，`emmo:CrystallineMaterial` 一条），
  还有 1 条捷径父类边（`MaterialByStructure ⊑ Material`，上游实际要经过 `MaterialByClassicalMaterialsScience` 这一跳）。
- **D3 · 刚性探针没有写明怎么翻译成 EMMO 的说法（给不出答案）。** 试点里的翻译是：刚性问题 → 存在依赖
  （`Role ⊑ ∃hasRole⁻.Whole`，再加"整体与部分类型不同"）。
- **D4 · H8 机判只能查同名重复，查不出近义重复（没问到这个维度）。** 例：`Phase` 的释义与 `emmo:PhaseOfMatter`
  的 elucidation 几乎逐字相同。现在只能靠 S-isa 加 S-exist 间接兜住。

## 出处

- legacy 报告：12（material-core 逐条审计）、17（视角与判据）、26（五派方法）、33（PMDco 物质/非物质判定）、
  44（拿真实字段压判据）、57（材料本体综述，§5.3 互斥缺失）。
- EMMO governance，"EMMO conventions" 与 "Domain Ontologies" 两节：
  <https://github.com/emmo-repo/EMMO/blob/master/doc/EMMO_governance.md>
- emmocheck（EMMOntoPy）：<https://github.com/emmo-repo/EMMOntoPy/blob/master/emmopy/emmocheck.py>
- OOPS! pitfall 目录：<https://oops.linkeddata.es/catalogue.jsp>；
  Poveda-Villalón, Gómez-Pérez & Suárez-Figueroa, *IJSWIS* 10(2):7–34, 2014。
- Guarino & Welty, "An Overview of OntoClean", *Handbook on Ontologies*, 2nd ed., Springer, 2009, pp. 201–221。
