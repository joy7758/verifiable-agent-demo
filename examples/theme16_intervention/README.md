# Local cancellation checkpoint / 本地取消检查点

This is a non-normative operational fixture for Theme #16, not a TITMAS core upgrade. The controller, provider and read-only observer execute as local Python processes. The provider really changes a disposable SQLite row; event ordering is driven by a synthetic logical clock. No wall-clock performance or human response capability is measured.

中文：这是供主题16审查的非规范性操作小样，不是 TITMAS 核心升级。控制端、动作提供端和只读观察端通过本地 Python 进程运行；提供端实际修改临时 SQLite 数据库的一行。时序采用合成逻辑时钟，不测现实耗时或真人反应能力。

Run from the repository root / 从仓库根目录执行：

```bash
python examples/theme16_intervention/run.py
python -m unittest discover -s tests -p 'test_theme16_intervention.py' -v
python -m unittest discover -s tests -p 'test_fgtida_theme16_noncurative_approval.py' -v
```

Expected summary / 预期摘要：`matches=7`（7项符合预期）, `total=7`（总计7项）, `ack_only_mismatches=5`（仅依赖确认的错误对照有5项误判）。Python 3.10+ is required; Python 3.12.14 was tested. No packages, credentials, network or live service are needed. 中文：要求 Python 3.10及以上，本轮实测3.12.14；无需安装依赖、密钥、网络或在线服务。

Output / 输出：`artifacts/theme16_intervention/report.json` and seven case directories, each with intent, trace, evidence bundle, replay verdict and unsigned audit receipt. Hashes reuse the existing `paper_eval.common.sha256_digest`; these local demo records do not implement or replace the canonical `agent-evidence` profile. 中文：生成一个汇总报告及7个案例目录，每个保存意图、轨迹、证据包、复核结论及未签名审计回执。哈希复用现有函数；这些本地演示记录不实现或取代规范证据配置。

| Case / 案例 | Fixed intervention / 固定干预 | Expected observation / 预期观察 |
|---|---|---|
| C0 | No cancellation / 未发取消 | Actual action executes / 动作实际执行 |
| C1 | Decision and delivery at tick 9 / 决定和送达均在逻辑时刻9 | Terminal cancellation, value remains 0 / 已取消的终态，数值保持0 |
| C2 | Decision at 9, delivery at 11 / 时刻9决定，11送达 | Action committed at 10 / 动作已在时刻10执行 |
| C3 | Positive receipt, command dropped / 确认收到，但命令丢弃 | Action still executes / 动作仍执行 |
| C4 | Delivery exactly at 10 / 恰在时刻10送达 | Commit wins under the frozen strict rule / 按预先固定的严格边界，执行先发生 |
| C5 | Timely cancellation, observer unavailable / 及时取消，观察缺失 | Unknown; no success inferred / 结果未知，不能推断成功 |
| C6 | Timely cancellation, receipt lost / 及时取消，确认丢失 | Readback establishes cancellation / 只读回查确认取消 |

## Source and evaluation boundary / 来源与评价边界

The human response is scripted, and authority is assumed current and applicable to cancelling this one action. Its legitimacy, authentication, reviewer understanding and evidence sufficiency are not tested. The assessor receives the observable evidence and state; it never receives case IDs, fault-injection labels or expected answers. The harness retains those separately. A read-only observer subprocess reads terminal state without using controller acknowledgements. All components share one trusted host and database; this is separation of readback from acknowledgement, not adversarial independence or authenticated provider reconciliation.

中文：人类响应由脚本代替，预设人具有取消这一动作的当前权限；不验证法律权限、身份真实性、人的理解或信息是否足够。评价器只收到可观察证据和状态，不收到案例编号、故障标签或预期答案；这些由实验端另存。只读观察子进程回查终态，不使用控制端确认。各组件共用可信主机和数据库，因此只是回查与确认的程序分离，不是对抗条件下的独立性或经过认证的提供方对账。

Commitment occurs at logical tick 10 before a cancellation received at or after that tick. The action is reversible in the physical sense, but this fixture has no undo operation: cancelling after commitment cannot prevent that already recorded action. Negative delivery controls are deliberately injected by the harness, not defects discovered in TITMAS or a vendor product. The positive continuity case prevents an always-block interpretation of success.

中文：动作在逻辑时刻10执行，时刻10及以后收到取消均算迟到。修改数值本身可逆，但本小样不包含撤销操作；执行以后取消不能抹去已发生的动作。送达故障由实验端故意注入，不是发现 TITMAS 或厂商产品缺陷。正常执行对照防止“全部阻止”被算成成功。

## Attribution and non-duplication / 署名与避免重复

Timing/recoverability criteria: Diana Baker's [Theme #16 contribution](https://github.com/FG-TIDA/themes/issues/16#issuecomment-6058863257). Observable-input and separate-effect conditions: Olena Pavlenko's [protocol comment](https://github.com/FG-TIDA/themes/issues/16#issuecomment-6001767204). UC-4 operational mapping proposal: Nelson Trasatti; [scope confirmation](https://github.com/FG-TIDA/themes/issues/16#issuecomment-6019817298) by Lei Gao. Delayed-action and current-state stress scenarios already exist in Iván Abril Palma's [UC-21, S5](https://github.com/dakleyer/use-cases/blob/aec08fb5b0fac2ee399372370e9ee2a82a2d5779/contributions/when-controls-work-system-fails/annexes/scenarios/S5.md).

中文：时间与可恢复性判据来自 Diana Baker；只使用可观察输入、分开观察效应的方法要求来自 Olena Pavlenko；UC-4操作映射提议来自 Nelson Trasatti，范围由 Lei Gao确认；延迟动作与当前状态的压力案例已由 Iván Abril Palma 的 UC-21/S5提出。

Bin Zhang's addition here is only this executed, seven-case local fixture and its reviewable records. It is not a new timing theory, an implementation of the full S5 scenario, an accepted UC-4 adapter, or a replacement for the preferred deferred checkpoint from Chi20. UC-6 and Matrix v0.2 remain upstream calibration references; this fixture proposes no changes to them. Original authors retain their source semantics. AI-assisted preparation is disclosed; no independent human review has yet occurred.

中文：Bin Zhang本轮新增仅为已运行的7例本地小样及可审查记录；不是新时间理论、完整S5实现、已被接纳的UC-4适配器，也不取代当前优先讨论的Chi20延迟检查点。UC-6及矩阵0.2继续作为上游校准参考，本小样不要求修改它们。原贡献者保留原案例语义。本材料经人工智能辅助制作，尚未经过独立人工复核。
