# 思源笔记技能 - 安全分析报告

## 🔒 安全隐患分析

### 1. 高风险问题

#### ❌ SQL 注入风险
**问题**: SQL 查询接口直接拼接用户输入，没有参数化查询
```python
# 危险代码示例
client.query.search_content(keyword)
# 内部实现：f"SELECT * FROM blocks WHERE content LIKE '%{keyword}%'"
```

**攻击示例**:
```python
# 恶意输入
keyword = "%' UNION SELECT * FROM blocks WHERE '1'='1"
# 可能导致数据泄露或未授权访问
```

**修复方案**:
- 使用参数化查询（如果 API 支持）
- 对用户输入进行严格转义
- 限制查询范围和返回结果数量

---

#### ❌ API Token 明文存储
**问题**: Token 通过环境变量传递，可能被泄露
- 环境变量可能被 `ps` 命令查看
- 可能被日志记录
- 子进程可能继承环境变量

**修复方案**:
- 使用加密的配置文件
- 限制文件权限（chmod 600）
- 使用系统密钥管理（如 keyring）

---

#### ❌ 无访问控制
**问题**: 任何能调用脚本的人都可以执行所有操作
- 删除笔记本/文档无确认
- 批量删除无限制
- 敏感操作无审计日志

**修复方案**:
- 实现操作确认机制
- 添加操作审计日志
- 实现权限分级

---

### 2. 中风险问题

#### ⚠️ 本地 API 无 HTTPS
**问题**: API 默认使用 HTTP (127.0.0.1:6806)
- 数据明文传输
- 如果端口被转发到外网，风险极高

**修复方案**:
- 确保端口不暴露到外网
- 防火墙限制只允许本地访问
- 考虑使用思源笔记的 HTTPS 配置（如果支持）

---

#### ⚠️ 文件路径遍历风险
**问题**: 文件操作接口可能被滥用
```python
# 危险操作
client.files.get("/../../../etc/passwd")
```

**修复方案**:
- 验证路径必须在思源工作空间内
- 禁止 `..` 路径跳转
- 使用白名单验证

---

#### ⚠️ 资源上传无限制
**问题**: 上传接口无大小和类型限制
- 可能导致存储耗尽
- 可能上传恶意文件

**修复方案**:
- 限制文件大小
- 限制文件类型
- 扫描上传内容

---

### 3. 低风险问题

#### ⚪ 错误信息泄露
**问题**: API 错误直接返回给用户
- 可能暴露内部结构
- 可能泄露敏感信息

**修复方案**:
- 统一错误处理
- 脱敏错误信息

---

#### ⚪ 无速率限制
**问题**: 可以无限次调用 API
- 可能被用于 DoS 攻击
- 可能影响思源笔记性能

**修复方案**:
- 实现请求速率限制
- 添加重试机制

---

## 📁 安全配置方案

### 推荐配置位置

#### 方案 1: 环境变量（推荐用于开发）

```bash
# ~/.hermes/.env 或 ~/.bashrc
export SIYUAN_API_URL="http://127.0.0.1:6806"
export SIYUAN_API_TOKEN="your-secret-token"

# 设置文件权限
chmod 600 ~/.hermes/.env
```

**优点**: 简单，不落地
**缺点**: 环境变量可能泄露

---

#### 方案 2: 加密配置文件（推荐用于生产）

```bash
# 配置文件位置
~/.hermes/siyuan_config.json

# 文件内容
{
    "api_url": "http://127.0.0.1:6806",
    "api_token": "your-secret-token",
    "workspace_path": "~/SiYuan/workspace",
    "security": {
        "max_query_limit": 100,
        "allow_delete": false,
        "audit_log": true
    }
}

# 设置严格权限
chmod 600 ~/.hermes/siyuan_config.json
```

**优点**: 集中管理，可添加更多配置
**缺点**: 文件需要保护

---

#### 方案 3: 系统密钥环（最安全）

```bash
# 使用 Python keyring 存储 Token
python -c "import keyring; keyring.set_password('siyuan', 'api_token', 'your-token')"

# 读取时
python -c "import keyring; print(keyring.get_password('siyuan', 'api_token'))"
```

**优点**: 系统级加密存储
**缺点**: 需要额外依赖

---

## 🛡️ 安全加固建议

### 1. 网络隔离

```bash
# 防火墙规则 - 只允许本地访问
sudo ufw deny 6806
sudo ufw allow from 127.0.0.1 to any port 6806

# 或 iptables
sudo iptables -A INPUT -p tcp --dport 6806 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 6806 -j DROP
```

---

### 2. 思源笔记安全设置

在思源笔记中：
1. **设置 → 关于** - 定期更换 API Token
2. **设置 → 通用** - 禁用发布模式（如不需要）
3. **设置 → 导出** - 限制导出路径

---

### 3. 操作审计

```python
# 添加审计日志
import logging
from datetime import datetime

logging.basicConfig(
    filename='~/.hermes/siyuan_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_operation(operation, details):
    logging.info(f"{operation}: {details}")
```

---

### 4. 权限分级

```python
# 配置权限级别
PERMISSIONS = {
    "read_only": ["lsNotebooks", "exportMdContent", "query/sql"],
    "read_write": ["createDocWithMd", "updateBlock", "insertBlock"],
    "admin": ["removeNotebook", "removeDoc", "deleteBlock"]
}

# 根据 Token 级别限制操作
```

---

## ✅ 安全检查清单

使用前请确认：

- [ ] API Token 已安全存储（非明文）
- [ ] 配置文件权限设置为 600
- [ ] 防火墙限制 6806 端口只允许本地访问
- [ ] 思源笔记未启用外网访问
- [ ] 定期更换 API Token
- [ ] 敏感操作有确认机制
- [ ] 有操作审计日志
- [ ] SQL 查询有结果数量限制
- [ ] 文件上传有大小和类型限制

---

## 📋 安全使用指南

### 最小权限原则

```bash
# 只读操作 - 可以使用受限 Token
export SIYUAN_API_TOKEN="read-only-token"

# 写入操作 - 需要完整权限
export SIYUAN_API_TOKEN="full-access-token"
```

### 敏感操作确认

```python
# 删除前确认
def safe_delete(resource_type, resource_id):
    confirm = input(f"确认删除 {resource_type} ({resource_id})? (yes/no): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return False
    # 执行删除
```

### 定期安全审计

```bash
# 检查配置文件权限
ls -la ~/.hermes/siyuan_config.json

# 检查开放端口
netstat -tlnp | grep 6806

# 检查 API 调用日志
tail -f ~/.hermes/siyuan_audit.log
```

---

## 🚨 应急响应

如果发现安全事件：

1. **立即更换 API Token**（思源笔记 → 设置 → 关于）
2. **检查审计日志** 确认影响范围
3. **审查防火墙规则** 确保端口未暴露
4. **备份数据** 防止进一步损失
5. **报告安全事件** 给思源笔记团队

---

## 参考资源

- [思源笔记官方文档](https://github.com/siyuan-note/siyuan)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Python 安全最佳实践](https://docs.python.org/3/library/security.html)
