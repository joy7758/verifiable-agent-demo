# FG-TIDA use-case input / FG-TIDA用例贡献

Candidate for the first-meeting programme of work; non-normative. / 首次会议工作计划候选输入，非规范性材料。

## 1. Identification / 识别信息

**Title / 标题:** Recorded cancellation versus timely local effect: an executed seven-case fixture / 取消记录与及时本地效应：已运行的7例小样

**Submitting organization / 提交机构:** Individual contribution / 个人贡献

**Contact name / 联系人:** Bin Zhang（张斌）

**Contact email / 联系邮箱:** joy7759@gmail.com

**Sector / 行业:**

- [ ] Education / 教育
- [ ] Displaced persons / humanitarian / 流离失所及人道主义
- [ ] Health / 健康
- [ ] Financial services / 金融服务
- [ ] Telecom / 电信
- [ ] Media and publishing / 媒体及出版
- [ ] Logistics / 物流
- [ ] Energy / 能源
- [ ] Critical infrastructure / 关键基础设施
- [ ] Smart home / IoT / 智能家居及物联网
- [x] Other: enterprise software, isolated synthetic operations / 其他：企业软件、隔离合成操作

## 2. The situation / 情况

**Plain language description / 通俗描述:** A local agent has one queued, permitted update and a scripted human response can request cancellation. A positive receipt can coexist with an executed update when delivery is late or deliberately dropped. A separate read-only process checks actual terminal state, keeping missing observations unknown.

中文：本地智能体有一个获准排队的更新，脚本代替人发出取消请求。送达迟到或故意丢弃时，收到确认和动作实际执行可以同时出现。分开的只读进程检查实际终态，观察缺失保留为未知。

**Actor / 参与者:** Stipulated principal, agent/controller, scripted reviewer, local provider, separate read-only observer, experimental evaluator. / 预设委托人、智能体控制端、脚本审查者、本地提供端、分开的只读观察端、实验评价器。

**Action / 动作:** Set one disposable SQLite row from 0 to 1 at logical tick 10, or cancel before commitment; no undo operation is modelled. / 在逻辑时刻10将临时数据库的一行从0改为1，或在执行前取消；不建模撤销。

**Decision required / 所需判断:** Does this record establish that the cancellation actually prevented this exact local action before the declared boundary? / 记录能否证明取消在声明边界以前确实阻止了这一具体本地动作？

**Problem encountered / 问题:** Receipt, valid authority, decision and actual effect are logically different; the existing public approval-integrity regression does not exercise this time-to-actuation distinction. / 确认、有效权限、决定和实际效应各不相同；已有公开批准/完整性回归未测试这一决定到动作的时间边界。

**Current mitigation / 现有措施:** Existing workflow pause/cancel/state machinery and evidence integrity checks. / 现有工作流暂停、取消、状态机制及证据完整性检查。

**Residual gap / 剩余差距:** An executed, reviewable local counter-control for receipt/effect conflation and a declared strict deadline, without asserting a general standard or product gap. / 对确认与效应混同及明确严格截止点，提供已运行、可审查的本地反例；不主张普遍标准或产品缺口。

## 3. Actors and context / 参与者及上下文

**Taxonomy roles / 分类角色:**

- [x] Principal / 委托人
- [x] Relying party / 判断依赖方
- [x] Builder / 构建者
- [x] Deployer / Owner / 部署者或拥有者
- [x] Agent instance / 智能体实例
- [x] User / 用户
- [x] Infra provider / 基础设施提供方
- [ ] Attestor / 证明方
- [x] Other: observer and experimental evaluator / 其他：观察方和实验评价器

**Mandates / 授权关系:**

| Grantor / 授权者 | Grantee / 获授权者 | What is conferred / 授予事项 | Governing regime / 适用规则 |
|---|---|---|---|
| Synthetic principal / 合成委托人 | Local agent/provider / 本地智能体及提供端 | One exact local update / 一次指定本地更新 | Stipulated local fixture policy v0.1; no legal validity tested / 预设本地小样规则0.1，不验证法律效力 |
| Synthetic principal / 合成委托人 | Scripted reviewer / 脚本审查者 | Cancel this action before tick 10 / 时刻10前取消此动作 | Same stipulated policy; identity and authority assumed current / 同一预设规则，预设身份及权限有效 |

**Cross-border / 跨境:** [ ] Yes / 是; [x] No / 否

**Embodied / 物理执行或感测:** [ ] Yes / 是; [x] No / 否

**Agent action type / 智能体动作类型:** [ ] Read-only / 只读; [x] Consequential (reversible) / 有影响但可逆; [ ] Irreversible / 不可逆

**Crosses organisational boundary / 跨机构:** [ ] Yes / 是; [x] No / 否

**Risk level / 风险等级:** [x] Low / 低; [ ] Medium / 中; [ ] High / 高

This is a sandbox with disposable local state, not a production deployment or a legal-authority experiment. / 仅为临时本地状态的沙盒，不是生产部署或法律权限实验。

## 4. Theme relevance / 主题关联

| Theme / 主题 | Yes / 是 | Primary / 首要 | Justification / 理由 |
|---|---|---|---|
| Dynamic Identity / 动态身份 | [ ] | [ ] | Not exercised / 不测试 |
| Continuous Trust and Attestation / 持续信任及证明 | [ ] | [ ] | No attestation profile proposed / 不提出证明配置 |
| Delegation / 委托授权 | [ ] | [ ] | Authority is stipulated, not appraised / 权限预设，不进行判断 |
| Discovery and Cross-Border Trust / 发现及跨境信任 | [ ] | [ ] | Not exercised / 不测试 |
| Runtime Enforcement (Control Plane) / 运行时控制执行 | [x] | [x] | Cancellation delivery, boundary and actual local effect / 取消送达、边界和实际本地效应 |
| Embodied AI Identity and Trust / 具身智能身份及信任 | [ ] | [ ] | No physical actuation / 无物理执行 |

**Related theme proposals / 相关提案:** [Theme #16](https://github.com/FG-TIDA/themes/issues/16)（主题16）；optional later interface review with [UC-4](https://github.com/FG-TIDA/use-cases/issues/4)（用例4，之后可另行审查接口）。

## 5. Requirements / 要求

These are test-local acceptance conditions offered for review, not universal requirements. / 以下只是供审查的小样验收条件，不是普遍要求。

| # | Type / 类型 | Requirement / 要求 | Criticality / 必要程度 |
|---|---|---|---|
| 1 | Technical / 技术 | Freeze action version, authority assumption, deadline and tie ordering before running / 运行前固定动作版本、权限假设、截止点及同刻先后顺序 | Must / 必须 |
| 2 | Technical / 技术 | Preserve decision, receipt, provider confirmation and observed terminal effect separately / 分别保留决定、确认、提供端执行说明及观察终态 | Must / 必须 |
| 3 | Technical / 技术 | Evaluator gets observable state only, not case labels or expected answers / 评价器只拿可观察状态，不拿案例标签或预期答案 | Must / 必须 |
| 4 | Technical / 技术 | Late delivery and positive receipt with dropped delivery must not imply effective cancellation / 迟到或仅有确认但丢弃送达，不得推断取消有效 | Must / 必须 |
| 5 | Technical / 技术 | Missing or action-mismatched observation cannot become a positive effect result / 观察缺失或动作不匹配，不得变成效应成功 | Must / 必须 |
| 6 | Technical / 技术 | Demonstrate both timely cancellation and legitimate execution with no cancellation / 同时展示及时取消和未要求取消时正常执行 | Must / 必须 |
| 7 | Technical / 技术 | State logical-clock, authentication, human-capacity and observer trust limits / 说明逻辑时钟、认证、真人能力及观察信任边界 | Must / 必须 |

## 6. Assessment criteria / 验收判据

**Success criteria / 成功条件:** Match the seven frozen expected local outcomes, preserve unknown when readback is missing, and reject receipt/effect conflation. / 与7个预先固定的本地预期一致，缺回查时保持未知，拒绝确认与效应混同。

**Measurable metric / 可测指标:** Expected/observed match count; false positive cancellation under the acknowledgement-only comparator; actual cancellation application tick and remaining logical margin where observed. / 预期与观察一致数量；仅依赖确认的错误对照的取消假成功；可观察时记录实际取消应用时刻及逻辑余量。

**Executed result / 已运行结果:** 7/7 matches; acknowledgement-only comparator 5/7 mismatches; eight counter-control tests and original one-case approval regression pass. Positive cancellation margin is one synthetic tick, not one second. / 7/7一致，仅靠确认对照5/7误判；8项反例测试及原1项批准回归通过。及时取消的余量是1个合成逻辑单位，不是1秒。

## 7. Duplication check / 避免重复核查

**Existing standards or SDOs / 已有标准或组织工作:** Existing FG-TIDA Themes #16, UC-4, UC-6, UC-20 and UC-21/S5; IETF RATS [RFC 9334](https://www.rfc-editor.org/rfc/rfc9334.html) evidence/appraisal separation; [MITRE CWE-367](https://cwe.mitre.org/data/definitions/367) check-to-use timing; LangGraph persistence/interrupts and Azure Durable Functions workflow machinery. / 已有FG-TIDA相关主题和案例；IETF（互联网工程任务组）RATS（远程证明流程）证据/评价区分；MITRE（技术研究机构）检查与使用的时间差分类；现有图式及云工作流。

**Overlap notes / 重叠说明:** Timing/operability and acknowledgement/effect separation are already proposed by others. Diana Baker, Olena Pavlenko, Nelson Trasatti, Lei Gao and Iván Abril Palma are credited in the source README. The previously submitted Bin Zhang non-curative regression remains old work. The sole increment is the executed seven-case local fixture, separate read-only terminal-state observation and retained records; no new matrix dimension, general architecture, proprietary-control requirement or standard gap is asserted. It does not implement full S5 or replace Chi20's preferred source checkpoint; UC-4 integration would require separate contributor review and a version-pinned scope. Further standards-overlap review remains open.

中文：时间/可操作性和确认/效应区分已由其他人提出，来源说明明确署名。张斌此前的批准回归保留为旧成果。唯一新增是已运行的7例本地小样、分开的只读终态观察和留存记录，不增矩阵维度、普遍架构或专有控制要求，不主张标准缺口。不实现完整S5、不取代Chi20优先源案例；接入UC-4仍需原贡献者另行审查并固定版本范围。更广标准重叠审查仍开放。

## 8. Maturity / 成熟度

**Pilot status / 试验状态:** [ ] Hypothetical / 仅构想; [x] Pilot in progress / 试验中; [ ] Deployed in production / 生产部署

The scenario is synthetic; the local operational fixture has been executed. No real humans or production providers participated, and no independent human review has occurred. / 场景是合成的，本地操作小样已实际运行。无真人或生产提供方参与，尚无独立人工复核。

**Reference implementation / 参考实现:** [local fixture](../../examples/theme16_intervention/README.md)（本地小样）；[review and execution limits](fgtida-theme16-intervention-review.md)（核查及执行边界）。

## 9. IP and confidentiality / 知识产权及保密

**Confidentiality level / 保密等级:** [x] Public / 公开; [ ] FG-internal only / 仅组内; [ ] Redact before publication / 发布前脱敏

**IP notes / 知识产权说明:** Only new synthetic local records and source already public are included; private TITMAS core and customer material are excluded. This is AI-assisted preparation submitted by Bin Zhang; attribution grants no rights in others' materials and implies no endorsement. No new blanket repository licence or patent-clearance claim is made. / 只含新增合成本地记录及已公开来源，不含私有TITMAS核心或客户材料。由张斌提交，人工智能辅助制作；署名不授予他人材料权利、不表示认可，不新增全仓库许可或无专利负担声明。

## 10. Assets / 材料

- [x] Dataset / 数据：[seven case fixtures](../../examples/theme16_intervention/cases.json)（7例固定输入及独立预期）
- [x] Code / 代码：[runner](../../examples/theme16_intervention/run.py)（运行器）；[counter-controls](../../tests/test_theme16_intervention.py)（反例测试）
- [x] Protocol / 协议：[scope, attribution and reproduction](../../examples/theme16_intervention/README.md)（范围、署名及复现）
- [x] Other / 其他：[executed report](../../artifacts/theme16_intervention/report.json)（实际运行报告，含每例证据摘要）；[research decision](fgtida-theme16-intervention-review.md)（研究判断）

**IP notes / 知识产权说明:** Source attributions and exact reviewed revisions are preserved in the linked documents. / 关联文档保留来源署名和确切已读版本。

## Requested disposition / 请求审查事项

Please consider this bounded benchmark input for the initial programme of work and review whether its records are useful for a separately admitted Theme #16 operational mapping. No Matrix v0.2/UC-6 change or UC-4 maintenance assignment is requested. Submission is for review; agenda selection, admission and adoption remain with FG-TIDA. / 请审查此窄范围基准能否作为初期工作计划输入，以及记录能否帮助另行接纳的主题16操作映射。不要求修改矩阵0.2/UC-6，不分配UC-4维护任务。此为送审，议程选择、接纳和采纳仍由FG-TIDA决定。
