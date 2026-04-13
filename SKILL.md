---
name: siyuan-notes
description: 思源笔记本地 API 操作 - 笔记本、文档、块、SQL 查询、模板等完整管理
---

# SiYuan Notes - 思源笔记操作技能

## 概述

本技能提供思源笔记（SiYuan Note）本地 API 的完整操作能力，包括笔记本管理、文档操作、块操作、SQL 查询、模板渲染等。

## 触发条件

当用户需要：
- 创建/编辑/删除思源笔记
- 搜索笔记内容
- 批量管理笔记
- 查询笔记数据库
- 操作笔记块或属性
- 使用模板创建笔记

## 环境要求

1. 思源笔记必须正在运行
2. API 已启用（默认端口 6806）
3. 获取 API Token（设置 → 关于 → API Token）

## 配置

### 方式一：配置文件（推荐）

使用配置管理工具安全地存储配置：

```bash
# 1. 初始化配置（交互式）
python ~/.hermes/skills/note-taking/siyuan-notes/scripts/siyuan_config.py init

# 2. 验证配置
python .../siyuan_config.py verify

# 3. 查看配置
python .../siyuan_config.py show

# 4. 安全检查
python .../siyuan_config.py check
```

配置文件位置：`~/.hermes/siyuan_config.json`
- 自动设置权限为 600（仅所有者可读写）
- Token 部分脱敏显示

### 方式二：环境变量

```bash
# ~/.hermes/.env 或 ~/.bashrc
export SIYUAN_API_TOKEN="your-token-here"
export SIYUAN_API_URL="http://127.0.0.1:6806"

# 设置文件权限
chmod 600 ~/.hermes/.env
```

### 配置管理命令

| 命令 | 说明 |
|------|------|
| `init` | 初始化配置（交互式） |
| `show` | 显示当前配置 |
| `verify` | 验证连接和 Token |
| `rotate` | 轮换 API Token |
| `check` | 安全检查 |

## 核心 API 端点

- **基础 URL**: `http://127.0.0.1:6806`
- **鉴权头**: `Authorization: Token <your-token>`
- **方法**: 全部使用 POST
- **Content-Type**: `application/json`

## 操作步骤

### 1. 笔记本操作

#### 列出所有笔记本
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/notebook/lsNotebooks" \
  -H "Content-Type: application/json"
```

#### 创建笔记本
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/notebook/createNotebook" \
  -H "Content-Type: application/json" \
  --data '{"name": "新笔记本"}'
```

#### 重命名笔记本
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/notebook/renameNotebook" \
  -H "Content-Type: application/json" \
  --data '{"notebook": "笔记本 ID", "name": "新名称"}'
```

#### 删除笔记本
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/notebook/removeNotebook" \
  -H "Content-Type: application/json" \
  --data '{"notebook": "笔记本 ID"}'
```

#### 获取笔记本配置
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/notebook/getNotebookConf" \
  -H "Content-Type: application/json" \
  --data '{"notebook": "笔记本 ID"}'
```

### 2. 文档操作

#### 通过 Markdown 创建文档
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/filetree/createDocWithMd" \
  -H "Content-Type: application/json" \
  --data '{"notebook": "笔记本 ID", "path": "/文件夹/文档名", "markdown": "# 标题\n\n内容"}'
```

#### 重命名文档（通过 ID）
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/filetree/renameDocByID" \
  -H "Content-Type: application/json" \
  --data '{"id": "文档 ID", "title": "新标题"}'
```

#### 删除文档（通过 ID）
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/filetree/removeDocByID" \
  -H "Content-Type: application/json" \
  --data '{"id": "文档 ID"}'
```

#### 移动文档（通过 ID）
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/filetree/moveDocsByID" \
  -H "Content-Type: application/json" \
  --data '{"fromIDs": ["文档 ID"], "toID": "目标父文档 ID 或笔记本 ID"}'
```

#### 导出 Markdown 内容
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/export/exportMdContent" \
  -H "Content-Type: application/json" \
  --data '{"id": "文档 ID"}'
```

#### 根据 ID 获取人类可读路径
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/filetree/getHPathByID" \
  -H "Content-Type: application/json" \
  --data '{"id": "块 ID"}'
```

### 3. 块操作

#### 插入块
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/block/insertBlock" \
  -H "Content-Type: application/json" \
  --data '{"dataType": "markdown", "data": "块内容", "previousID": "前一个块 ID"}'
```

#### 插入前置子块
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/block/prependBlock" \
  -H "Content-Type: application/json" \
  --data '{"dataType": "markdown", "data": "块内容", "parentID": "父块 ID"}'
```

#### 插入后置子块
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/block/appendBlock" \
  -H "Content-Type: application/json" \
  --data '{"dataType": "markdown", "data": "块内容", "parentID": "父块 ID"}'
```

#### 更新块
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/block/updateBlock" \
  -H "Content-Type: application/json" \
  --data '{"id": "块 ID", "dataType": "markdown", "data": "新内容"}'
```

#### 删除块
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/block/deleteBlock" \
  -H "Content-Type: application/json" \
  --data '{"id": "块 ID"}'
```

#### 移动块
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/block/moveBlock" \
  -H "Content-Type: application/json" \
  --data '{"id": "块 ID", "previousID": "前一个块 ID", "parentID": "父块 ID"}'
```

#### 获取子块
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/block/getChildBlocks" \
  -H "Content-Type: application/json" \
  --data '{"id": "父块 ID"}'
```

#### 获取块 kramdown 源码
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/block/getBlockKramdown" \
  -H "Content-Type: application/json" \
  --data '{"id": "块 ID"}'
```

#### 折叠/展开块
```bash
# 折叠
curl -u "" -X POST "http://127.0.0.1:6806/api/block/foldBlock" \
  -H "Content-Type: application/json" \
  --data '{"id": "块 ID"}'

# 展开
curl -u "" -X POST "http://127.0.0.1:6806/api/block/unfoldBlock" \
  -H "Content-Type: application/json" \
  --data '{"id": "块 ID"}'
```

### 4. SQL 查询（最强大功能）

#### 搜索内容
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/query/sql" \
  -H "Content-Type: application/json" \
  --data '{"stmt": "SELECT * FROM blocks WHERE content LIKE '\''%关键词%'\'' LIMIT 10"}'
```

#### 常用 SQL 查询示例

```sql
-- 搜索包含关键词的块
SELECT * FROM blocks WHERE content LIKE '%关键词%' LIMIT 20

-- 按类型查询（h1/h2/p/listitem 等）
SELECT * FROM blocks WHERE type = 'h' AND subType = 'h1'

-- 查询特定笔记本的文档
SELECT * FROM blocks WHERE box = '笔记本 ID'

-- 查询最近更新的块
SELECT * FROM blocks ORDER BY updated DESC LIMIT 10

-- 统计笔记数量
SELECT COUNT(*) FROM blocks WHERE type = 'd'  -- d = document

-- 搜索标题
SELECT * FROM blocks WHERE content LIKE '%# 关键词%'

-- 查找所有任务列表项
SELECT * FROM blocks WHERE type = 'i' AND subtype = 't'
```

### 5. 属性操作

#### 设置块属性
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/attr/setBlockAttrs" \
  -H "Content-Type: application/json" \
  --data '{"id": "块 ID", "attrs": {"custom-标签": "值", "custom-状态": "进行中"}}'
```

#### 获取块属性
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/attr/getBlockAttrs" \
  -H "Content-Type: application/json" \
  --data '{"id": "块 ID"}'
```

### 6. 模板操作

#### 渲染 Sprig 模板
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/template/renderSprig" \
  -H "Content-Type: application/json" \
  --data '{"template": "/daily note/{{now | date \"2006/01/02\"}}"}'
```

#### 渲染模板文件
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/template/render" \
  -H "Content-Type: application/json" \
  --data '{"id": "文档 ID", "path": "模板文件绝对路径"}'
```

### 7. 文件操作

#### 读取文件
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/file/getFile" \
  -H "Content-Type: application/json" \
  --data '{"path": "/data/笔记本 ID/文档 ID.sy"}'
```

#### 写入文件
```bash
# 使用 multipart/form-data 上传
curl -u "" -X POST "http://127.0.0.1:6806/api/file/putFile" \
  -F "path=/data/test.txt" \
  -F "file=@/path/to/local/file.txt"
```

#### 删除文件
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/file/removeFile" \
  -H "Content-Type: application/json" \
  --data '{"path": "/data/文件路径"}'
```

#### 列出目录
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/file/readDir" \
  -H "Content-Type: application/json" \
  --data '{"path": "/data/笔记本 ID"}'
```

#### 重命名文件
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/file/renameFile" \
  -H "Content-Type: application/json" \
  --data '{"path": "/data/旧路径", "newPath": "/data/新路径"}'
```

### 8. 资源文件上传

```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/asset/upload" \
  -F "assetsDirPath=/assets/" \
  -F "file[]=@/path/to/image.png"
```

### 9. 系统操作

#### 获取版本
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/system/version"
```

#### 获取当前时间
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/system/currentTime"
```

#### 获取启动进度
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/system/bootProgress"
```

### 10. 通知

#### 推送消息
```bash
curl -u "" -X POST "http://127.0.0.1:6806/api/notification/pushMsg" \
  -H "Content-Type: application/json" \
  --data '{"msg": "操作完成", "timeout": 7000}'
```

## 块类型参考

| 类型 | 说明 | subType |
|------|------|---------|
| d | 文档 | - |
| h | 标题 | h1, h2, h3, h4, h5, h6 |
| p | 段落 | - |
| l | 列表 | u (无序), o (有序), t (任务) |
| i | 列表项 | - |
| q | 引用块 | - |
| c | 代码块 | - |
| t | 表格 | - |
| s | 分隔线 | - |
| w | 视频 | - |
| a | 音频 | - |
| f | 资源文件 | - |
| m | 数学公式 | - |
| e | 嵌入块 | - |

## 数据库表结构

### blocks 表
```sql
CREATE TABLE blocks (
  id TEXT PRIMARY KEY,      -- 块 ID
  created INTEGER,          -- 创建时间（毫秒时间戳）
  updated INTEGER,          -- 更新时间
  seq INTEGER,              -- 序列号
  content TEXT,             -- 内容
  markdown TEXT,            -- Markdown 内容
  type TEXT,                -- 块类型
  subType TEXT,             -- 子类型
  root_id TEXT,             -- 根文档 ID
  parent_id TEXT,           -- 父块 ID
  previous_id TEXT,         -- 前一个块 ID
  box TEXT                  -- 笔记本 ID
);
```

## 完整 Python 脚本示例

```python
#!/usr/bin/env python3
"""思源笔记 API 操作脚本"""

import requests
import json

API_URL = "http://127.0.0.1:6806"
API_TOKEN = "your-token-here"  # 从思源笔记「设置 - 关于」获取

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

def api_call(endpoint, data=None):
    """调用思源笔记 API"""
    url = f"{API_URL}{endpoint}"
    response = requests.post(url, headers=HEADERS, json=data or {})
    result = response.json()
    if result.get("code") != 0:
        raise Exception(f"API 错误：{result.get('msg')}")
    return result.get("data")

# 示例：列出所有笔记本
notebooks = api_call("/api/notebook/lsNotebooks")
print("笔记本列表:", json.dumps(notebooks, indent=2, ensure_ascii=False))

# 示例：创建文档
doc_id = api_call("/api/filetree/createDocWithMd", {
    "notebook": notebooks["notebooks"][0]["id"],
    "path": "/测试文档",
    "markdown": "# 测试\n\n这是通过 API 创建的文档。"
})
print(f"创建文档 ID: {doc_id}")

# 示例：SQL 查询
results = api_call("/api/query/sql", {
    "stmt": "SELECT * FROM blocks WHERE type='d' LIMIT 5"
})
print("文档列表:", json.dumps(results, indent=2, ensure_ascii=False))
```

## pitfalls

### 安全问题

#### 删除保护机制

本技能已实现**三层删除保护**：

1. **全局开关** - 客户端默认禁用删除 (`allow_delete=False`)
2. **二次确认** - 删除时需要输入资源 ID 进行验证
3. **审计日志** - 所有删除操作自动记录到 `~/.hermes/siyuan_delete_log.jsonl`

**使用示例**:
```python
from siyuan_client import SiYuanClient

# 默认情况下删除被禁用
client = SiYuanClient()

# 需要显式启用删除功能
client = SiYuanClient(allow_delete=True)

# 删除文档（会自动要求二次确认）
client.documents.remove(doc_id="20240101120000-abc1234", title="重要文档")

# 或者使用安全删除函数
from siyuan_delete_protect import safe_delete
safe_delete(client, "文档", "20240101120000-abc1234", "重要文档")
```

**查看删除历史**:
```bash
python ~/.hermes/skills/note-taking/siyuan-notes/scripts/siyuan_delete_protect.py history
```

#### 其他安全问题

1. **SQL 注入风险** - 避免直接在 SQL 查询中使用用户输入，应进行转义或限制
2. **Token 泄露** - 配置文件权限设置为 600，不要提交到版本控制
3. **端口暴露** - 确保 6806 端口不暴露到外网，防火墙限制只允许本地访问

### 技术问题

1. **API Token 错误** - 确保 Token 正确，在「设置 - 关于」中查看
2. **思源未运行** - API 调用前确认思源笔记已启动
3. **端口冲突** - 默认端口 6806，可在设置中修改
4. **发布模式限制** - 发布模式下 SQL 查询接口被禁用
5. **路径格式** - 文件路径必须以 `/` 开头，使用 `/` 分隔层级
6. **自定义属性前缀** - 必须以 `custom-` 开头
7. **块 ID 格式** - 时间戳格式如 `20240101120000-abc1234`
8. **Markdown 转义** - JSON 中的引号需要转义
9. **并发修改** - 避免同时修改同一块，可能导致冲突

## 验证步骤

1. 测试 API 连通性：
   ```bash
   curl -u "" -X POST "http://127.0.0.1:6806/api/system/version"
   ```

2. 列出笔记本确认鉴权：
   ```bash
   curl -u "" -X POST "http://127.0.0.1:6806/api/notebook/lsNotebooks" \
     -H "Authorization: Token your-token"
   ```

3. 执行简单 SQL 查询：
   ```bash
   curl -u "" -X POST "http://127.0.0.1:6806/api/query/sql" \
     -H "Authorization: Token your-token" \
     --data '{"stmt": "SELECT COUNT(*) FROM blocks"}'
   ```

## 相关技能

- `obsidian` - Obsidian 笔记操作
- `notion` - Notion API 操作
- `google-workspace` - Google Docs 集成
