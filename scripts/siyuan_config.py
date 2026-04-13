#!/usr/bin/env python3
"""
思源笔记配置管理工具
安全地管理 API URL 和 Token 配置

用法:
    python siyuan_config.py init      # 初始化配置
    python siyuan_config.py show      # 显示当前配置
    python siyuan_config.py update    # 更新配置
    python siyuan_config.py verify    # 验证配置
    python siyuan_config.py rotate    # 轮换 Token
    python siyuan_config.py check     # 安全检查
"""

import os
import sys
import json
import stat
import urllib.request
import urllib.error
from pathlib import Path

# 配置路径
CONFIG_DIR = Path.home() / ".hermes"
CONFIG_FILE = CONFIG_DIR / "siyuan_config.json"
ENV_FILE = CONFIG_DIR / ".env"


def ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(CONFIG_DIR, stat.S_IRWXU)


def load_config():
    """加载配置"""
    if not CONFIG_FILE.exists():
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            file_stat = os.stat(CONFIG_FILE)
            if file_stat.st_mode & stat.S_IROTH:
                print("⚠️ 警告：配置文件权限过于宽松")
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误：{e}")
        return None


def save_config(config):
    """保存配置"""
    ensure_config_dir()
    temp_file = CONFIG_FILE.with_suffix('.tmp')
    with open(temp_file, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    os.chmod(temp_file, stat.S_IRUSR | stat.S_IWUSR)
    temp_file.replace(CONFIG_FILE)
    print(f"✅ 配置已保存到 {CONFIG_FILE} (权限 600)")


def init_config():
    """初始化配置"""
    print("🔧 思源笔记配置初始化\n")
    print("📝 获取 API Token:")
    print("   1. 打开思源笔记 → 设置 → 关于 → API Token")
    print("   2. 复制 Token 粘贴到下方\n")
    
    config = load_config() or {}
    
    api_url = input(f"API URL [http://127.0.0.1:6806]: ").strip() or "http://127.0.0.1:6806"
    api_token = input("API Token: ").strip()
    
    if not api_token:
        print("❌ Token 不能为空")
        return False
    
    config["api_url"] = api_url.rstrip('/')
    config["api_token"] = api_token
    config.setdefault("security", {"max_query_limit": 100, "allow_delete": False, "audit_log": True})
    
    save_config(config)
    print("\n✅ 配置初始化成功！")
    return verify_config(config)


def show_config():
    """显示配置"""
    config = load_config()
    if not config:
        print("❌ 未找到配置文件，运行 'python siyuan_config.py init' 初始化")
        return
    
    print("📋 当前配置\n" + "-" * 40)
    print(f"API URL:   {config.get('api_url', '未设置')}")
    token = config.get('api_token', '')
    print(f"API Token: {token[:8]}...{token[-4:]}" if token else "未设置")
    
    sec = config.get("security", {})
    print(f"\n🔒 安全设置:")
    print(f"  查询限制：{sec.get('max_query_limit', 100)} 条")
    print(f"  允许删除：{'是' if sec.get('allow_delete') else '否'}")
    
    if CONFIG_FILE.exists():
        perms = oct(os.stat(CONFIG_FILE).st_mode)[-3:]
        print(f"\n📁 文件权限：{perms} ({CONFIG_FILE})")
        if perms != "600":
            print("⚠️ 建议：chmod 600 ~/.hermes/siyuan_config.json")


def verify_config(config=None):
    """验证配置"""
    config = config or load_config()
    if not config:
        print("❌ 未找到配置文件")
        return False
    
    print("🔍 验证连接...")
    try:
        url = f"{config['api_url']}/api/system/version"
        headers = {"Authorization": f"Token {config['api_token']}", "Content-Type": "application/json"}
        req = urllib.request.Request(url, data=b'{}', headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("code") == 0:
                print(f"✅ 连接成功 - 思源版本：{result.get('data')}")
                
                # 测试笔记本
                url = f"{config['api_url']}/api/notebook/lsNotebooks"
                req = urllib.request.Request(url, data=b'{}', headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=5) as r:
                    res = json.loads(r.read().decode('utf-8'))
                    if res.get("code") == 0:
                        nbs = res.get("data", {}).get("notebooks", [])
                        print(f"📚 笔记本数量：{len(nbs)}")
                        print("✅ 配置验证通过！")
                        return True
            print(f"❌ API 错误：{result.get('msg')}")
            return False
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {'Token 无效' if e.code == 401 else e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ 连接失败：{e.reason}")
        print("💡 确认思源笔记运行且 API 已启用")
        return False


def rotate_token():
    """轮换 Token"""
    print("🔄 Token 轮换\n⚠️ 旧 Token 将失效\n")
    config = load_config()
    if not config:
        print("❌ 未找到配置文件")
        return False
    
    new_token = input("新 API Token: ").strip()
    if not new_token:
        print("❌ Token 不能为空")
        return False
    
    # 备份
    backup = CONFIG_FILE.with_suffix('.bak')
    with open(backup, 'w') as f:
        json.dump(config, f, indent=2)
    os.chmod(backup, stat.S_IRUSR | stat.S_IWUSR)
    
    config["api_token"] = new_token
    save_config(config)
    
    if verify_config(config):
        print(f"\n✅ Token 轮换成功！备份：{backup}")
        return True
    print(f"\n⚠️ 验证失败，恢复：cp {backup} {CONFIG_FILE}")
    return False


def check_security():
    """安全检查"""
    print("🔒 安全检查\n" + "-" * 40)
    issues = []
    
    if CONFIG_FILE.exists():
        perms = oct(os.stat(CONFIG_FILE).st_mode)[-3:]
        if perms != "600":
            issues.append(f"配置文件权限 {perms}，建议 600")
    else:
        issues.append("配置文件不存在")
    
    config = load_config()
    if config and len(config.get("api_token", "")) < 16:
        issues.append("Token 长度异常")
    
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        if s.connect_ex(('127.0.0.1', 6806)) != 0:
            issues.append("思源笔记可能未运行 (端口 6806)")
        s.close()
    except:
        pass
    
    if issues:
        print("⚠️ 安全问题:")
        for i, x in enumerate(issues, 1):
            print(f"  {i}. {x}")
    else:
        print("✅ 未发现安全问题")
    return len(issues) == 0


if __name__ == "__main__":
    cmds = {
        "init": init_config,
        "show": show_config,
        "verify": verify_config,
        "rotate": rotate_token,
        "check": check_security,
        "update": init_config,
    }
    
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        sys.exit(1)
    
    success = cmds[sys.argv[1]]()
    sys.exit(0 if success else 1)
