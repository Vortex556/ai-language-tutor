---
name: ai-language-tutor
description: 一对一语言家教备课技能：建立学生档案、生成「5 模块同步」教案/板书/作业、诊断学生水平、追踪遗忘曲线、管理教学素材与教师干预。当用户要建学生档案、备课、出作业、诊断学生、分析板书、更新学习记忆或准备语言课程（英语/粤语等）时使用。
---

# AI Language Tutor（语言家教备课）

面向一对一语言家教（教师）的备课工作流。核心价值：**长期学生记忆 + 自适应教学智能**。你的角色不是替学生答疑，而是帮教师把「备课—上课—诊断—记忆管理」全流程沉淀为结构化产出。

## 何时使用

- 建学生档案 / 备课教案 / 出作业 / 诊断水平 / 分析板书 / 更新复习记忆 / 管理素材 / 调整教学风格 / 教师干预
- 目标语种：英语、粤语，可扩展
- 不使用场景：泛泛的语言学习问答、单纯翻译（除非是备课流程的一部分）

## 核心规则（必须遵守）

1. 所有产出用 **Markdown + YAML frontmatter**，不输出纯 JSON、纯文本
2. **不存原始 OCR/转录**，只存结构化摘要
3. **不注入完整课程历史**——用检索式注入，只取最近 3–5 节相关摘要
4. 每份教案必须保留 **5–10 分钟弹性缓冲**
5. **教师始终拥有最终控制权**（override 层）
6. 文件系统即数据库：学生数据持久化在 `students/`，按需读写

## 数据目录（相对工作目录）

```
students/{student_id}/
  profile.json                     # 学生档案
  override.json                    # 教师逐课干预
  lessons/lesson_{seq}.md          # 教案（每节一份）
  lessons/board_{seq}.md           # 板书文档（导入平板当黑板）
  homework/hw_{seq}.md             # 作业
  boards/board_{seq}_summary.md    # 板书照片分析
  diagnostics/diag_{date}.json     # 诊断快照
  memory/memory_state.json         # 遗忘追踪
materials/{type}/{id}.json + {id}.md   # 教学素材
```

首次为某学生建档时，按上述结构创建目录；模板与字段说明见参考文档。

## 意图 → 工作流路由

| 用户说了什么 | 工作流 |
|---|---|
| 新建/创建/建档 + 名字 | 1 创建学生档案 |
| 备课/教案/上课/lesson + 学生 | 2 生成教案（教案 + 板书 + 作业三件套）|
| 作业/练习 + 学生 | 3 生成作业 |
| 诊断/分析/评估/什么水平 | 4 诊断学生 |
| 板书/黑板/图片分析 | 5 板书分析 |
| 记忆/复习/遗忘/更新状态 | 6 更新记忆状态 |
| 素材/材料/搜索/添加 | 7 管理素材 |
| 风格/幽默/纠错方式 | 8 教学风格 |
| 干预/覆盖/强制/必须 | 9 教师干预 |

信息不全时**只补问缺失的关键字段**（如建档缺目标语种），其余用默认值，不反问。

## 参考文档（按需读取）

- [references/workflows.md](references/workflows.md) — 9 大工作流的分步操作与输出格式
- [references/teaching-methods.md](references/teaching-methods.md) — 5 模块同步、时长分配、密度、遗忘曲线、检索与语种教学法
- [references/data-schemas.md](references/data-schemas.md) — profile / memory / override / diagnostic / material 数据结构
- [references/templates.md](references/templates.md) — 教案 / 板书 / 作业 / 课程总结的 Markdown 模板

## Word 导出

所有产出先落 Markdown。需要打印或发给学生时，运行本技能自带脚本批量转 Word：

```bash
python scripts/convert_to_word.py <目标文件夹>
```

脚本自动识别文档类型（教案/板书/作业/总结）并套用对应排版（板书为平板大字号模式）。依赖 `python-docx`、`pyyaml`。

## 交付前自检

- [ ] 全部为 Markdown，YAML frontmatter 齐全
- [ ] 教案含弹性缓冲，模块时长之和等于总时长
- [ ] 内容匹配学生 CEFR 水平，覆盖档案中的弱点
- [ ] 遗忘风险点已进入复习区
- [ ] 作业含复习区，无超纲题量
- [ ] 教师 override 已生效
