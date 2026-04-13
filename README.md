# SiYuan Notes Skill - 思源笔记技能

Hermes Agent 的思源笔记操作技能，提供完整的本地 API 操作能力。

## 功能特性

- 📓 **笔记本管理** - 创建、重命名、删除、配置笔记本
- 📄 **文档操作** - 创建、编辑、删除、移动文档
- 🧱 **块操作** - 插入、更新、删除、移动块
- 🔍 **SQL 搜索** - 强大的数据库查询功能
- 🏷️ **属性管理** - 设置和获取块属性
- 📝 **模板渲染** - Sprig 模板和文件模板
- 📁 **文件操作** - 读/写/删除/列出文件
- 🔔 **通知推送** - 向思源笔记推送消息

## 安全特性

### 三层删除保护

1. **全局开关** - 客户端默认禁用删除 (`allow_delete=False`)
2. **二次确认** - 删除时需要输入资源 ID 进行验证
3. **审计日志** - 所有删除操作自动记录

### 配置安全

- 配置文件自动设置权限为 600
- API Token 加密存储
- 支持 Token 轮换

## 快速开始

### 1. 安装技能

```bash
# 克隆技能到 Hermes
git clone https://github.com/NoviaRick/siyuan-skill.git ~/.hermes/skills/note-taking/siyuan-notes
```

### 2. 配置 API

```bash
# 初始化配置（交互式）
python ~/.hermes/skills/note-taking/siyuan-notes/scripts/siyuan_config.py init

# 验证配置
python .../siyuan_config.py verify
```

### 3. 使用 Python 客户端

```python
from siyuan_client import SiYuanClient

# 创建客户端（删除操作默认禁用）
client = SiYuanClient()

# 列出笔记本
notebooks = client.notebooks.list()

# 创建文档
doc_id = client.documents.create(
    notebook_id="xxx",
    path="/测试文档",
    markdown="# 标题\n\n内容"
)

# SQL 搜索
results = client.query.search_content("关键词")
```

## 文件结构

```
siyuan-skill/
├── SKILL.md                      # 技能主文档
├── README.md                     # 使用说明
├── references/
│   └── SECURITY.md               # 安全分析报告
└── scripts/
    ├── siyuan_api.py             # 命令行工具
    ├── siyuan_client.py          # Python 客户端库
    ├── siyuan_config.py          # 配置管理工具
    └── siyuan_delete_protect.py  # 删除保护工具
```

## 环境要求

1. 思源笔记正在运行
2. API 已启用（默认端口 6806）
3. 获取 API Token（设置 → 关于）

## 安全提示

- ⚠️ 确保 6806 端口不暴露到外网
- ⚠️ 定期更换 API Token
- ⚠️ 配置文件权限保持 600
- ⚠️ 不要将配置文件提交到版本控制

## 许可证

MIT License
