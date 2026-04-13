#!/usr/bin/env python3
"""
思源笔记 API 工具脚本
用法：python siyuan_api.py <命令> [参数]

命令:
  ls-notebooks        列出所有笔记本
  create-notebook     创建笔记本
  create-doc          创建文档
  search              SQL 搜索
  get-doc             获取文档内容
  insert-block        插入块
  update-block        更新块
  delete-block        删除块
  set-attrs           设置块属性
  get-attrs           获取块属性
  version             获取思源版本
"""

import sys
import os
import json
import urllib.request
import urllib.error

# 配置
API_URL = os.getenv("SIYUAN_API_URL", "http://127.0.0.1:6806")
API_TOKEN = os.getenv("SIYUAN_API_TOKEN", "")

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}


def api_call(endpoint, data=None):
    """调用思源笔记 API"""
    url = f"{API_URL}{endpoint}"
    payload = json.dumps(data).encode('utf-8') if data else b'{}'
    
    req = urllib.request.Request(url, data=payload, headers=HEADERS, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("code") != 0:
                print(f"❌ API 错误：{result.get('msg')}", file=sys.stderr)
                sys.exit(1)
            return result.get("data")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP 错误：{e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ 连接错误：{e.reason}", file=sys.stderr)
        print("💡 请确认思源笔记正在运行且 API 已启用", file=sys.stderr)
        sys.exit(1)


def ls_notebooks():
    """列出所有笔记本"""
    data = api_call("/api/notebook/lsNotebooks")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def create_notebook(name):
    """创建笔记本"""
    data = api_call("/api/notebook/createNotebook", {"name": name})
    print(f"✅ 创建笔记本成功:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def create_doc(notebook_id, path, markdown):
    """创建文档"""
    doc_id = api_call("/api/filetree/createDocWithMd", {
        "notebook": notebook_id,
        "path": path,
        "markdown": markdown
    })
    print(f"✅ 创建文档成功，ID: {doc_id}")


def search(sql):
    """SQL 搜索"""
    results = api_call("/api/query/sql", {"stmt": sql})
    print(json.dumps(results, indent=2, ensure_ascii=False))


def get_doc_content(doc_id):
    """获取文档内容"""
    data = api_call("/api/export/exportMdContent", {"id": doc_id})
    print(f"📄 路径：{data.get('hPath')}")
    print("-" * 50)
    print(data.get('content', ''))


def insert_block(data_text, previous_id=None, parent_id=None, next_id=None):
    """插入块"""
    payload = {
        "dataType": "markdown",
        "data": data_text
    }
    if previous_id:
        payload["previousID"] = previous_id
    if parent_id:
        payload["parentID"] = parent_id
    if next_id:
        payload["nextID"] = next_id
    
    result = api_call("/api/block/insertBlock", payload)
    print(f"✅ 插入块成功:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def update_block(block_id, data_text):
    """更新块"""
    result = api_call("/api/block/updateBlock", {
        "id": block_id,
        "dataType": "markdown",
        "data": data_text
    })
    print(f"✅ 更新块 {block_id} 成功")


def delete_block(block_id):
    """删除块"""
    result = api_call("/api/block/deleteBlock", {"id": block_id})
    print(f"✅ 删除块 {block_id} 成功")


def set_attrs(block_id, attrs):
    """设置块属性"""
    # 确保自定义属性以 custom- 开头
    processed_attrs = {}
    for key, value in attrs.items():
        if not key.startswith("custom-"):
            key = f"custom-{key}"
        processed_attrs[key] = value
    
    api_call("/api/attr/setBlockAttrs", {
        "id": block_id,
        "attrs": processed_attrs
    })
    print(f"✅ 设置块属性成功")


def get_attrs(block_id):
    """获取块属性"""
    attrs = api_call("/api/attr/getBlockAttrs", {"id": block_id})
    print(json.dumps(attrs, indent=2, ensure_ascii=False))


def get_version():
    """获取思源版本"""
    version = api_call("/api/system/version")
    print(f"思源笔记版本：{version}")


def print_usage():
    """打印使用说明"""
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "ls-notebooks":
        ls_notebooks()
    
    elif command == "create-notebook":
        if len(sys.argv) < 3:
            print("❌ 用法：python siyuan_api.py create-notebook <笔记本名称>")
            sys.exit(1)
        create_notebook(sys.argv[2])
    
    elif command == "create-doc":
        if len(sys.argv) < 5:
            print("❌ 用法：python siyuan_api.py create-doc <笔记本 ID> <路径> <Markdown 内容>")
            sys.exit(1)
        create_doc(sys.argv[2], sys.argv[3], sys.argv[4])
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ 用法：python siyuan_api.py search <SQL 语句>")
            sys.exit(1)
        search(sys.argv[2])
    
    elif command == "get-doc":
        if len(sys.argv) < 3:
            print("❌ 用法：python siyuan_api.py get-doc <文档 ID>")
            sys.exit(1)
        get_doc_content(sys.argv[2])
    
    elif command == "insert-block":
        if len(sys.argv) < 3:
            print("❌ 用法：python siyuan_api.py insert-block <内容> [previousID] [parentID]")
            sys.exit(1)
        insert_block(sys.argv[2], 
                    sys.argv[3] if len(sys.argv) > 3 else None,
                    sys.argv[4] if len(sys.argv) > 4 else None)
    
    elif command == "update-block":
        if len(sys.argv) < 4:
            print("❌ 用法：python siyuan_api.py update-block <块 ID> <新内容>")
            sys.exit(1)
        update_block(sys.argv[2], sys.argv[3])
    
    elif command == "delete-block":
        if len(sys.argv) < 3:
            print("❌ 用法：python siyuan_api.py delete-block <块 ID>")
            sys.exit(1)
        delete_block(sys.argv[2])
    
    elif command == "set-attrs":
        if len(sys.argv) < 4:
            print("❌ 用法：python siyuan_api.py set-attrs <块 ID> <JSON 属性>")
            sys.exit(1)
        attrs = json.loads(sys.argv[3])
        set_attrs(sys.argv[2], attrs)
    
    elif command == "get-attrs":
        if len(sys.argv) < 3:
            print("❌ 用法：python siyuan_api.py get-attrs <块 ID>")
            sys.exit(1)
        get_attrs(sys.argv[2])
    
    elif command == "version":
        get_version()
    
    else:
        print(f"❌ 未知命令：{command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
