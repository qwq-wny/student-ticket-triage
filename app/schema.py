"""Request and response models for the ticket triage API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CustomerTier = Literal["free", "standard", "premium"]


class TicketRequest(BaseModel):
    """提交给模型预测的一条客服工单。"""

    model_config = ConfigDict(extra="forbid", title="工单请求")

    text: str = Field(
        title="工单内容",
        description="客服工单标题或正文，长度必须在 3 到 4000 个字符之间。",
        examples=["Production is down for every customer after the release."],
        min_length=3,
        max_length=4000,
    )
    customer_tier: CustomerTier = Field(
        title="客户等级",
        description="客户合同等级，只能选择 free、standard 或 premium。",
    )
    monthly_revenue: float = Field(
        title="客户月收入",
        description="该客户账户每月产生的收入，必须大于等于 0。",
        ge=0,
        le=1_000_000_000,
    )


class PredictionResponse(BaseModel):
    """模型返回给路由系统的预测结果。"""

    model_config = ConfigDict(extra="forbid", title="工单优先级预测结果")

    priority: Literal["urgent", "high", "normal", "low"] = Field(
        title="预测优先级",
        description="urgent=紧急，high=高，normal=普通，low=低。",
    )
    confidence: float = Field(
        title="预测置信度",
        description="模型对返回优先级的置信程度，范围是 0 到 1。",
        ge=0,
        le=1,
    )
    probabilities: dict[str, float] = Field(
        title="各类别概率",
        description="urgent、high、normal、low 四个类别各自的预测概率。",
    )
    model_version: str = Field(title="模型版本", description="当前使用的模型版本号。")
