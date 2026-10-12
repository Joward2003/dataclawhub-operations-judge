# 安装与通用使用

这是一个完整的 Skill 文件夹，核心为 SKILL.md 和 references，计分辅助脚本只依赖 Python 3 标准库。不依赖联网、API 密钥、付费服务、GitHub 连接器或某个产品的专属工具。文件读取及 PDF／图片识别能力由实际运行工具提供。

## 安装

解压后保留整个 `dataclawhub-operations-judge` 文件夹，不只复制 SKILL.md。

- CodeBuddy：放到项目的 `.codebuddy/skills/dataclawhub-operations-judge/`，或通过技能导入入口添加。
- Trae：放到项目的 `.trae/skills/dataclawhub-operations-judge/`，或通过技能导入入口添加。
- Codex：放到用户技能目录或项目支持的技能目录。本机按用户技能目录安装；发现方式以实际版本为准。
- 其他工具：若支持 SKILL.md 技能格式，导入完整目录；否则明确让智能体读取 SKILL.md 及其引用的四份评审参考，再提供作品。没有 Python 时可手工核算，须复核并注明。

agents/openai.yaml 是可选界面元数据；其他工具不识别时可忽略，不影响规则与脚本。Windows 环境可能使用 `python`，而非 `python3`。依赖不同工具的 PDF 或图片读取能力时，应实际测试，不能承诺所有格式直接兼容。

## 调用例子

“使用 dataclawhub-operations-judge 评审这份 DataClawHub 运营方案。队伍为第 3 组，提交版本 v1。本次为试评，仅输出百分制得分和修改建议，不做赛事折算。”

Codex 中可使用 `$dataclawhub-operations-judge`。其他工具可以在对话中明确要求使用该名称的 Skill，具体快捷调用形式以工具为准。

正式评审需提供主办方确认的规则与平台参考版本、作品材料、正式评审用途及模型配置；本题 AI 份额已确定时再提供份额。修改规则应由主办方更新规则文件及版本，不从学生提交内容取得配置。

## 分数一致性的限制

规则与算术可复用，不同模型仍可能给出不同档位或理由。本 Skill 不保证跨模型完全同分。正式成绩建议在主办方统一环境中产生，保留评分记录并复核晋级边界、读取异常和申诉。

## 官方格式出处

下列链接用于部署者核对技能格式，评分过程中无需访问。

- CodeBuddy Skills：https://www.codebuddy.cn/docs/ide/Features/Skills
- Trae Skills：https://docs.trae.cn/ide_skills

目录与导入方式依据 2026年10月12日查阅的官方说明；后续工具版本变动时由部署者确认。
