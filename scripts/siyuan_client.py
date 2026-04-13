#!/usr/bin/env python3
"""
思源笔记 Python 客户端库
提供面向对象的 API 封装

用法:
    from siyuan_client import SiYuanClient
    
    client = SiYuanClient()
    
    # 列出笔记本
    notebooks = client.notebooks.list()
    
    # 创建文档
    doc_id = client.documents.create(notebook_id, "/path", "# 标题\n\n内容")
    
    # SQL 搜索
    results = client.query("SELECT * FROM blocks WHERE content LIKE '%关键词%'")
    
    # 操作块
    client.blocks.insert("内容", previous_id="xxx")
    client.blocks.update(block_id, "新内容")
"""

import json
import urllib.request
import urllib.error
import os
import sys
from typing import Optional, List, Dict, Any


class SiYuanAPIError(Exception):
    """思源笔记 API 错误"""
    pass


class SiYuanConnectionError(Exception):
    """思源笔记连接错误"""
    pass


class DeleteConfirmationError(Exception):
    """删除操作未确认"""
    pass


def confirm_delete(resource_type: str, resource_id: str, extra_info: str = "") -> bool:
    """
    删除操作二次确认
    
    Args:
        resource_type: 资源类型（笔记本/文档/块/文件）
        resource_id: 资源 ID
        extra_info: 额外信息（如标题、路径等）
    
    Returns:
        bool: 用户是否确认删除
    """
    print("\n⚠️  删除操作确认", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print(f"资源类型：{resource_type}", file=sys.stderr)
    print(f"资源 ID:  {resource_id}", file=sys.stderr)
    if extra_info:
        print(f"详细信息：{extra_info}", file=sys.stderr)
    print("\n⚠️  此操作不可逆！数据将永久丢失！", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    # 要求用户输入资源 ID 进行确认
    user_input = input(f"\n请输入 '{resource_id}' 确认删除 (或输入 no 取消): ").strip()
    
    if user_input == resource_id:
        print(f"✅ 已确认删除 {resource_type}: {resource_id}", file=sys.stderr)
        return True
    elif user_input.lower() in ('no', 'n', 'cancel'):
        print(f"❌ 已取消删除操作", file=sys.stderr)
        return False
    else:
        print(f"❌ 输入不匹配，已取消删除操作", file=sys.stderr)
        return False


class NotebookManager:
    """笔记本管理"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self) -> Dict[str, Any]:
        """列出所有笔记本"""
        return self.client._call("/api/notebook/lsNotebooks")
    
    def create(self, name: str) -> Dict[str, Any]:
        """创建笔记本"""
        return self.client._call("/api/notebook/createNotebook", {"name": name})
    
    def open(self, notebook_id: str) -> None:
        """打开笔记本"""
        self.client._call("/api/notebook/openNotebook", {"notebook": notebook_id})
    
    def close(self, notebook_id: str) -> None:
        """关闭笔记本"""
        self.client._call("/api/notebook/closeNotebook", {"notebook": notebook_id})
    
    def rename(self, notebook_id: str, name: str) -> None:
        """重命名笔记本"""
        self.client._call("/api/notebook/renameNotebook", 
                         {"notebook": notebook_id, "name": name})
    
    def remove(self, notebook_id: str, confirm: bool = True, name: str = "") -> None:
        """
        删除笔记本（需要二次确认）
        
        Args:
            notebook_id: 笔记本 ID
            confirm: 是否需要确认，默认 True
            name: 笔记本名称（用于确认提示）
        """
        # 检查全局删除开关
        if not self.client.allow_delete:
            raise SiYuanAPIError("删除操作已被禁用，需要在客户端中设置 allow_delete=True")
        
        # 使用全局配置或显式覆盖
        confirm = confirm if confirm is not None else self.client.require_delete_confirm
        
        if confirm:
            extra = f"名称：{name}" if name else ""
            if not confirm_delete("笔记本", notebook_id, extra):
                raise DeleteConfirmationError(f"用户取消删除笔记本 {notebook_id}")
        self.client._call("/api/notebook/removeNotebook", {"notebook": notebook_id})
    
    def get_config(self, notebook_id: str) -> Dict[str, Any]:
        """获取笔记本配置"""
        return self.client._call("/api/notebook/getNotebookConf", 
                                {"notebook": notebook_id})
    
    def set_config(self, notebook_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """保存笔记本配置"""
        return self.client._call("/api/notebook/setNotebookConf",
                                {"notebook": notebook_id, "conf": config})


class DocumentManager:
    """文档管理"""
    
    def __init__(self, client):
        self.client = client
    
    def create(self, notebook_id: str, path: str, markdown: str) -> str:
        """
        通过 Markdown 创建文档
        
        Args:
            notebook_id: 笔记本 ID
            path: 文档路径，如 "/文件夹/文档名"
            markdown: Markdown 内容
            
        Returns:
            创建的文档 ID
        """
        return self.client._call("/api/filetree/createDocWithMd", {
            "notebook": notebook_id,
            "path": path,
            "markdown": markdown
        })
    
    def rename(self, doc_id: str, title: str) -> None:
        """重命名文档（通过 ID）"""
        self.client._call("/api/filetree/renameDocByID", 
                         {"id": doc_id, "title": title})
    
    def remove(self, doc_id: str, confirm: bool = True, title: str = "") -> None:
        """
        删除文档（需要二次确认）
        
        Args:
            doc_id: 文档 ID
            confirm: 是否需要确认，默认 True
            title: 文档标题（用于确认提示）
        """
        # 检查全局删除开关
        if not self.client.allow_delete:
            raise SiYuanAPIError("删除操作已被禁用，需要在客户端中设置 allow_delete=True")
        
        # 使用全局配置或显式覆盖
        confirm = confirm if confirm is not None else self.client.require_delete_confirm
        
        if confirm:
            extra = f"标题：{title}" if title else ""
            if not confirm_delete("文档", doc_id, extra):
                raise DeleteConfirmationError(f"用户取消删除文档 {doc_id}")
        self.client._call("/api/filetree/removeDocByID", {"id": doc_id})
    
    def move(self, from_ids: List[str], to_id: str) -> None:
        """移动文档"""
        self.client._call("/api/filetree/moveDocsByID", 
                         {"fromIDs": from_ids, "toID": to_id})
    
    def export(self, doc_id: str) -> Dict[str, str]:
        """导出 Markdown 内容"""
        return self.client._call("/api/export/exportMdContent", {"id": doc_id})
    
    def get_path(self, doc_id: str) -> str:
        """根据 ID 获取人类可读路径"""
        return self.client._call("/api/filetree/getHPathByID", {"id": doc_id})
    
    def get_storage_path(self, doc_id: str) -> Dict[str, str]:
        """根据 ID 获取存储路径"""
        return self.client._call("/api/filetree/getPathByID", {"id": doc_id})


class BlockManager:
    """块管理"""
    
    def __init__(self, client):
        self.client = client
    
    def insert(self, data: str, data_type: str = "markdown",
               previous_id: Optional[str] = None,
               next_id: Optional[str] = None,
               parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        插入块
        
        Args:
            data: 块内容
            data_type: 数据类型，"markdown" 或 "dom"
            previous_id: 前一个块 ID
            next_id: 后一个块 ID
            parent_id: 父块 ID
            
        Returns:
            插入操作结果
        """
        payload = {
            "dataType": data_type,
            "data": data
        }
        if previous_id:
            payload["previousID"] = previous_id
        if next_id:
            payload["nextID"] = next_id
        if parent_id:
            payload["parentID"] = parent_id
        
        return self.client._call("/api/block/insertBlock", payload)
    
    def prepend(self, data: str, parent_id: str, data_type: str = "markdown") -> List[Dict[str, Any]]:
        """插入前置子块"""
        return self.client._call("/api/block/prependBlock", {
            "dataType": data_type,
            "data": data,
            "parentID": parent_id
        })
    
    def append(self, data: str, parent_id: str, data_type: str = "markdown") -> List[Dict[str, Any]]:
        """插入后置子块"""
        return self.client._call("/api/block/appendBlock", {
            "dataType": data_type,
            "data": data,
            "parentID": parent_id
        })
    
    def update(self, block_id: str, data: str, data_type: str = "markdown") -> List[Dict[str, Any]]:
        """更新块"""
        return self.client._call("/api/block/updateBlock", {
            "id": block_id,
            "dataType": data_type,
            "data": data
        })
    
    def delete(self, block_id: str, confirm: bool = True, content_preview: str = "") -> List[Dict[str, Any]]:
        """
        删除块（需要二次确认）
        
        Args:
            block_id: 块 ID
            confirm: 是否需要确认，默认 True
            content_preview: 内容预览（用于确认提示）
            
        Returns:
            删除操作结果
        """
        # 检查全局删除开关
        if not self.client.allow_delete:
            raise SiYuanAPIError("删除操作已被禁用，需要在客户端中设置 allow_delete=True")
        
        # 使用全局配置或显式覆盖
        confirm = confirm if confirm is not None else self.client.require_delete_confirm
        
        if confirm:
            # 截断过长的内容预览
            if content_preview and len(content_preview) > 50:
                content_preview = content_preview[:50] + "..."
            extra = f"内容：{content_preview}" if content_preview else ""
            if not confirm_delete("块", block_id, extra):
                raise DeleteConfirmationError(f"用户取消删除块 {block_id}")
        return self.client._call("/api/block/deleteBlock", {"id": block_id})
    
    def move(self, block_id: str, 
             previous_id: Optional[str] = None,
             parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """移动块"""
        payload = {"id": block_id}
        if previous_id:
            payload["previousID"] = previous_id
        if parent_id:
            payload["parentID"] = parent_id
        return self.client._call("/api/block/moveBlock", payload)
    
    def fold(self, block_id: str) -> None:
        """折叠块"""
        self.client._call("/api/block/foldBlock", {"id": block_id})
    
    def unfold(self, block_id: str) -> None:
        """展开块"""
        self.client._call("/api/block/unfoldBlock", {"id": block_id})
    
    def get_kramdown(self, block_id: str) -> Dict[str, str]:
        """获取块 kramdown 源码"""
        return self.client._call("/api/block/getBlockKramdown", {"id": block_id})
    
    def get_children(self, parent_id: str) -> List[Dict[str, str]]:
        """获取子块"""
        return self.client._call("/api/block/getChildBlocks", {"id": parent_id})


class AttributeManager:
    """属性管理"""
    
    def __init__(self, client):
        self.client = client
    
    def set(self, block_id: str, attrs: Dict[str, str]) -> None:
        """
        设置块属性
        
        Args:
            block_id: 块 ID
            attrs: 属性字典，会自动添加 custom- 前缀
        """
        processed_attrs = {}
        for key, value in attrs.items():
            if not key.startswith("custom-"):
                key = f"custom-{key}"
            processed_attrs[key] = value
        
        self.client._call("/api/attr/setBlockAttrs", {
            "id": block_id,
            "attrs": processed_attrs
        })
    
    def get(self, block_id: str) -> Dict[str, Any]:
        """获取块属性"""
        return self.client._call("/api/attr/getBlockAttrs", {"id": block_id})


class QueryManager:
    """SQL 查询管理"""
    
    def __init__(self, client):
        self.client = client
    
    def execute(self, sql: str) -> List[Dict[str, Any]]:
        """执行 SQL 查询"""
        return self.client._call("/api/query/sql", {"stmt": sql})
    
    def search_content(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索内容"""
        return self.execute(f"SELECT * FROM blocks WHERE content LIKE '%{keyword}%' LIMIT {limit}")
    
    def search_by_type(self, block_type: str, sub_type: Optional[str] = None, 
                       limit: int = 20) -> List[Dict[str, Any]]:
        """按类型搜索"""
        if sub_type:
            sql = f"SELECT * FROM blocks WHERE type='{block_type}' AND subtype='{sub_type}' LIMIT {limit}"
        else:
            sql = f"SELECT * FROM blocks WHERE type='{block_type}' LIMIT {limit}"
        return self.execute(sql)
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近更新的块"""
        return self.execute(f"SELECT * FROM blocks ORDER BY updated DESC LIMIT {limit}")
    
    def count_by_type(self, block_type: str) -> int:
        """统计某类型块的数量"""
        result = self.execute(f"SELECT COUNT(*) as count FROM blocks WHERE type='{block_type}'")
        return result[0].get('count', 0) if result else 0


class FileManager:
    """文件管理"""
    
    def __init__(self, client):
        self.client = client
    
    def get(self, path: str) -> bytes:
        """获取文件内容"""
        # 注意：getFile 返回的是原始文件内容，不是 JSON
        url = f"{self.client.api_url}/api/file/getFile"
        payload = json.dumps({"path": path}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers=self.client.headers, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            raise SiYuanAPIError(f"获取文件失败：{e.code} {e.reason}")
    
    def remove(self, path: str, confirm: bool = True) -> None:
        """
        删除文件（需要二次确认）
        
        Args:
            path: 文件路径
            confirm: 是否需要确认，默认 True
        """
        # 检查全局删除开关
        if not self.client.allow_delete:
            raise SiYuanAPIError("删除操作已被禁用，需要在客户端中设置 allow_delete=True")
        
        # 使用全局配置或显式覆盖
        confirm = confirm if confirm is not None else self.client.require_delete_confirm
        
        if confirm:
            if not confirm_delete("文件", path, f"路径：{path}"):
                raise DeleteConfirmationError(f"用户取消删除文件 {path}")
        self.client._call("/api/file/removeFile", {"path": path})
    
    def rename(self, path: str, new_path: str) -> None:
        """重命名文件"""
        self.client._call("/api/file/renameFile", {"path": path, "newPath": new_path})
    
    def list_dir(self, path: str) -> List[Dict[str, Any]]:
        """列出目录内容"""
        return self.client._call("/api/file/readDir", {"path": path})


class TemplateManager:
    """模板管理"""
    
    def __init__(self, client):
        self.client = client
    
    def render_sprig(self, template: str) -> str:
        """渲染 Sprig 模板"""
        return self.client._call("/api/template/renderSprig", {"template": template})
    
    def render(self, doc_id: str, template_path: str) -> Dict[str, str]:
        """渲染模板文件"""
        return self.client._call("/api/template/render", {
            "id": doc_id,
            "path": template_path
        })


class NotificationManager:
    """通知管理"""
    
    def __init__(self, client):
        self.client = client
    
    def push(self, msg: str, timeout: int = 7000) -> str:
        """推送消息"""
        result = self.client._call("/api/notification/pushMsg", {
            "msg": msg,
            "timeout": timeout
        })
        return result.get("id", "")
    
    def push_error(self, msg: str, timeout: int = 7000) -> str:
        """推送错误消息"""
        result = self.client._call("/api/notification/pushErrMsg", {
            "msg": msg,
            "timeout": timeout
        })
        return result.get("id", "")


class SiYuanClient:
    """思源笔记 API 客户端"""
    
    def __init__(self, api_url: Optional[str] = None, api_token: Optional[str] = None,
                 require_delete_confirm: bool = True, allow_delete: bool = False):
        """
        初始化客户端
        
        Args:
            api_url: API URL，默认 http://127.0.0.1:6806
            api_token: API Token，从思源笔记「设置 - 关于」获取
            require_delete_confirm: 删除操作是否需要二次确认，默认 True
            allow_delete: 是否允许删除操作，默认 False（需要显式启用）
        """
        self.api_url = api_url or os.getenv("SIYUAN_API_URL", "http://127.0.0.1:6806")
        self.api_token = api_token or os.getenv("SIYUAN_API_TOKEN", "")
        self.require_delete_confirm = require_delete_confirm
        self.allow_delete = allow_delete
        
        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # 管理器（传入安全配置）
        self.notebooks = NotebookManager(self)
        self.documents = DocumentManager(self)
        self.blocks = BlockManager(self)
        self.attrs = AttributeManager(self)
        self.query = QueryManager(self)
        self.files = FileManager(self)
        self.templates = TemplateManager(self)
        self.notifications = NotificationManager(self)
    
    def _call(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """内部 API 调用方法"""
        url = f"{self.api_url}{endpoint}"
        payload = json.dumps(data).encode('utf-8') if data else b'{}'
        
        req = urllib.request.Request(url, data=payload, headers=self.headers, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get("code") != 0:
                    raise SiYuanAPIError(f"API 错误：{result.get('msg')}")
                return result.get("data")
        except urllib.error.HTTPError as e:
            raise SiYuanAPIError(f"HTTP 错误：{e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise SiYuanConnectionError(f"连接错误：{e.reason}\n请确认思源笔记正在运行")
    
    def version(self) -> str:
        """获取思源笔记版本"""
        return self._call("/api/system/version")
    
    def current_time(self) -> int:
        """获取当前时间（毫秒时间戳）"""
        return self._call("/api/system/currentTime")
    
    def boot_progress(self) -> Dict[str, Any]:
        """获取启动进度"""
        return self._call("/api/system/bootProgress")
    
    def ping(self) -> bool:
        """检查连接是否正常"""
        try:
            self.version()
            return True
        except Exception:
            return False


# 便捷函数
def create_client(api_url: Optional[str] = None, api_token: Optional[str] = None) -> SiYuanClient:
    """创建思源笔记客户端"""
    return SiYuanClient(api_url, api_token)


if __name__ == "__main__":
    # 使用示例
    client = SiYuanClient()
    
    # 检查连接
    if client.ping():
        print(f"✅ 连接成功，思源版本：{client.version()}")
    else:
        print("❌ 无法连接到思源笔记，请确认思源正在运行且 API 已启用")
        sys.exit(1)
    
    # 列出笔记本
    print("\n📚 笔记本列表:")
    notebooks = client.notebooks.list()
    for nb in notebooks.get("notebooks", []):
        print(f"  - {nb['name']} (ID: {nb['id']})")
