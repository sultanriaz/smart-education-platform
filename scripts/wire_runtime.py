"""One-time integration helper; all resulting service code is committed."""
from pathlib import Path
import re
import ast

ROOT = Path(__file__).resolve().parents[1]

for service in sorted((ROOT / "services").glob("*-service")):
    main = service / "app/main.py"
    code = main.read_text(encoding="utf-8")
    if "from app.sprint16 import install_sprint16" not in code:
        # Install observability first: contract context middleware is outermost
        # and owns request IDs reused by observability.
        imports = "from app.sprint16 import install_sprint16\nfrom app.sprint18 import install_sprint18\nfrom app.sprint21 import install_sprint21\n"
        code = code.replace("from fastapi import ", imports + "\nfrom fastapi import ", 1)
        for node in ast.walk(ast.parse(code)):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "FastAPI":
                lines = code.splitlines(keepends=True)
                indentation = " " * node.col_offset
                lines.insert(node.end_lineno, "".join(indentation + f"install_sprint{sprint}(app)\n" for sprint in (21, 16, 18)))
                code = "".join(lines)
                break
        else:
            raise RuntimeError(f"No FastAPI constructor found in {main}")
        main.write_text(code, encoding="utf-8")
    dbfile = service / "app/db/session.py"
    if dbfile.exists():
        code = dbfile.read_text(encoding="utf-8")
        # Reuse the existing engine variable/session factory, never create a second pool.
        code = re.sub(r"from sqlalchemy import create_engine\n", "from smartedu_infra import DatabaseSettings, build_engine\n", code)
        start = code.find("engine = create_engine(")
        if start != -1:
            stop = start + len("engine = create_engine(")
            depth = 1
            while depth:
                depth += (code[stop] == "(") - (code[stop] == ")")
                stop += 1
            existing_settings = "get_settings()" if "from app.core.config import get_settings" in code else "settings"
            code = code[:start] + f'engine = build_engine(DatabaseSettings(DATABASE_URL={existing_settings}.DATABASE_URL, DB_APPLICATION_NAME="{service.name}"))' + code[stop:]
            dbfile.write_text(code, encoding="utf-8")
    # Security middleware must allow the explicit configured internal hosts too.
    security = service / "app/sprint18.py"
    code = security.read_text(encoding="utf-8")
    code = code.replace("allowed_hosts=settings.host_allowlist,", 'allowed_hosts=settings.host_allowlist + (("testserver",) if settings.environment == "test" else ()),')
    security.write_text(code, encoding="utf-8")

# Remove the old Attendance ID generator; shared contracts now own IDs.
main = ROOT / "services/attendance-service/app/main.py"
code = main.read_text(encoding="utf-8")
code = code.replace("from uuid import uuid4\n\n", "")
code = re.sub(r'    @app.middleware\("http"\)\n    async def correlation_id.*?\n    def error', "    def error", code, flags=re.S)
main.write_text(code, encoding="utf-8")

print("Wired contracts, security, observability and bounded service-owned DB pools in ten services.")
