"""FastAPI entrypoint for ticket priority inference."""

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.docs_page import chinese_swagger_page
from app.model import DEFAULT_MODEL_PATH, ModelService, ModelUnavailableError
from app.schema import PredictionResponse, TicketRequest

model_service = ModelService(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))

app = FastAPI(
    title="客服工单优先级分类 API",
    version="1.0.0",
    description="输入客服工单内容、客户等级和月收入，模型会返回 urgent、high、normal 或 low 四种优先级。",
    docs_url=None,
)


@app.get("/docs", include_in_schema=False)
def docs() -> HTMLResponse:
    """中文接口文档页面。"""
    return chinese_swagger_page()


@app.get("/", summary="首页", description="用于确认 API 服务已经启动。")
def home() -> dict[str, str]:
    """返回服务状态。"""
    return {"status": "ok"}


@app.get(
    "/health",
    summary="健康检查",
    description="检查 API 服务是否正常，以及机器学习模型是否成功加载。",
)
def health() -> dict[str, Any]:
    """返回服务和模型状态。"""
    try:
        version = model_service.bundle["metadata"]["version"]
    except ModelUnavailableError:
        return {"status": "error", "model_loaded": False}

    return {"status": "ok", "model_loaded": True, "model_version": version}


@app.post(
    "/triage",
    summary="预测工单优先级",
    description="提交一条客服工单，模型返回 urgent、high、normal 或 low。点击“试一试”，修改请求示例，然后点击“执行”查看结果。",
    response_model=PredictionResponse,
    responses={200: {"description": "预测成功"}, 422: {"description": "请求参数不合法"}},
)
def triage(ticket: TicketRequest) -> dict[str, Any]:
    """预测并返回工单优先级。"""
    try:
        return model_service.predict(ticket)
    except ModelUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
