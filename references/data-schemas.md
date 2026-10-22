# 数据结构

所有 JSON 均为 UTF-8、无注释。未提供的字段留空（空字符串 / 空数组 / 默认布尔）。

## profile.json — 学生档案

```json
{
  "student_id": "",
  "student_name": "",
  "age": "",
  "native_language": "",
  "target_language": "",

  "learning_goal": {
    "goal_type": "",
    "short_term_goal": "",
    "long_term_goal": "",
    "exam_target": "",
    "industry_focus": ""
  },

  "frequency_per_week": "",

  "current_level": {
    "listening": "",
    "speaking": "",
    "reading": "",
    "writing": "",
    "grammar": "",
    "pronunciation": "",
    "vocabulary": ""
  },

  "learning_style": {
    "personality": "",
    "pace": "",
    "attention_span": "",
    "preferred_methods": []
  },

  "lesson_preferences": {
    "likes_roleplay": true,
    "likes_drills": false,
    "likes_visual_learning": true
  },

  "weak_points": [],
  "strong_points": [],
  "common_errors": [],
  "mastered_topics": [],
  "recommended_next_topics": [],

  "memory_state": [],
  "retention_scores": [],

  "course_phase": "",
  "current_learning_arc": ""
}
```

字段语义：

- `student_id` / `student_name`：唯一标识与显示名
- `native_language` / `target_language`：母语 / 目标语种（English、Cantonese）
- `learning_goal.goal_type`：如考试、工作、日常交流、兴趣
- `current_level.*`：各技能 CEFR 估级（A1–C1）
- `learning_style`：性格、节奏（慢/中/快）、注意力时长、偏好方法
- `lesson_preferences`：是否喜欢角色扮演 / 操练 / 视觉化教学
- `weak_points` / `strong_points`：跨技能弱项与强项（如「第三人称单数」「疑问句构成」）
- `common_errors`：高频错误（如「漏冠词」）
- `mastered_topics`：已掌握主题
- `recommended_next_topics`：建议下一主题
- `memory_state` / `retention_scores`：与 memory_state.json 冗余的轻量索引，可留空
- `course_phase` / `current_learning_arc`：课程阶段与当前学习弧（如「入门→基础会话」）

## memory_state.json — 遗忘追踪（每主题一条）

```json
{
  "topic": "",
  "mastery_score": 0.0,
  "retention_score": 0.0,
  "last_reviewed": "",
  "review_priority": ""
}
```

- `topic`：知识点名（如「Present Perfect」）
- `mastery_score`：掌握度 0–1
- `retention_score`：留存度 0–1（衰减见 [teaching-methods.md](teaching-methods.md)）
- `last_reviewed`：最近复习日期（YYYY-MM-DD）
- `review_priority`：URGENT / HIGH / MEDIUM / LOW

## override.json — 教师逐课干预

```json
{
  "force_include": [],
  "force_exclude": [],
  "locked_sections": [],
  "locked_homework": false
}
```

- `force_include`：下节课必须包含的主题
- `force_exclude`：跳过主题
- `locked_sections`：AI 不得修改的教案区块（如 ["题目练习"]）
- `locked_homework`：true 时禁止 AI 修改作业

## diagnostic.json — 诊断快照

```json
{
  "estimated_level": {
    "listening": "",
    "speaking": "",
    "reading": "",
    "writing": "",
    "grammar": "",
    "pronunciation": "",
    "vocabulary": ""
  },
  "confidence_score": 0.0,
  "weaknesses": [],
  "strengths": [],
  "recurring_errors": [],
  "retention_risks": [],
  "recommended_next_topics": []
}
```

## material.json — 教学素材元数据

```json
{
  "material_id": "",
  "material_type": "",
  "difficulty": "",
  "topic": "",
  "estimated_duration": 0,
  "tags": [],
  "content_path": ""
}
```

- `material_type`：roleplay / pronunciation_drill / listening_activity / grammar_worksheet / shadowing / vocabulary_game / writing_prompt / discussion_topic
- `content_path`：指向同目录 `{id}.md` 的内容文件

## teacher_style.json — 全局教学风格

空白模板：

```json
{
  "humor_level": "",
  "correction_style": "",
  "speaking_ratio": 0,
  "uses_roleplay": true,
  "uses_drills": true,
  "prefers_visual_teaching": true
}
```

推荐默认配置（与「5 模块同步」模型配套）：

```json
{
  "teaching_mode": "5模块同步教学",
  "lesson_duration": { "default_minutes": 150, "min_minutes": 150, "max_minutes": 180, "flexible_buffer_minutes": 10 },
  "modules": [
    { "name": "语法教学", "key": "grammar", "per_lesson_min": 25, "per_lesson_max": 40 },
    { "name": "词汇解析教学", "key": "vocabulary", "per_lesson_min": 20, "per_lesson_max": 35 },
    { "name": "日常交流对话/课文", "key": "speaking", "per_lesson_min": 30, "per_lesson_max": 45 },
    { "name": "听力素材练习", "key": "listening", "per_lesson_min": 15, "per_lesson_max": 25 },
    { "name": "题目练习", "key": "exercises", "per_lesson_min": 20, "per_lesson_max": 35 }
  ],
  "humor_level": "light",
  "correction_style": "delayed",
  "speaking_ratio": 50,
  "uses_roleplay": true,
  "uses_drills": true,
  "prefers_visual_teaching": true,
  "pacing_rules": {
    "density": "medium",
    "new_topics_per_lesson": "2-3 per module",
    "review_ratio": 0.15,
    "practice_ratio": 0.30,
    "new_content_ratio": 0.55
  }
}
```

注意：听力模块素材按语种适配——英语用英剧/播客原声，粤语用港剧原声，遵循「泛听 → 精听 → 跟读」三步。
