# DataClawHub 平台运营方案 AI 评分 Skill

这是「掘金评分官」的通用 Skill，用于评审 DataClawHub 校园黑客松赛题一的**运营方案初赛文字材料**。它按创新优先的独立 AI 规则，以初赛探索方案的成熟度评价核心思路、主要路径和基本验证闭环，给出百分制评分、材料依据、分数图表和可执行的修改建议。当前版本为 `dch-ops-ai-v0.4`。

## 评分范围

| 维度 | 分值 |
| --- | ---: |
| 平台理解与目标方向 | 20 |
| 创新性与机制价值 | 40 |
| 核心路径与试验可行性 | 15 |
| 数据验证设计 | 20 |
| 阶段计划与资源认知 | 5 |

评分包含 14 个子项，每项按 0—4 档判断，再按权重计算。初赛只评方案设计，不评实际执行结果。核心设计成立、主要路径清楚可评 3 档；关键选择有针对性且解释合理可评 4 档，允许细节待完善。判 2 档及以下须说明核心缺口的实际影响，同一缺口原则上只在最直接的子项体现。AI 百分制分数**不会自动折算为赛事 AI 20 分**：运营题占其中的份额须由主办方确认。

本 Skill 仅处理运营题 AI 评分，不处理赛题二、评委评分、跨学院加分或最佳人气奖。

## 安装与使用

仓库根目录和 `dataclawhub-operations-judge/` 子目录提供相同的 v0.4 Skill。安装时保留完整 Skill 文件夹，运行环境应能读取 `SKILL.md`、`references/` 和 `scripts/`；不要只复制入口文件。

- Codex：将仓库中的 `dataclawhub-operations-judge/` 文件夹复制到用户技能目录，然后说：“使用 `$dataclawhub-operations-judge` 评审这份运营方案。”
- CodeBuddy：复制到项目的 `.codebuddy/skills/dataclawhub-operations-judge/`，或使用技能导入功能。
- Trae：复制到项目的 `.trae/skills/dataclawhub-operations-judge/`，或使用技能导入功能。
- 其他 Coding Agent：若支持 `SKILL.md`，导入完整目录；否则让它先读取 `SKILL.md` 及引用的评审文件。

提交作品时，最好同时提供队伍名称、材料版本和可定位的文件或页码。正式统一评审还应由主办方固定规则版本、平台参考版本和模型配置。不同模型可能给出不同档位，建议对边界分数和读取异常进行人工复核。

跨工具安装说明见 [`references/integration.md`](references/integration.md)；具体规则以 [`references/rubric.json`](references/rubric.json) 和 [`references/evaluation.md`](references/evaluation.md) 为准。

## 计分脚本

脚本仅使用 Python 3 标准库。它负责检查 14 项输入并计算分数，不能判断作品证据是否真实。

```bash
python3 scripts/calculate_score.py --template > scoring-input.json
```

填好 `scoring-input.json` 中的材料、14 项档位、理由和证据定位后运行：

```bash
python3 scripts/calculate_score.py scoring-input.json --output scoring-result.json
```

两张分数图表从同一评分记录生成：

```bash
python3 scripts/render_score_charts.py scoring-result.json --output-dir charts
```

若主办方已明确运营题在赛事 AI 20 分中的份额，可额外传入 `--event-points` 生成折算预览。完整字段说明见 [`references/report.md`](references/report.md)。

## 文件结构

```text
SKILL.md                  Skill 入口和评审流程
agents/openai.yaml        可选的界面元数据
references/rubric.json    版本、维度、子项和档位
references/evaluation.md  评分判断、创新容错和案例
references/platform.md    固定平台参考摘要
references/report.md      评分报告和审计记录格式
references/integration.md 跨工具安装说明
scripts/calculate_score.py 计分与输入校验
scripts/render_score_charts.py 五维柱状图与得分构成饼图
```

`references/platform.md` 是公开资料摘要。正式使用前，主办方可提供统一平台说明并更新参考版本。评分时只依据参赛作品及主办方统一材料，不联网补充队伍背景。
