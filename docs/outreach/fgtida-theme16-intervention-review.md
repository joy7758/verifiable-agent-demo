# Submission decision, 9 October 2026 / 2026年10月9日投稿判断

## 1. Prior evidence / 旧进度

The prior [Theme #16 contribution](https://github.com/FG-TIDA/themes/issues/16#issuecomment-5464151540) at repository commit `9988e7a2ee3544b233abf07394c0fcd57a63be92` proposes conceptual separation and a non-curative approval rule. Its existing regression was rerun successfully on Python 3.12.14. The runner treats presence of an approval token as satisfying its synthetic approval check; this is not authenticated human review. No prior record is relabelled as a new result.

中文：此前主题16贡献提出概念性区分和“批准不能修复相反证据”的规则。本轮用Python 3.12.14重跑原回归测试，1项通过。运行器将合成批准令牌的存在视为批准条件满足，不等于认证真人审查。不将旧记录改名为新成果。

The public TITMAS Digital Cell demo at commit `255b3636a740a65d78cbdf7fd0dc46178c3551a9` has seven tests rerun successfully. Its identity, lifecycle, boundary, hash, evidence and health checks do not demonstrate timed human control of a queued action. The public integration README says live service unavailable. The verified-experience specification at `1a73ef42180bae283f929efa7c666d1a6b6aad6f` and APEX test matrix at `d7ee82d774661bdf1987760518d73235deab064f` were read, not rerun: they cover bounded task verification, experience admission, result expiry/signature/context and lifecycle safeguards; these are different from decision-to-actuation timing and human understanding. The public FDO verification STATUS at `1dcca69d0bcc2ee94b7e3ef0c80f21536cd39d1c` retains historical local-candidate publication wording even though the repository is accessible; availability is not certification or a fresh execution result.

中文：公开数字细胞演示本轮7项测试通过，检查身份、生命周期、边界、哈希、证据和健康状态，没有展示对排队动作的限时人类控制。公开集成说明表明在线服务不可用。经验证经验实验规格和APEX测试矩阵本轮只阅读、未重跑；任务验收、经验准入、结果有效期/签名/上下文和生命周期保护，与决定到实际执行的时间、人的理解不同。公开FDO验证仓库的状态文件仍保留历史本地候选措辞；代码可访问不等于认证或本轮执行结果。

| Question / 问题 | Prior reviewed evidence / 旧证据 | This addition / 本轮新增 |
|---|---|---|
| Contrary evidence survives approval / 批准不能覆盖相反证据 | Existing regression, rerun 1/1 / 原回归复验1/1 | Retained, not resubmitted as new / 保留，不重复报新 |
| Human has legitimate current authority / 人有合法当前权限 | Approval token or externally stipulated authority / 合成令牌或外部预设权限 | Assumed for one cancellation, not established / 对单一取消预设，不证明 |
| Human understands and judges in time / 人能及时理解判断 | No evidence in reviewed tests / 已查测试没有此证据 | Not tested; scripted response / 不测试，以脚本代替响应 |
| Stop command changes action before commitment / 停止命令在执行前改变动作 | No demonstrated coverage in reviewed public tests / 已查公开测试未展示覆盖 | Local SQLite effect and logical timing / 本地数据库实际效应及逻辑时序 |
| Acknowledgement versus effect / 确认与效应 | UC-4 declarative mapping already discusses separation / UC-4声明性映射已讨论区分 | Separate read-only process observes actual local state / 分开的只读进程观察实际本地状态 |
| Meaningful real-world human oversight / 现实中有效人类监督 | Unestablished / 未证明 | Remains unestablished / 仍未证明 |

## 2. Research / 最新研究

Searched on 9 October 2026. Read the abstracts of [Comparing Human Oversight Strategies for Computer-Use Agents](https://arxiv.org/abs/2604.04918) and [Keeping an Eye on AI](https://arxiv.org/abs/2605.16278), not their full papers. They concern oversight along action trajectories and oversight architectures/processes. This supports treating timing/oversight as an existing research problem, not claiming conceptual novelty. No numerical human-performance claim from these papers is used. Status: partially completed at abstract level; sufficient for this narrowly bounded non-novelty check, not a systematic review.

中文：2026年10月9日检索，只阅读《比较计算机操作智能体的人类监督策略》和《关注人工智能：有效人类监督框架》的摘要，未阅读全文。它们分别涉及动作过程中的监督和监督架构/流程。因此不主张时间与监督问题本身是新概念，也不采用论文中的真人性能数字。本步部分完成，足够用于本次窄范围避免概念重复的核查，不是系统综述。

## 3. Open implementation and FG-TIDA overlap / 开源实现及现有讨论

Read [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts): graph execution can pause and await external input with persisted state. This is reusable workflow machinery, not evidence that a downstream action is actually stopped in a finite window. No dependency is installed. The existing local demo hash helper is reused, and no canonical verifier or authority engine is moved into this fixture.

中文：读取LangGraph（图式智能体工作流）暂停机制官方文档，已有持久化暂停及外部输入等待能力；这不证明下游动作在有限时间内真的停止。本轮不安装新依赖，仅复用现有本地演示的哈希工具，不搬移规范验证器或权限引擎。

Theme #16 has already discussed finite oversight windows, receipt/effect separation, observable-only evaluator inputs, and an operational experiment. UC-6 preserves authority applicability; UC-20 asks whether required review actually occurred; UC-21/S5 already specifies delayed repair, scoped response, check-to-use binding, and legitimate continuity. Baker's new October contribution offers timing/recoverability criteria. This fixture credits these sources and adds only executable local evidence. It is not full implementation of any of their cases, and it is not the agreed Chi20/UC-4 checkpoint or an admitted adapter. No unreviewed semantic mapping is claimed.

中文：主题16已经讨论有限监督窗口、确认和效应分离、评价器仅用可观察输入以及操作性实验。UC-6区分权限适用性，UC-20追问要求的审查是否发生，UC-21/S5已有延迟修复、限时响应、检查到执行绑定及正常连续性。Baker的10月贡献新增时间/恢复性判据。本小样署名这些来源，只新增可运行的本地证据，不是其完整实现，也不是已议定的Chi20/UC-4检查点或已接纳适配器，不声称未经审查的语义映射成立。本步已检索。

## 4. Commercial services / 商业服务

Read Microsoft's [Durable Functions overview](https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-overview): existing workflow machinery manages state, checkpoints, retries and recovery. UC-21/S5 additionally documents AWS Step Functions/RDS as an existing deferred-action implementation route. Existing native controls must receive credit if they satisfy an agreed case. No provider purchase, deployment, vendor benchmark or live-service test was performed; prices are irrelevant to this zero-service local fixture. Status: official documentation checked; product capability for this specific test remains unverified.

中文：读取微软Durable Functions（持久化工作流函数）官方概览，已有状态、检查点、重试和恢复机制。UC-21/S5还列出了AWS（亚马逊云）工作流/数据库的延迟动作路线。成熟原生控制若满足议定案例应得到认可。本轮未采购、部署、比较厂商性能或测在线服务；本地零服务小样不需要价格选型。本步已查官方资料，厂商对本案例的实际能力仍未验证。

## 5. Decision and formal route / 综合判断与正式流程

Submit one small benchmark/use-case input using the current [FG-TIDA use-case template](https://github.com/FG-TIDA/use-cases/blob/main/.github/ISSUE_TEMPLATE/fg-tida-use-case-proposal.md). Its new content is the seven executed local states and explicit uncertainty, not the existing principles. Ask whether reviewers find the records useful for a later reviewed operational mapping; do not volunteer a new workstream or alter Matrix v0.2 or UC-6. Stop if the exact executed fixture is found already represented, if contributors reject the scope, or if future runs cannot preserve expected versus observed evidence.

中文：用当前官方用例模板提交一份小型基准/用例输入。新增是7个已运行本地状态及明确的未知结果，不是现有原则。只请审查者判断它能否辅助之后另行审查的操作映射，不认领新工作线，不修改矩阵0.2或UC-6。如果发现完全相同的已运行小样已经存在、贡献者否定范围，或以后运行无法保留预期与观察结果，则停止。

The full public [TSB Circular 179](https://www.itu.int/md/T25-TSB-CIR-0179/en), dated 8 October 2026 in the document itself, was read. Paragraph 4 invites use cases, requirements, security criteria and benchmarks; paragraph 7 requires GitHub submission with the applicable template by 23 November; paragraphs 8–9 allow remote participation and require online registration for either attendance mode. The email confirms 20 November registration. The official homepage states registration is mandatory on-site or online. No text reviewed requires Paris attendance to submit a contribution, and submission does not guarantee agenda selection or acceptance. Working language is English; this package provides adjacent Chinese translation.

中文：已读取179号公开正式通知全文，正文日期是2026年10月8日。第4段征集用例、要求、安全判据及基准；第7段要求11月23日前通过GitHub按适用模板提交；第8—9段支持远程参会，现场及远程均须在线注册。邮件确认11月20日报名截止，官网亦明确两种参会方式都须注册。所读文件没有要求贡献者必须到巴黎；提交不保证入议程或采纳。工作语言是英语，本包提供相邻中文翻译。

### Validation boundary / 验证边界

New operational campaign: 7/7 expected/observed matches; the intentionally defective acknowledgement-only comparator mismatches 5/7. Five counter-control tests pass, and the original non-curative approval regression still passes. The public Digital Cell seven tests also pass. A broader demo test discovery was attempted and failed importing existing receipt tests because `aro_audit` is not installed; no claim of full-suite success is made. No private component or paid service was used to repair this environment. These results establish local synthetic discrimination only, not product superiority or general matrix sufficiency.

中文：新操作小样7/7预期与观察一致，故意错误的“仅靠确认”对照5/7误判；5项反例检查通过，原“批准不能修复相反证据”回归仍通过，公开数字细胞7项也通过。尝试扩大到演示仓库全套测试时，已有回执测试因未安装aro_audit（审计库）无法导入；不声称全套通过，不用私有组件或付费服务填补环境。结果仅表明本地合成区分能力，不证明产品优越或矩阵普遍充分。
