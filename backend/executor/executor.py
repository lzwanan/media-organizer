"""执行引擎 — 文件重命名/移动操作"""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ExecutionItem:
    """单个执行项"""
    path: str               # 原文件绝对路径
    target_dir: str         # 目标目录（相对于 root）
    target_name: str        # 目标文件名


@dataclass 
class ExecutionResult:
    """执行结果"""
    total: int
    success: int
    failed: int
    skipped: int
    dry_run: bool
    items: list[dict]       # [{path, target, status, error?}]


def execute(
    items: list[ExecutionItem],
    root_path: str,
    *,
    dry_run: bool = True,
    conflict_strategy: str = "skip",
) -> ExecutionResult:
    """
    执行文件整理

    Args:
        items: 要处理的文件列表
        root_path: 整理根目录（目标目录的父级）
        dry_run: True=仅预览不写盘
        conflict_strategy: skip / overwrite / rename

    Returns:
        ExecutionResult
    """
    result_items: list[dict] = []
    success = 0
    failed = 0
    skipped = 0

    for item in items:
        src = Path(item.path)
        if not src.exists() or not src.is_file():
            result_items.append({
                "path": item.path,
                "target": item.target_name,
                "status": "skipped",
                "error": "Source file not found",
            })
            skipped += 1
            continue

        # 构建目标路径
        target_full_dir = Path(root_path) / item.target_dir
        target_full = target_full_dir / item.target_name

        if dry_run:
            result_items.append({
                "path": str(src),
                "target": str(target_full),
                "status": "preview",
            })
            success += 1
            continue

        # 实际执行
        try:
            # 创建目标目录
            target_full_dir.mkdir(parents=True, exist_ok=True)

            # 冲突处理
            if target_full.exists():
                if conflict_strategy == "skip":
                    result_items.append({
                        "path": str(src),
                        "target": str(target_full),
                        "status": "skipped",
                        "error": "Target already exists",
                    })
                    skipped += 1
                    continue
                elif conflict_strategy == "rename":
                    # 自动编号
                    stem = target_full.stem
                    suffix = target_full.suffix
                    counter = 1
                    while True:
                        alt = target_full_dir / f"{stem}_{counter}{suffix}"
                        if not alt.exists():
                            target_full = alt
                            break
                        counter += 1
                elif conflict_strategy == "overwrite":
                    target_full.unlink()

            # 移动/重命名
            shutil.move(str(src), str(target_full))
            result_items.append({
                "path": str(src),
                "target": str(target_full),
                "status": "success",
            })
            success += 1

        except PermissionError as e:
            result_items.append({
                "path": str(src),
                "target": str(target_full),
                "status": "failed",
                "error": f"Permission denied: {e}",
            })
            failed += 1
        except OSError as e:
            result_items.append({
                "path": str(src),
                "target": str(target_full),
                "status": "failed",
                "error": str(e),
            })
            failed += 1

    return ExecutionResult(
        total=len(items),
        success=success,
        failed=failed,
        skipped=skipped,
        dry_run=dry_run,
        items=result_items,
    )
