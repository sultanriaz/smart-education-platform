from __future__ import annotations

import ast
import sys
from pathlib import Path

IMPORT_LINE = "from app.sprint21 import install_sprint21\n"
CALL_LINE = "install_sprint21(app)\n"


def patch_main(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    if "install_sprint21(app)" in source:
        return False

    tree = ast.parse(source)
    app_assign = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "app"
            for target in node.targets
        ):
            continue
        value = node.value
        if not isinstance(value, ast.Call):
            continue
        func = value.func
        name = (
            func.id
            if isinstance(func, ast.Name)
            else func.attr
            if isinstance(func, ast.Attribute)
            else None
        )
        if name == "FastAPI":
            app_assign = node
            break

    if app_assign is None or app_assign.end_lineno is None:
        raise RuntimeError(f"Could not locate app = FastAPI(...) in {path}")

    lines = source.splitlines(keepends=True)

    import_index = 0
    if lines and lines[0].startswith("from __future__ import"):
        import_index = 1
        while import_index < len(lines) and not lines[import_index].strip():
            import_index += 1
    lines.insert(import_index, IMPORT_LINE)

    # Insert after FastAPI creation. The imported line shifts original positions by one.
    call_index = app_assign.end_lineno + 1
    lines.insert(call_index, "\n" + CALL_LINE)

    path.write_text("".join(lines), encoding="utf-8")
    return True


def main() -> None:
    repo_root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    services_root = repo_root / "services"

    changed: list[str] = []
    skipped: list[str] = []

    for service_dir in sorted(services_root.glob("*-service")):
        main_path = service_dir / "app" / "main.py"
        bridge = service_dir / "app" / "sprint21.py"
        if not main_path.exists() or not bridge.exists():
            skipped.append(service_dir.name)
            continue
        if patch_main(main_path):
            changed.append(service_dir.name)

    print("Sprint 21 wiring:")
    print("  changed:", ", ".join(changed) if changed else "none")
    print("  skipped:", ", ".join(skipped) if skipped else "none")


if __name__ == "__main__":
    main()
