# 工作流详解

由自然语言意图路由到 9 大工作流之一。解析信息不全时**只补问缺失的关键字段**，其余用默认值，不反问。

## 通用意图解析

- 姓名 → `student_name`（如「张三」）
- 语种 → `target_language`（English / Cantonese，支持中英文说法）
- 时长 → `duration`（「60分钟」「1小时」→ 60；默认 150）
- 类型 → `type`（口语→speaking，语法→grammar，写作→writing，综合→mixed）
- 级别 → `level`（A1/A2/B1/B2/C1；「初级」→A1-A2，「中级」→B1）
- 学生 ID：新建时自动分配 STU001、STU002…；已有学生按名字模糊匹配；匹配不到时列出已有学生让教师选

## 工作流 1：创建学生档案

**触发：** 新建/创建/建档 + 姓名
**最少输入：** 姓名 + 目标语种（缺语种只补问这一项）

**步骤：**

1. 提取 `student_name`、`target_language`
2. 参考 [data-schemas.md](data-schemas.md) 中的 `profile.json` 字段
3. 扫描 `students/` 取最大 ID，分配下一号
4. 创建 `students/{student_id}/` 及子目录（见 SKILL.md 数据目录）
5. 写入 `profile.json`，未提供字段留空
6. 返回确认（含 `student_id` 供后续使用）

**输出格式：**

```markdown
# ✅ 学生档案已创建

**ID:** STU001 | **姓名:** 张三 | **目标:** English | **级别:** A2
档案：`students/STU001/profile.json`

下次直接说「给张三备一节 60 分钟口语课」即可。
```

## 工作流 2：生成教案

**触发：** 备课/教案/上课/lesson + 学生
**最少输入：** 学生 + 时长（如「给两兄妹备课」）
**默认值：** duration=150，density=medium

**课时标准：** 每节 150–180 分钟（2.5–3 小时），**5 大模块每节同步推进**。

**重要：每次备课必须同时产出 3 个文件。**

| 文件 | 保存路径 | 用途 |
|---|---|---|
| `lesson_{seq}.md` | `students/{id}/lessons/` | 教案（教师备课用：时间表、步骤、教师备忘）|
| `board_{seq}.md` | `students/{id}/lessons/` | 板书文档（导入平板笔记 APP 当黑板，大字排版、留批注区）|
| `hw_{seq}.md` | `students/{id}/homework/` | 作业（精简：题目 + 听力素材 + 口语录音任务）|

**步骤：**

1. 加载全局教学风格（`teacher_style.json`，默认值见 [data-schemas.md](data-schemas.md)）
2. 加载 `students/{id}/profile.json`
3. 加载 `students/{id}/override.json`（若存在）
4. 加载 `students/{id}/memory/memory_state.json`（若存在）
5. 检索最近 3–5 节课程摘要（按 YAML tags 匹配主题，见 [teaching-methods.md](teaching-methods.md) 检索系统）
6. 分析：当前水平、弱点、遗忘风险、常错点、教师 override
7. 检索到期待复习的旧知识点（间隔重复）
8. **同时生成三份 Markdown 文件**（教案 + 板书 + 作业）
9. 按时长分配算法配平（见 [teaching-methods.md](teaching-methods.md)）
10. 保存三个文件，返回教案内容 + 板书/作业生成确认

三份文件的具体结构见 [templates.md](templates.md)。

## 工作流 3：生成作业

**触发：** 作业/练习 + 学生
**最少输入：** 只有学生名字（自动选最新一课）

**步骤：**

1. 加载学生档案与最近一节教案
2. 从档案提取弱点、从教案提取本课错误
3. 纳入遗忘引擎中 `retention_score < 0.6` 的待复习主题
4. 按 [templates.md](templates.md) 的作业结构生成
5. 保存到 `students/{id}/homework/hw_{seq}.md`
6. 返回作业内容

## 工作流 4：诊断学生

**触发：** 诊断/分析/评估/什么水平 + 学生
**最少输入：** 学生名字即可

**步骤：**

1. 加载全部可用数据：profile、lessons、homework、board summaries、memory state
2. 跨数据源分析规律
3. 输出诊断报告

**分析维度：** 各技能当前 CEFR 估级与置信度、弱点（严重度 × 频次排序）、强项、跨课反复出现的错误、遗忘风险主题、推荐下一步主题、学习节奏趋势（提升/平台/下滑）。

**输出格式：**

```markdown
# 📊 Student Diagnostic Report

## Student: {name} ({student_id})
## Analysis Date: {date}

## Estimated Level
| Skill | Level | Confidence |
|---|---|---|
| Listening | A2 | 0.75 |
| Speaking | A2 | 0.70 |
| Reading | B1 | 0.80 |
| Writing | A2 | 0.65 |
| Grammar | A2 | 0.72 |
| Pronunciation | A2 | 0.60 |
| Vocabulary | A2 | 0.68 |

## Weak Points
1. **Present Perfect vs Past Simple** — confused in 4/6 recent lessons (HIGH)

## Strengths
1. **Question formation** — consistently accurate

## Recurring Errors
| Error | Frequency | Last Seen |
|---|---|---|
| Missing articles | 12 times | Lesson 5 |

## Retention Risks (Forgetting Curve)
| Topic | Retention | Priority |
|---|---|---|
| Countable/uncountable nouns | 0.35 | URGENT |

## Recommended Next Topics
1. （按弱点 + 遗忘风险的紧急度排序）

## Teacher Action Items
- Consider dedicating next lesson to {topic}
```

## 工作流 5：板书分析

**触发：** 板书/黑板/图片/分析 + 图片路径（学生选填）
**最少输入：** 图片路径；无图时询问路径

**步骤：**

1. 分析教师提供的课堂板书照片
2. **不逐字 OCR**（除非明确要求），只提取教学结构与要点

**分析维度：** 本课主题、板书可见的语法点、词汇、发音重点、例句、学生错误、随堂练习、难度估级。

**输出格式：**

```markdown
# 📋 Board Analysis

## Lesson Topic
## Grammar Detected
## Vocabulary Detected
## Pronunciation Focus
## Example Sentences
## Student Mistakes Detected
## Exercises Detected
## Difficulty Level
## Teaching Notes
```

分析后保存到 `students/{id}/boards/board_{seq}_summary.md`（仅存结构化摘要）。

## 工作流 6：更新记忆状态

**触发：** 记忆/复习/遗忘/更新状态 + 学生；以及每次课后

**步骤：**

1. 回顾最近一节课程摘要
2. 对每个涉及主题更新或新建 memory state 条目：
   - 新主题：`mastery_score = 0.3`，`retention_score = 1.0`，`last_reviewed = 今天`
   - 已复习主题：`mastery_score += 0.05~0.15`（封顶 1.0），`retention_score` 重置为 1.0
   - 学过但未复习：`retention_score -= 0.1~0.2`（衰减）
3. 计算 `review_priority`：
   - `< 0.4` → URGENT
   - `< 0.6` → HIGH
   - `< 0.8` → MEDIUM
   - `>= 0.8` → LOW
4. 保存到 `students/{id}/memory/memory_state.json`

详细规则见 [teaching-methods.md](teaching-methods.md) 的「遗忘与复习引擎」。

## 工作流 7：管理素材

**触发：** 素材/材料/搜索/添加

**子动作：**

- 添加素材：在 `materials/{type}/{id}.json` 写元数据，`{id}.md` 写内容
- 搜索素材：按主题、难度、类型、标签检索
- 推荐素材：匹配当前学生水平与弱点的素材

**素材类型：** roleplay、pronunciation_drill、listening_activity、grammar_worksheet、shadowing、vocabulary_game、writing_prompt、discussion_topic

素材元数据字段见 [data-schemas.md](data-schemas.md)。

## 工作流 8：教学风格设置

**触发：** 风格/教学风格/humor/correction

**字段：**

- `humor_level`: none / light / moderate / heavy
- `correction_style`: immediate / delayed / gentle / direct
- `speaking_ratio`: 0–100（学生开口占比目标）
- `uses_roleplay`: true/false
- `uses_drills`: true/false
- `prefers_visual_teaching`: true/false

生成教案时匹配这些风格偏好。

## 工作流 9：教师干预（Override）

**触发：** 干预/覆盖/强制/必须/下节课一定要

**能力：**

- `force_include`: 下节课必须包含的主题
- `force_exclude`: 跳过主题
- `locked_sections`: AI 不得修改的教案区块
- `locked_homework`: 禁止 AI 修改作业

保存到 `students/{id}/override.json`。
