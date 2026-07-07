import os

WORKSPACE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "workspace")
os.makedirs(WORKSPACE, exist_ok=True)


def safe_path(path: str) -> str:
    """将路径限制在 workspace 内，防止目录穿越。"""
    full = os.path.normpath(os.path.join(WORKSPACE, path))
    if not full.startswith(os.path.normpath(WORKSPACE)):
        raise ValueError("不允许访问 workspace 外的路径")
    return full


def list_workspace_files() -> list[str]:
    result = []
    for root, _, files in os.walk(WORKSPACE):
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), WORKSPACE)
            result.append(rel.replace("\\", "/"))
    return result if result else ["（workspace 为空）"]


def search_workspace_file(filename: str) -> str | None:
    target = filename.lower()
    for root, _, files in os.walk(WORKSPACE):
        for file in files:
            if target in file.lower():
                return os.path.relpath(os.path.join(root, file), WORKSPACE).replace("\\", "/")
    return None


def read_workspace_file(path: str) -> str:
    full = safe_path(path)
    if not os.path.isfile(full):
        return f"文件不存在: {path}"
    with open(full, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    if len(content) > 8000:
        return content[:8000] + f"\n\n... (已截断，共 {len(content)} 字符)"
    return content


def write_workspace_file(path: str, text: str) -> str:
    full = safe_path(path)
    os.makedirs(os.path.dirname(full) or WORKSPACE, exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)
    return f"已写入 {path}"
