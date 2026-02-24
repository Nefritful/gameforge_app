import json
from pathlib import Path
from typing import Any, Dict

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .db import db_all, db_one, db_exec
from .auth import verify_login, register_user

def _session_user(request) -> Dict[str, Any] | None:
    uid = request.session.get("user_id")
    email = request.session.get("user_email")
    if uid and email:
        return {"id": uid, "email": email}
    return None

def _require_login(request):
    if not _session_user(request):
        return redirect("home")
    return None

def _ensure_storage_user_dir(email: str) -> Path:
    root = Path(settings.USER_PROJECTS_ROOT)
    p = root / email
    p.mkdir(parents=True, exist_ok=True)
    return p

def home(request):
    user = _session_user(request)
    return render(request, "pages/home.html", {"user": user})

def projects(request):
    guard = _require_login(request)
    if guard: return guard
    user = _session_user(request)

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        desc = (request.POST.get("description") or "").strip()
        if not name:
            return redirect("projects")
        pid = db_exec(
            "INSERT INTO gf_projects(user_id, name, description) VALUES (%s,%s,%s)",
            (user["id"], name, desc or None)
        )
        # базовые файлы проекта
        db_exec(
            "INSERT INTO gf_project_files(project_id, file_key, content) VALUES (%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE content=VALUES(content)",
            (pid, "project_json", json.dumps({
                "format_version": 1,
                "title": name,
                "window": {"width": 1280, "height": 720},
                "plugins": [],
                "assets": {"textures": {}},
                "start_scene": "level1"
            }, ensure_ascii=False, indent=2))
        )
        db_exec(
            "INSERT INTO gf_project_files(project_id, file_key, content) VALUES (%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE content=VALUES(content)",
            (pid, "scene:level1", json.dumps({
                "scene_id": "level1",
                "entities": []
            }, ensure_ascii=False, indent=2))
        )

        # storage
        user_dir = _ensure_storage_user_dir(user["email"])
        proj_dir = user_dir / name
        proj_dir.mkdir(parents=True, exist_ok=True)
        (proj_dir / "project.json").write_text(db_one(
            "SELECT content FROM gf_project_files WHERE project_id=%s AND file_key='project_json'", (pid,)
        )["content"], encoding="utf-8")

        return redirect("project_editor", project_id=pid)

    projects = db_all(
        "SELECT id, name, description, created_at FROM gf_projects WHERE user_id=%s ORDER BY created_at DESC",
        (user["id"],)
    )
    return render(request, "pages/projects.html", {"user": user, "projects": projects})

def project_editor(request, project_id: int):
    guard = _require_login(request)
    if guard: return guard
    user = _session_user(request)

    proj = db_one(
        "SELECT id, user_id, name, description FROM gf_projects WHERE id=%s", (project_id,)
    )
    if not proj or proj["user_id"] != user["id"]:
        return redirect("projects")

    # список сцен (keys scene:xxx)
    scenes = db_all(
        "SELECT file_key FROM gf_project_files WHERE project_id=%s AND file_key LIKE 'scene:%%' ORDER BY file_key",
        (project_id,)
    )
    scenes = [r["file_key"].split("scene:", 1)[1] for r in scenes]

    return render(request, "pages/project_editor.html", {
        "user": user,
        "project": proj,
        "scenes": scenes,
    })

@csrf_exempt
def login_post(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = request.POST
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""
    user = verify_login(email, password)
    if not user:
        return JsonResponse({"ok": False, "error": "Неверный email или пароль"}, status=401)
    request.session["user_id"] = user["id"]
    request.session["user_email"] = user["email"]
    return JsonResponse({"ok": True})

@csrf_exempt
def register_post(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = request.POST
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""
    if not email or not password:
        return JsonResponse({"ok": False, "error": "Заполни email и пароль"}, status=400)
    try:
        user = register_user(email, password)
    except Exception as e:
        return JsonResponse({"ok": False, "error": "Такой email уже зарегистрирован"}, status=400)

    request.session["user_id"] = user["id"]
    request.session["user_email"] = user["email"]
    _ensure_storage_user_dir(email)
    return JsonResponse({"ok": True})

def logout_get(request):
    request.session.flush()
    return redirect("home")

# ---------------- API ----------------

def _require_project_owner(request, project_id: int):
    user = _session_user(request)
    if not user:
        return None, JsonResponse({"ok": False, "error": "unauthorized"}, status=401)
    proj = db_one("SELECT id, user_id, name FROM gf_projects WHERE id=%s", (project_id,))
    if not proj or proj["user_id"] != user["id"]:
        return None, JsonResponse({"ok": False, "error": "forbidden"}, status=403)
    return proj, None

def api_file_get(request, project_id: int):
    proj, err = _require_project_owner(request, project_id)
    if err: return err
    key = (request.GET.get("key") or "").strip()
    if not key:
        return JsonResponse({"ok": False, "error": "key required"}, status=400)
    row = db_one("SELECT content, updated_at FROM gf_project_files WHERE project_id=%s AND file_key=%s", (project_id, key))
    if not row:
        return JsonResponse({"ok": False, "error": "not found"}, status=404)
    return JsonResponse({"ok": True, "key": key, "content": row["content"], "updated_at": str(row["updated_at"])})

@csrf_exempt
def api_file_save(request, project_id: int):
    proj, err = _require_project_owner(request, project_id)
    if err: return err
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST only"}, status=405)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid json"}, status=400)
    key = (payload.get("key") or "").strip()
    content = payload.get("content")
    if not key or content is None:
        return JsonResponse({"ok": False, "error": "key/content required"}, status=400)

    if isinstance(content, (dict, list)):
        content_str = json.dumps(content, ensure_ascii=False, indent=2)
    else:
        content_str = str(content)

    db_exec(
        "INSERT INTO gf_project_files(project_id, file_key, content) VALUES (%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE content=VALUES(content)",
        (project_id, key, content_str)
    )

    # зеркалим в storage (минимум: project_json и scene:*)
    user = _session_user(request)
    user_dir = _ensure_storage_user_dir(user["email"])
    proj_dir = user_dir / proj["name"]
    proj_dir.mkdir(parents=True, exist_ok=True)
    if key == "project_json":
        (proj_dir / "project.json").write_text(content_str, encoding="utf-8")
    elif key.startswith("scene:"):
        scene_id = key.split("scene:", 1)[1]
        (proj_dir / f"scene_{scene_id}.json").write_text(content_str, encoding="utf-8")

    return JsonResponse({"ok": True})

def api_scenes_list(request, project_id: int):
    proj, err = _require_project_owner(request, project_id)
    if err: return err
    rows = db_all(
        "SELECT file_key, updated_at FROM gf_project_files WHERE project_id=%s AND file_key LIKE 'scene:%%' ORDER BY file_key",
        (project_id,)
    )
    scenes = [{"scene_id": r["file_key"].split("scene:", 1)[1], "file_key": r["file_key"], "updated_at": str(r["updated_at"])} for r in rows]
    return JsonResponse({"ok": True, "scenes": scenes})

@csrf_exempt
def api_scenes_create(request, project_id: int):
    proj, err = _require_project_owner(request, project_id)
    if err: return err
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST only"}, status=405)
    payload = json.loads(request.body.decode("utf-8"))
    scene_id = (payload.get("scene_id") or "").strip()
    if not scene_id:
        return JsonResponse({"ok": False, "error": "scene_id required"}, status=400)

    key = f"scene:{scene_id}"
    # если уже есть — ошибка
    exists = db_one("SELECT id FROM gf_project_files WHERE project_id=%s AND file_key=%s", (project_id, key))
    if exists:
        return JsonResponse({"ok": False, "error": "scene exists"}, status=400)

    db_exec(
        "INSERT INTO gf_project_files(project_id, file_key, content) VALUES (%s,%s,%s)",
        (project_id, key, json.dumps({"scene_id": scene_id, "entities": []}, ensure_ascii=False, indent=2))
    )
    return JsonResponse({"ok": True, "scene_id": scene_id})
