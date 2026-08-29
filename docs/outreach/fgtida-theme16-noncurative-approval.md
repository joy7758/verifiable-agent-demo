# Non-Curative Human Approval at an Agent Action Boundary

**智能体动作边界上“人工批准不可修复证据”的规则**

## Status / 状态

This is a bounded discussion note for FG-TIDA Theme #16 and a publicly reproducible implementation supplement centered on one test. It acknowledges the earlier [Theme #16 comment presenting Iman Schrock's contribution on bounded human authority](https://github.com/FG-TIDA/themes/issues/16#issuecomment-5461859516). It is not an ITU standard, formal proposal, or adopted document. This note and test have not been reviewed or endorsed by Iman Schrock, FG-TIDA, or ITU.

这是一份面向 FG-TIDA 主题 #16 的有边界讨论说明，也是一项以单个测试为中心、可公开复现的实现性补充。本文承认此前[主题 #16 评论中介绍的 Iman Schrock 关于有限人工权限的贡献](https://github.com/FG-TIDA/themes/issues/16#issuecomment-5461859516)。本文不是 ITU 标准、正式提案或已采纳文件。本说明及其测试未经过 Iman Schrock、FG-TIDA 或 ITU 的审阅或认可。

## Core rule / 核心规则

Three outcomes remain separate: **evidence status** — `VALID`, `INVALID`, `INCOMPLETE`, or `INDETERMINATE`; **human decision** — `APPROVE`, `REJECT`, or `HOLD`; and **execution decision** — `PERMIT`, `DENY`, or `HOLD`. A human decision must not modify the evidence status.

三个结果应分别保存：**证据状态**——`VALID`（有效）、`INVALID`（无效）、`INCOMPLETE`（不完整）或 `INDETERMINATE`（无法确定）；**人工决定**——`APPROVE`（同意）、`REJECT`（拒绝）或 `HOLD`（暂停）；以及**执行决定**——`PERMIT`（允许）、`DENY`（拒绝）或 `HOLD`（暂停）。人工决定不得修改证据状态。

Where a high-risk action requires valid evidence, `APPROVE` combined with evidence that is invalid, incomplete, indeterminate, or mismatched to the exact action must still produce `DENY` or `HOLD`, never `PERMIT`.

如果某类高风险动作要求有效证据，那么，即使人工决定为 `APPROVE`（同意），只要证据无效、不完整、无法确定或与准确动作不匹配，执行决定仍必须是 `DENY`（拒绝）或 `HOLD`（暂停），不得是 `PERMIT`（允许）。

## Why this matters / 为什么重要

Approval to make a payment does not make a missing contract appear. Approval to merge code does not remove an evidence-binding error. Acceptance of residual risk may affect a decision, but it does not change the result of a factual or evidence check.

批准付款不代表缺失的合同已经出现。批准合并代码不代表证据绑定错误已经消失。接受剩余风险可以影响决定，但不会改变事实检查或证据检查的结果。

## Minimal record / 最小记录

For discussion, a minimal oversight record should preserve separately: `trigger_event`, `action_digest`, `evidence_status`, `human_decision`, `human_decision_artifact_digest`, `execution_decision`, `policy_version`, `reasons`, and `revalidation_condition`. This is a suggested discussion record, not a mandatory international standard.

作为讨论建议，最小人工监督记录应分别保存：`trigger_event`（触发事件）、`action_digest`（动作摘要）、`evidence_status`（证据状态）、`human_decision`（人工决定）、`human_decision_artifact_digest`（人工决定文件摘要）、`execution_decision`（执行决定）、`policy_version`（策略版本）、`reasons`（理由）以及 `revalidation_condition`（重新验证条件）。这只是讨论性建议，不是强制性国际标准。

## Bounded test / 有边界测试

The test `tests/test_fgtida_theme16_noncurative_approval.py` reuses the existing `task-015` scenario and `evidence_chain` runner. The current harness models explicit human approval with a present synthetic test token, and the approval check passes. The expected action digest is then deliberately mutated, producing a mismatch with the actual action digest. The final result remains `tamper_detected` and does not become `completed`.

测试 `tests/test_fgtida_theme16_noncurative_approval.py` 复用现有的 `task-015` 场景和 `evidence_chain` 运行路径。当前测试框架以一个明确存在的合成测试凭证来模拟人工批准，且批准检查通过；随后刻意变异预期动作摘要，使它与实际动作摘要不一致。最终结果仍为 `tamper_detected`（发现篡改），不会变成 `completed`（已完成）。

Run the bounded test with:

使用以下命令运行该有边界测试：

```bash
python3 -m unittest discover -s tests -p 'test_fgtida_theme16_noncurative_approval.py' -v
```

Expected result: `Ran 1 test` and `OK`.

预期结果：`Ran 1 test`（运行 1 项测试）和 `OK`（通过）。

## Attribution / 署名

The prior bounded-human-authority contribution is attributed to Iman Schrock in the linked Theme #16 comment. This note does not claim that Bin Zhang originated the underlying principle. The following attribution covers only the bounded test and this implementation note.

此前关于有限人工权限的贡献，依照上述主题 #16 评论归于 Iman Schrock。本文不宣称张斌首创其底层原则。以下署名仅覆盖该有边界测试和本实现说明。

Technical contribution: Bin Zhang; Independent Researcher; Shanxi Youqibing E-Commerce Co., Ltd.; ORCID: `0009-0002-8861-1481`.

技术贡献者：张斌；独立研究者；山西游骑兵电子商务有限公司；ORCID（开放研究者与贡献者身份标识）：`0009-0002-8861-1481`。

## Claim boundaries / 主张边界

This test does not prove that a human decision is correct, lawful, or proportionate; that underlying input facts are true; or that a complete human-oversight solution exists. It is not a determination of legal responsibility, a compliance certification, or evidence of adoption by FG-TIDA or ITU. It demonstrates only that, in the current public demo, satisfying the approval requirement does not automatically override detected action tampering.

该测试不证明人工决定正确、合法或合乎比例，不证明底层输入事实真实，也不证明已经形成完整的人工监督方案。它不构成法律责任判断、合规认证，也不构成 FG-TIDA 或 ITU 采纳的证据。它只证明：在当前公开演示中，“批准条件已满足”不会自动覆盖“发现动作篡改”的结果。

In this deterministic fixture, approval satisfaction is a nonempty-token check and the tamper case is predefined. The test does not validate a real approver's identity, signature, authority, scope, expiry, or binding to the exact action, and it is not an independent detector of unknown production tampering or real payment or code-merge effects.

在这个确定性的测试夹具中，批准满足条件只是检查凭证非空，篡改情形也是预先定义的。该测试不验证真实批准人的身份、签名、权限、范围、有效期或与准确动作的绑定，也不是用于发现未知生产篡改、真实付款影响或真实代码合并影响的独立检测器。
