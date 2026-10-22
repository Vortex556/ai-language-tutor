# 产物模板

以下模板用于约束输出结构。生成时把 `{...}` 占位符替换为实际内容，YAML frontmatter 字段必须保留。

## 教案 lesson_{seq}.md

```markdown
---
student_id: ""
lesson_id: ""
date: ""
lesson_type: "5模块同步"
duration: 150
difficulty: ""
tags: []
---

# Lesson Plan

## 本课总目标

## 时间总览
| 模块 | 时段 | 时长 | 内容要点 |
|---|---|---|---|
| 回顾与导入 | 0:00-0:15 | 15m | |
| 语法教学 | 0:15-0:50 | 35m | |
| 词汇解析 | 0:50-1:20 | 30m | |
| 日常交流/课文 | 1:20-2:00 | 40m | |
| 听力素材练习 | 2:00-2:20 | 20m | |
| 题目练习 | 2:20-2:50 | 30m | |
| 弹性缓冲 | 2:50-3:00 | 10m | |

## 回顾与导入 (15 mins)

## 语法教学 (30-40 mins)

## 词汇解析 (20-35 mins)

## 日常交流/课文 (30-45 mins)

## 听力素材练习 (15-25 mins)

## 题目练习 (20-35 mins)

## 弹性缓冲 (10 mins)

## 教师备忘
```

## 板书文档 board_{seq}.md

用途：教师导入平板笔记 APP（GoodNotes / Notability / 享做笔记）当黑板，上课展示并直接书写批注。

版面原则：

- **大字优先**——屏幕有限，字号大、行距宽
- **留白充足**——每个知识点后留空行供手写批注
- **一屏一主题**——每个 `##` 标题代表一个「翻页」或滚动节点
- **对话可朗读**——课文对话大字号展示
- **表格少而精**——表格 5–8 行以内，避免缩小字号

必须包含 6 个板块：本课主题+日期、上周重点回顾（3–5 条）、今日词汇墙（3 组、每组 3–6 词带例句）、今日句式公式（1–2 条大字居中）、课文/对话（双人标注 A/B 角色）、题目当场练（3–5 题留答案空白）。

```markdown
---
student_ids: []
lesson_id: ""
date: ""
lesson_type: "board"
theme: ""
---

# 板书 — {主题}

## {日期}

---

## 上堂回顾

---

## 今日词汇

### 类别1：XXX
| 词汇 | 释义 | 例句 |
|---|---|---|

### 类别2：XXX
| 词汇 | 释义 | 例句 |
|---|---|---|

### 口语俚语
| 词汇 | 释义 |
|---|---|

---

## 今日句式

> **{语法公式大字展示}**
> 例：________________________________

> **{语法公式二}**
> 例：________________________________

---

## 课文 / 对话

**{场景标题}**

---

## 随堂练习

1. → 答案：______
2. → 答案：______
3. → 答案：______
4. → 答案：______
5. → 答案：______

---

## 备忘
```

## 作业 hw_{seq}.md

用途：课后发给学生，**精简少量**，三类内容：题目练习（3–5 题）、听力素材（1 段 + 1–2 道理解题）、口语录音任务（1 个，要求录音提交）。

```markdown
---
student_ids: []
lesson_id: ""
date: ""
difficulty: ""
---

# 作业

## 一、题目练习

## 二、听力素材
- 素材：
- 听力题：

## 三、口语录音
- 任务描述：
- 提交方式：录音发送至 ______
- 截止时间：下次课前
```

## 课程总结 lesson_{seq}_summary（可选，用于检索）

```markdown
---
student_id: ""
date: ""
lesson_type: ""
duration: 60
difficulty: ""
tags: []
---

# Lesson Summary

## Lesson Topic
## Lesson Objectives
## Grammar Points
## Vocabulary
## Pronunciation Focus
## Listening Practice
## Speaking Practice
## Student Errors
## Student Strengths
## Homework
## Teacher Notes
## Engagement Level
## Recommended Review Topics
## Recommended Next Topics
```

`tags` 用于检索系统做主题匹配（见 [teaching-methods.md](teaching-methods.md)）。

## 板书分析摘要 board_{seq}_summary.md

```markdown
# Board Summary

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

## 板书排版（Word 转换自动处理）

`scripts/convert_to_word.py` 对 `board_teaching` 类型自动套用平板大字排版：

- H1：26pt 深蓝加粗居中
- H2：20pt
- 正文词汇：14pt
- 例句/对话：13pt、1.5 倍行距
- 表格字号：12pt
- 空白横线用下划线 `_____` 表示手写区
- 对话角色用 **A:** **B:** 加粗
