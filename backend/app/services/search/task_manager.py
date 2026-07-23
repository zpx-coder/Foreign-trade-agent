"""后台搜索任务管理器 — 内存存储，不持久化"""

import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# 任务自动清理时间（超过此时间的已完成/失败任务将被清除）
_TASK_TTL_HOURS = 2
# 轮询时最多返回的任务数
_MAX_TASKS_PER_TENANT = 20


class SearchTaskManager:
    """内存中的搜索任务管理器（单例）"""

    _tasks: Dict[str, dict] = {}
    _lock: asyncio.Lock = None

    @classmethod
    def _get_lock(cls) -> asyncio.Lock:
        if cls._lock is None:
            cls._lock = asyncio.Lock()
        return cls._lock

    @classmethod
    async def create(
        cls,
        tenant_id: str,
        icp_name: str,
        channels: List[str],
        region: Optional[str] = None,
    ) -> str:
        """创建新任务，返回 task_id"""
        task_id = uuid.uuid4().hex[:12]
        now = datetime.now(timezone.utc).isoformat()
        task = {
            "task_id": task_id,
            "tenant_id": tenant_id,
            "icp_name": icp_name,
            "channels": channels,
            "region": region,
            "status": "pending",
            "current_section": None,
            "progress_message": "等待执行...",
            "result": {
                "saved_count": 0,
                "enriched_count": 0,
                "contact_search_count": 0,
                "inferred_count": 0,
                "total_found": 0,
            },
            "error": None,
            "created_at": now,
            "updated_at": now,
        }
        lock = cls._get_lock()
        async with lock:
            cls._tasks[task_id] = task
            # 清理过期任务
            cls._cleanup_expired()
        return task_id

    @classmethod
    async def get(cls, task_id: str) -> Optional[dict]:
        """获取单个任务"""
        lock = cls._get_lock()
        async with lock:
            return cls._tasks.get(task_id)

    @classmethod
    async def list_by_tenant(cls, tenant_id: str) -> list:
        """获取租户的最近任务列表"""
        lock = cls._get_lock()
        async with lock:
            cls._cleanup_expired()
            tenant_tasks = [
                t for t in cls._tasks.values()
                if t["tenant_id"] == tenant_id
            ]
            # 按创建时间倒序
            tenant_tasks.sort(key=lambda t: t["created_at"], reverse=True)
            return tenant_tasks[:_MAX_TASKS_PER_TENANT]

    @classmethod
    async def update(cls, task_id: str, **kwargs):
        """更新任务字段"""
        lock = cls._get_lock()
        async with lock:
            task = cls._tasks.get(task_id)
            if task:
                task.update(kwargs)
                task["updated_at"] = datetime.now(timezone.utc).isoformat()

    @classmethod
    async def remove(cls, task_id: str):
        """移除任务"""
        lock = cls._get_lock()
        async with lock:
            cls._tasks.pop(task_id, None)

    @classmethod
    def _cleanup_expired(cls):
        """清理过期任务（需在锁内调用）"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=_TASK_TTL_HOURS)
        expired = []
        for tid, task in cls._tasks.items():
            if task["status"] in ("completed", "failed"):
                try:
                    updated = datetime.fromisoformat(task["updated_at"])
                    if updated < cutoff:
                        expired.append(tid)
                except (ValueError, KeyError):
                    pass
        for tid in expired:
            del cls._tasks[tid]


# 全局单例
search_task_manager = SearchTaskManager()
