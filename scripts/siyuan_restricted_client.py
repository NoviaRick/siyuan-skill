#!/usr/bin/env python3
"""
思源笔记受限客户端 - 仅限「爱马仕整理」笔记本操作

安全限制:
- 只能对「爱马仕整理」笔记本进行增删改操作
- 其他笔记本只能读取，不允许任何修改
- 所有删除操作需要二次确认
"""

import json
import urllib.request
import urllib.error
import os
import sys
from typing import Optional, List, Dict, Any

# 配置
API_URL = "http://192.168.3.147:6806"
API_TOKEN = "c379msp2b54cdl10"
ALLOWED_NOTEBOOK_ID = "20260413070429-k17qjna"  # 爱马仕整理
ALLOWED_NOTEBOOK_NAME = "爱马仕整理"

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}


class SiYuanAPIError(Exception):
    """API 错误"""
    pass


class PermissionDeniedError(Exception):
    """权限拒绝错误"""
    pass


class DeleteConfirmationError(Exception):
    """删除确认错误"""
    pass


def api_call(endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
    """调用思源笔记 API"""
    url = f"{API_URL}{endpoint}"
    payload = json.dumps(data).encode('utf-8') if data else b'{}'
    
    req = urllib.request.Request(url, data=payload, headers=HEADERS, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("code") != 0:
                raise SiYuanAPIError(f"API 错误：{result.get('msg')}")
            return result.get("data")
    except urllib.error.HTTPError as e:
        raise SiYuanAPIError(f"HTTP 错误：{e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise SiYuanAPIError(f"连接错误：{e.reason}")


def confirm_delete(resource_type: str, resource_id: str, extra_info: str = "") -> bool:
    """删除操作二次确认"""
    print("\n⚠️  删除操作确认", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print(f"资源类型：{resource_type}", file=sys.stderr)
    print(f"资源 ID:  {resource_id}", file=sys.stderr)
    if extra_info:
        print(f"详细信息：{extra_info}", file=sys.stderr)
    print("\n⚠️  此操作不可逆！数据将永久丢失！", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    user_input = input(f"\n请输入 '{resource_id}' 确认删除 (或输入 no 取消): ").strip()
    
    if user_input == resource_id:
        print(f"✅ 已确认删除", file=sys.stderr)
        return True
    else:
        print(f"❌ 已取消删除操作", file=sys.stderr)
        return False


def check_notebook_permission(notebook_id: str, operation: str = "修改") -> None:
    """检查笔记本权限"""
    if notebook_id != ALLOWED_NOTEBOOK_ID:
        raise PermissionDeniedError(
            f"❌ 权限拒绝：只能对「{ALLOWED_NOTEBOOK_NAME}」笔记本进行{operation}操作\n"
            f"   当前笔记本 ID: {notebook_id}\n"
            f"   允许笔记本 ID: {ALLOWED_NOTEBOOK_ID}\n"
            f"   💡 其他笔记本只能读取，不允许增删改"
        )


def get_notebook_info(notebook_id: str) -> str:
    """获取笔记本信息（用于错误提示）"""
    try:
        notebooks = api_call("/api/notebook/lsNotebooks")
        for nb in notebooks.get("notebooks", []):
            if nb["id"] == notebook_id:
                return nb["name"]
    except:
        pass
    return "未知笔记本"


class RestrictedNotebookManager:
    """受限笔记本管理（只能操作允许的笔记本）"""
    
    def __init__(self, client=None):
        self.client = client
    
    def list(self) -> Dict[str, Any]:
        """列出所有笔记本（只读，允许）"""
        return api_call("/api/notebook/lsNotebooks")
    
    def get_config(self, notebook_id: str) -> Dict[str, Any]:
        """获取笔记本配置（只读，允许）"""
        return api_call("/api/notebook/getNotebookConf", {"notebook": notebook_id})
    
    def create(self, name: str) -> Dict[str, Any]:
        """创建笔记本 - ❌ 禁止"""
        raise PermissionDeniedError("❌ 禁止创建新笔记本")
    
    def remove(self, notebook_id: str, **kwargs) -> None:
        """删除笔记本 - ❌ 禁止"""
        raise PermissionDeniedError("❌ 禁止删除笔记本")
    
    def rename(self, notebook_id: str, name: str) -> None:
        """重命名笔记本 - ❌ 禁止"""
        raise PermissionDeniedError("❌ 禁止重命名笔记本")
    
    def open(self, notebook_id: str) -> None:
        """打开笔记本 - ✅ 允许"""
        api_call("/api/notebook/openNotebook", {"notebook": notebook_id})
    
    def close(self, notebook_id: str) -> None:
        """关闭笔记本 - ✅ 允许"""
        api_call("/api/notebook/closeNotebook", {"notebook": notebook_id})
    
    def set_config(self, notebook_id: str, config: Dict[str, Any]) -> None:
        """保存笔记本配置 - ❌ 禁止"""
        raise PermissionDeniedError("❌ 禁止修改笔记本配置")


class RestrictedDocumentManager:
    """受限文档管理"""
    
    def __init__(self, client=None):
        self.client = client
    
    def create(self, notebook_id: str, path: str, markdown: str) -> str:
        """创建文档 - 仅限允许的笔记本"""
        check_notebook_permission(notebook_id, "创建文档")
        return api_call("/api/filetree/createDocWithMd", {
            "notebook": notebook_id,
            "path": path,
            "markdown": markdown
        })
    
    def remove(self, doc_id: str, confirm: bool = True, title: str = "") -> None:
        """删除文档 - 仅限允许的笔记本"""
        # 先获取文档所属笔记本
        try:
            path_info = api_call("/api/filetree/getPathByID", {"id": doc_id})
            nb_id = path_info.get("notebook", "")
            check_notebook_permission(nb_id, "删除文档")
        except PermissionDeniedError:
            raise
        except Exception as e:
            # 如果无法获取笔记本信息，默认拒绝
            raise PermissionDeniedError(f"❌ 无法确认文档所属笔记本，删除被拒绝：{e}")
        
        # 二次确认
        if confirm:
            extra = f"标题：{title}" if title else ""
            if not confirm_delete("文档", doc_id, extra):
                raise DeleteConfirmationError(f"用户取消删除文档 {doc_id}")
        
        api_call("/api/filetree/removeDocByID", {"id": doc_id})
    
    def rename(self, doc_id: str, title: str) -> None:
        """重命名文档 - 仅限允许的笔记本"""
        try:
            path_info = api_call("/api/filetree/getPathByID", {"id": doc_id})
            nb_id = path_info.get("notebook", "")
            check_notebook_permission(nb_id, "重命名文档")
        except PermissionDeniedError:
            raise
        except Exception as e:
            raise PermissionDeniedError(f"❌ 无法确认文档所属笔记本：{e}")
        
        api_call("/api/filetree/renameDocByID", {"id": doc_id, "title": title})
    
    def move(self, from_ids: List[str], to_id: str) -> None:
        """移动文档 - 仅限允许的笔记本"""
        # 检查目标笔记本
        check_notebook_permission(to_id, "移动文档到")
        
        # 检查源文档
        for doc_id in from_ids:
            try:
                path_info = api_call("/api/filetree/getPathByID", {"id": doc_id})
                nb_id = path_info.get("notebook", "")
                check_notebook_permission(nb_id, "移动文档")
            except PermissionDeniedError:
                raise
            except Exception as e:
                raise PermissionDeniedError(f"❌ 无法确认文档所属笔记本：{e}")
        
        api_call("/api/filetree/moveDocsByID", {"fromIDs": from_ids, "toID": to_id})
    
    def export(self, doc_id: str) -> Dict[str, str]:
        """导出 Markdown 内容（只读，允许）"""
        return api_call("/api/export/exportMdContent", {"id": doc_id})
    
    def get_path(self, doc_id: str) -> str:
        """获取文档路径（只读，允许）"""
        return api_call("/api/filetree/getHPathByID", {"id": doc_id})


class RestrictedBlockManager:
    """受限块管理"""
    
    def __init__(self, client=None):
        self.client = client
    
    def insert(self, data: str, parent_id: str = None, 
               previous_id: str = None, next_id: str = None,
               data_type: str = "markdown") -> List[Dict[str, Any]]:
        """插入块 - 检查父块所属笔记本"""
        # 获取父块的笔记本
        if parent_id:
            try:
                path_info = api_call("/api/filetree/getPathByID", {"id": parent_id})
                nb_id = path_info.get("notebook", "")
                check_notebook_permission(nb_id, "插入块")
            except PermissionDeniedError:
                raise
            except Exception as e:
                raise PermissionDeniedError(f"❌ 无法确认父块所属笔记本：{e}")
        
        payload = {"dataType": data_type, "data": data}
        if parent_id:
            payload["parentID"] = parent_id
        if previous_id:
            payload["previousID"] = previous_id
        if next_id:
            payload["nextID"] = next_id
        
        return api_call("/api/block/insertBlock", payload)
    
    def delete(self, block_id: str, confirm: bool = True, content_preview: str = "") -> List[Dict[str, Any]]:
        """删除块 - 检查块所属笔记本"""
        # 获取块的笔记本
        try:
            path_info = api_call("/api/filetree/getPathByID", {"id": block_id})
            nb_id = path_info.get("notebook", "")
            check_notebook_permission(nb_id, "删除块")
        except PermissionDeniedError:
            raise
        except Exception as e:
            raise PermissionDeniedError(f"❌ 无法确认块所属笔记本：{e}")
        
        # 二次确认
        if confirm:
            if content_preview and len(content_preview) > 50:
                content_preview = content_preview[:50] + "..."
            extra = f"内容：{content_preview}" if content_preview else ""
            if not confirm_delete("块", block_id, extra):
                raise DeleteConfirmationError(f"用户取消删除块 {block_id}")
        
        return api_call("/api/block/deleteBlock", {"id": block_id})
    
    def update(self, block_id: str, data: str, data_type: str = "markdown") -> List[Dict[str, Any]]:
        """更新块 - 检查块所属笔记本"""
        try:
            path_info = api_call("/api/filetree/getPathByID", {"id": block_id})
            nb_id = path_info.get("notebook", "")
            check_notebook_permission(nb_id, "更新块")
        except PermissionDeniedError:
            raise
        except Exception as e:
            raise PermissionDeniedError(f"❌ 无法确认块所属笔记本：{e}")
        
        return api_call("/api/block/updateBlock", {
            "id": block_id,
            "dataType": data_type,
            "data": data
        })
    
    def get_children(self, parent_id: str) -> List[Dict[str, str]]:
        """获取子块（只读，允许）"""
        return api_call("/api/block/getChildBlocks", {"id": parent_id})


class RestrictedQueryManager:
    """受限查询管理（只读，允许）"""
    
    def __init__(self, client=None):
        self.client = client
    
    def execute(self, sql: str) -> List[Dict[str, Any]]:
        """执行 SQL 查询（只读，允许）"""
        return api_call("/api/query/sql", {"stmt": sql})
    
    def search_content(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索内容"""
        return self.execute(f"SELECT * FROM blocks WHERE content LIKE '%{keyword}%' LIMIT {limit}")
    
    def search_in_allowed_notebook(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """仅在允许的笔记本中搜索"""
        sql = f"SELECT * FROM blocks WHERE box='{ALLOWED_NOTEBOOK_ID}' AND content LIKE '%{keyword}%' LIMIT {limit}"
        return self.execute(sql)
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近更新的块"""
        return self.execute(f"SELECT * FROM blocks ORDER BY updated DESC LIMIT {limit}")
    
    def count_in_allowed_notebook(self) -> int:
        """统计允许的笔记本中的文档数量"""
        result = self.execute(f"SELECT COUNT(*) as count FROM blocks WHERE box='{ALLOWED_NOTEBOOK_ID}' AND type='d'")
        return result[0].get('count', 0) if result else 0


class RestrictedSiYuanClient:
    """
    受限思源笔记客户端
    
    安全限制:
    - 只能对「爱马仕整理」笔记本进行增删改操作
    - 其他笔记本只能读取
    - 所有删除操作需要二次确认
    """
    
    def __init__(self):
        self.api_url = API_URL
        self.api_token = API_TOKEN
        self.allowed_notebook_id = ALLOWED_NOTEBOOK_ID
        self.allowed_notebook_name = ALLOWED_NOTEBOOK_NAME
        
        # 管理器
        self.notebooks = RestrictedNotebookManager(self)
        self.documents = RestrictedDocumentManager(self)
        self.blocks = RestrictedBlockManager(self)
        self.query = RestrictedQueryManager(self)
    
    def ping(self) -> bool:
        """检查连接"""
        try:
            self.version()
            return True
        except:
            return False
    
    def version(self) -> str:
        """获取思源版本"""
        return api_call("/api/system/version")
    
    def get_allowed_notebook(self) -> Dict[str, str]:
        """获取允许的笔记本信息"""
        return {
            "id": ALLOWED_NOTEBOOK_ID,
            "name": ALLOWED_NOTEBOOK_NAME
        }


# 便捷函数
def create_client() -> RestrictedSiYuanClient:
    """创建受限客户端"""
    return RestrictedSiYuanClient()


if __name__ == "__main__":
    # 使用示例
    print("思源笔记受限客户端")
    print("=" * 50)
    
    client = create_client()
    
    # 检查连接
    if client.ping():
        print(f"✅ 连接成功 - 思源版本：{client.version()}")
        print(f"\n📋 权限说明:")
        print(f"   允许操作的笔记本：{client.allowed_notebook_name} ({client.allowed_notebook_id})")
        print(f"   其他笔记本：只读，不允许增删改")
    else:
        print("❌ 无法连接到思源笔记")
        sys.exit(1)
    
    # 列出笔记本
    print(f"\n📚 所有笔记本:")
    notebooks = client.notebooks.list()
    for nb in notebooks.get("notebooks", []):
        if nb["id"] == client.allowed_notebook_id:
            print(f"   ✅ {nb['name']} (ID: {nb['id']}) - 可读写")
        else:
            print(f"   🔒 {nb['name']} (ID: {nb['id']}) - 只读")
    
    # 统计允许的笔记本中的文档数
    count = client.query.count_in_allowed_notebook()
    print(f"\n📊 「{client.allowed_notebook_name}」中有 {count} 篇文档")
