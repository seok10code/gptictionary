from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse

from backend.app.core.templates import templates

router = APIRouter()

SETTINGS = {
    "gpt_answer_style": "normal",
    "qdrant_enabled": True,
    "auto_example_enabled": True,
}


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "settings": SETTINGS,
            "message": None,
        },
    )


@router.post("/settings", response_class=HTMLResponse)
def update_settings(
    request: Request,
    gpt_answer_style: str = Form("normal"),
    qdrant_enabled: str = Form(None),
    auto_example_enabled: str = Form(None),
):
    SETTINGS["gpt_answer_style"] = gpt_answer_style
    SETTINGS["qdrant_enabled"] = qdrant_enabled == "on"
    SETTINGS["auto_example_enabled"] = auto_example_enabled == "on"

    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "settings": SETTINGS,
            "message": "설정이 저장되었습니다. 현재는 서버 실행 중에만 유지됩니다.",
        },
    )