from typing import Optional, List
from pydantic import BaseModel, Field


class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="消息角色，如 'user', 'assistant', 'system'")
    content: str = Field(..., description="消息内容")


class Choice(BaseModel):
    """选择项模型"""
    index: int = Field(..., description="选择项的索引")
    message: Message = Field(..., description="消息内容")
    finish_reason: Optional[str] = Field(None, alias="finishReason", description="完成原因")


class Usage(BaseModel):
    """使用量统计模型"""
    prompt_tokens: int = Field(..., alias="promptTokens", description="提示词token数量")
    completion_tokens: int = Field(..., alias="completionTokens", description="完成token数量")
    total_tokens: int = Field(..., alias="totalTokens", description="总token数量")


class ChatCompletionResponse(BaseModel):
    """TripNow聊天完成响应模型"""
    id: str = Field(..., description="响应ID")
    object: str = Field(..., description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="使用的模型")
    choices: List[Choice] = Field(..., description="选择项列表")
    usage: Usage = Field(..., description="使用量统计")

    def markdown(self):
        """将响应转换为Markdown格式"""
        result = []
        result.append(f"## TripNow 旅行助手回复\n")
        result.append(f"- **模型**: {self.model}\n")
        result.append(f"- **响应ID**: {self.id}\n")
        
        if self.choices:
            for choice in self.choices:
                result.append(f"\n### 回复内容\n")
                result.append(f"{choice.message.content}\n")
        
        if self.usage:
            result.append(f"\n### Token使用统计\n")
            result.append(f"- **提示词Token**: {self.usage.prompt_tokens}\n")
            result.append(f"- **完成Token**: {self.usage.completion_tokens}\n")
            result.append(f"- **总Token**: {self.usage.total_tokens}\n")
        
        return "".join(result)


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: Optional[str] = Field(None, description="错误信息")
    message: Optional[str] = Field(None, description="错误消息")

    def markdown(self):
        error_msg = self.error or self.message or "未知错误"
        return f"⚠️ **错误**: {error_msg}"
