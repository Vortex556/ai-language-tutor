# 教学法与引擎规则

## 5 模块同步教学（核心模型）

每节课**必须包含全部 5 个教学模块**，缺一不可；每模块推进 1–2 个新知识点并回顾关联旧知识点。模块间自然过渡：词汇为语法服务 → 语法为对话服务 → 对话创造听力语境 → 题目整合检验。

**双人学生（如兄妹/姐妹同堂）**：日常交流模块重点设计双人对话与角色互换练习。

## 时长分配（150 分钟基准）

默认课时 150 分钟（范围 150–180）。弹性缓冲**必须保留，不挤占任何模块**。

| 模块 | 名称 | Min | Max | 典型 |
|---|---|---|---|---|
| 1 | 回顾与导入 | 10 | 15 | 15 |
| 2 | 语法教学 | 25 | 40 | 35 |
| 3 | 词汇解析 | 20 | 35 | 30 |
| 4 | 日常交流/课文 | 30 | 45 | 40 |
| 5 | 听力素材练习 | 15 | 25 | 20 |
| 6 | 题目练习 | 20 | 35 | 30 |
| — | 弹性缓冲 | 5 | 10 | 10 |

总计 145–195 分钟 → 默认配平到 150 分钟。

### 180 分钟扩展规则

当 duration=180 时按比例扩展：语法 +5–10（多加练习）、日常交流 +5–10（多一组场景替换）、听力 +5（多一段素材）、题目 +5（增加翻译量）。

## 内容密度（150 分钟适配）

| Density | 新语法点 | 新词汇 | 课文场景 | 题目量 | 复习占比 |
|---|---|---|---|---|---|
| low | 1 | 6–8 | 复习深化 | 3 题型 | 30% |
| medium | 1–2 | 8–12 | 1 新场景 | 5 题型 | 20% |
| high | 2 | 12–15 | 1 新 + 扩展 | 6 题型 | 10% |

## 配平算法

```
total = duration - 10（缓冲）
review_import = 15（固定）
grammar      = clamp(total * 0.22, 25, 40)
vocabulary   = clamp(total * 0.18, 20, 35)
conversation = clamp(total * 0.27, 30, 45)
listening    = clamp(total * 0.13, 15, 25)
exercises    = clamp(total * 0.20, 20, 35)
确保 5 模块时长均 ≥ min 值
溢出：等比压缩 conversation 与 exercises
余量：按比例分配到各模块
```

## 遗忘与复习引擎

### Memory State 模型

每个主题一条记录（字段语义见 [data-schemas.md](data-schemas.md)）：

```json
{
  "topic": "Present Perfect",
  "mastery_score": 0.65,
  "retention_score": 0.70,
  "last_reviewed": "2026-01-15",
  "review_priority": "HIGH"
}
```

### 衰减规则

- 每节未复习：`retention_score -= 0.10`
- 已复习：`retention_score = 1.0`，`mastery_score += 0.05`（封顶 1.0）
- 出错：`mastery_score -= 0.05`，标记待复习
- `retention_score < 0.3` → 需重新教授（不只是复习）
- `retention_score < 0.5` → 注入下节复习区

### 间隔重复日程

- 第 1 课后 → 快速检查
- 第 3 课后 → 主动回忆
- 第 7 课后 → 深度回顾
- 第 15 课后 → 新语境应用
- 第 30 课后 → 确认掌握

## 检索系统（CRITICAL）

**不要把全部课程历史注入提示词**，按相关性检索。

备课给定主题时（如 present perfect）：

- **错误检索：** 从历史课程中找与该主题相关的错误（过去分词、不规则动词等）
- **主题检索：** 找过去讲过的 present perfect / simple past / tenses
- **记忆检索：** 找 `retention_score < 0.6` 且与主题相关的 memory 条目

**不检索：**

- 无关主题（备 present perfect 时不检索 food vocabulary）
- 已完全掌握的主题（`mastery_score > 0.9` 且 `retention_score > 0.8`）
- 超过 3 个月的课程（除非明确相关）

**实现（文件级检索）：** 扫描课程 YAML frontmatter 的 `tags` 做主题匹配 → 按难度兼容过滤 → 按「新近 + 相关」排序 → 取 3–5 条最相关。

## 语种教学法

### 英语

流程：Warm-up → Review → Vocabulary → Grammar → Listening → Speaking → Correction → Homework

重点：12 时态（渐进引入）、冠词（a/an/the/零冠词）、介词（in/on/at + 时间/地点）、短语动词、条件句、间接引语。

### 粤语

流程：Warm-up → 声调操练 → 词汇 → 对话 → 影子跟读 → 角色扮演 → 纠错 → 作业

重点：6 声调（声调操练、最小对立对）、句末语气词（啦/囉/啩/咋等）、量词、口语 vs 正式语体、粤拼、主题-述题结构。

## 错误追踪约定

在课程摘要中记录学生错误，格式：

```markdown
## Student Errors

| # | Error | Correction | Type | Topic | Persistence |
|---|---|---|---|---|---|
| 1 | "I go to school yesterday" | "I went to school yesterday" | Grammar | Past tense | 3rd occurrence |
```

**持续度：** 首次出现记「New」，重复出现记「Nth occurrence」，连续 3+ 节课未再出现标记为 RESOLVED。

## 成本优化

1. 压缩：存结构化摘要，不存原始转录
2. 检索：只取相关上下文（3–5 条），不取全量历史
3. Markdown 为唯一事实源：不做冗余的 JSON+MD 双存
4. 批量更新：课后一次性批量更新 memory_state，不逐条更新
5. 按水平过滤：不给 B2 学生检索 A1 素材
6. 持久化：文件系统即数据库，只加载所需内容
