#!/usr/bin/env python3
"""
思源笔记删除保护工具
提供安全的删除操作确认和审计日志功能

用法:
    from siyuan_delete_protect import DeleteProtect
    
    protector = DeleteProtect()
    
    # 确认删除
    if protector.confirm("文档", "20240101120000-abc1234", "测试文档"):
        # 执行删除
        client.documents.remove("20240101120000-abc1234")
    
    # 记录删除日志
    protector.log_delete("文档", "20240101120000-abc1234", "测试文档")
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Optional


class DeleteProtect:
    """删除保护器"""
    
    def __init__(self, log_file: Optional[str] = None, require_confirm: bool = True):
        """
        初始化删除保护器
        
        Args:
            log_file: 审计日志文件路径，默认 ~/.hermes/siyuan_delete_log.jsonl
            require_confirm: 是否需要确认
        """
        self.log_file = Path(log_file) if log_file else Path.home() / ".hermes" / "siyuan_delete_log.jsonl"
        self.require_confirm = require_confirm
        
        # 确保日志目录存在
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def confirm(self, resource_type: str, resource_id: str, extra_info: str = "") -> bool:
        """
        删除操作二次确认
        
        Args:
            resource_type: 资源类型（笔记本/文档/块/文件）
            resource_id: 资源 ID
            extra_info: 额外信息（如标题、路径等）
            
        Returns:
            bool: 用户是否确认删除
        """
        if not self.require_confirm:
            return True
        
        print("\n" + "=" * 60, file=sys.stderr)
        print("⚠️  删除操作确认", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(f"资源类型：{resource_type}", file=sys.stderr)
        print(f"资源 ID:  {resource_id}", file=sys.stderr)
        if extra_info:
            print(f"详细信息：{extra_info}", file=sys.stderr)
        print("\n⚠️  此操作不可逆！数据将永久丢失！", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        
        # 第一次确认：输入 yes/no
        first_confirm = input("\n是否确认删除？(yes/no): ").strip().lower()
        if first_confirm not in ('yes', 'y'):
            print("❌ 已取消删除操作", file=sys.stderr)
            return False
        
        # 第二次确认：输入资源 ID
        verify_input = input(f"\n请输入 '{resource_id}' 进行验证：").strip()
        if verify_input == resource_id:
            print("✅ 已确认删除", file=sys.stderr)
            return True
        else:
            print("❌ ID 验证失败，已取消删除操作", file=sys.stderr)
            return False
    
    def log_delete(self, resource_type: str, resource_id: str, 
                   extra_info: str = "", success: bool = True) -> None:
        """
        记录删除操作日志
        
        Args:
            resource_type: 资源类型
            resource_id: 资源 ID
            extra_info: 额外信息
            success: 是否成功
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "resource_type": resource_type,
            "resource_id": resource_id,
            "extra_info": extra_info,
            "success": success
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_delete_history(self, limit: int = 20) -> list:
        """
        获取删除历史
        
        Args:
            limit: 返回记录数量
            
        Returns:
            删除历史记录列表
        """
        if not self.log_file.exists():
            return []
        
        history = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line))
        
        # 返回最新的记录
        return history[-limit:][::-1]
    
    def print_history(self, limit: int = 20) -> None:
        """打印删除历史"""
        history = self.get_delete_history(limit)
        
        if not history:
            print("暂无删除记录")
            return
        
        print("\n📋 删除历史记录")
        print("=" * 70)
        
        for entry in history:
            status = "✅" if entry.get("success") else "❌"
            print(f"{status} {entry['timestamp'][:19]} | {entry['resource_type']} | {entry['resource_id']}")
            if entry.get('extra_info'):
                print(f"   └─ {entry['extra_info']}")
        
        print("=" * 70)
        print(f"共 {len(history)} 条记录")


# 便捷函数
def safe_delete(client, resource_type: str, resource_id: str, 
                extra_info: str = "", log: bool = True) -> bool:
    """
    安全删除函数（带确认和日志）
    
    Args:
        client: SiYuanClient 实例
        resource_type: 资源类型
        resource_id: 资源 ID
        extra_info: 额外信息
        log: 是否记录日志
        
    Returns:
        是否删除成功
    """
    protector = DeleteProtect()
    
    if not protector.confirm(resource_type, resource_id, extra_info):
        if log:
            protector.log_delete(resource_type, resource_id, extra_info, success=False)
        return False
    
    try:
        # 根据类型执行删除
        if resource_type == "笔记本":
            client.notebooks.remove(notebook_id=resource_id, confirm=False)
        elif resource_type == "文档":
            client.documents.remove(doc_id=resource_id, confirm=False)
        elif resource_type == "块":
            client.blocks.delete(block_id=resource_id, confirm=False)
        elif resource_type == "文件":
            client.files.remove(path=resource_id, confirm=False)
        else:
            raise ValueError(f"未知资源类型：{resource_type}")
        
        if log:
            protector.log_delete(resource_type, resource_id, extra_info, success=True)
        
        print(f"✅ 已成功删除 {resource_type}: {resource_id}")
        return True
        
    except Exception as e:
        if log:
            protector.log_delete(resource_type, resource_id, extra_info, success=False)
        print(f"❌ 删除失败：{e}")
        return False


if __name__ == "__main__":
    # 命令行查看删除历史
    if len(sys.argv) > 1 and sys.argv[1] == "history":
        protector = DeleteProtect()
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        protector.print_history(limit)
    else:
        print(__doc__)
