import json
import os
from typing import Type, Any, List

import httpx
import uvicorn
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import CallToolResult, TextContent
from pydantic import Field
from starlette.routing import Host

from models import ChatCompletionResponse, ErrorResponse, Message

# 创建MCP服务器实例
mcp = FastMCP(
    name="tripnow_mcp",
    instructions="MCP Server 航班管家 - 一站式航铁票务查询 实时动态智能追踪。覆盖机票、火车票实时查询，航铁动态精准追踪，内置铁路航空领域知识库，解答出行高频问题，为MCP广场用户提供一站式出行信息服务。",
    stateless_http=True,
    port=8000,
    host="0.0.0.0"
)

"""
获取环境变量/Header中的API密钥, 用于调用TripNow API
变量名为: TRIPNOW_API_KEY
"""
tripnow_api_url = "https://tripnowengine.133.cn/tripnow/v1/chat/completions"


@mcp.tool(
    name="chat_completions", 
    description="调用TripNow旅行助手API，提供航铁票务实时查询、航铁动态精准追踪、航铁知识智能问答三大功能。支持机票、火车票实时查询，列车、航班动态追踪，以及铁路航空领域知识问答。"
)
async def chat_completions(ctx: Context,
                          messages: List[dict] = Field(description="消息列表，每个消息包含role和content字段。支持三种主要功能：1) 航铁票务实时查询（例如：'帮我查询明天北京到上海的火车票'）；2) 航铁动态精准追踪（例如：'帮我看看G123次列车现在到哪了'）；3) 航铁知识智能问答（例如：'学生票每年能买几次，要什么证件核验'）。"),) -> CallToolResult:
    """
    调用TripNow旅行助手API，提供以下三大功能：
    
    1. 航铁票务实时查询：支持机票、火车票实时查询，根据出发地、目的地、出行日期，快速返回对应航班/车次核心信息
    2. 航铁动态精准追踪：支持列车、航班动态实时查询，返回列车位置、检票口等信息及航班起降、登机口等状态
    3. 航铁知识智能问答：内置铁路、航空领域知识库，针对票务政策、退改签、行李规定等高频问题，快速给出精准、规范的解答
    
    Args:
        messages: 消息列表，支持多轮对话。每个消息应包含：
            - role: 消息角色，如 'user', 'assistant'
            - content: 消息内容（自然语言查询）
    """
    tripnow_api_key = get_api_key(ctx)
    # response_format = get_response_format(ctx)

    # 验证并转换消息格式
    formatted_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            formatted_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        elif isinstance(msg, Message):
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        else:
            # 兼容旧格式：如果传入的是字符串，转换为用户消息
            formatted_messages.append({
                "role": "user",
                "content": str(msg)
            })

    # 构建请求体
    payload = {
        "model": "tripnow-travel-pro",
        "messages": formatted_messages,
        "stream": False
    }

    # 构建请求头
    headers = {
        "Authorization": f"Bearer {tripnow_api_key}",
        "Content-Type": "application/json"
    }

    # 发送POST请求
    response = await http_post(tripnow_api_url, headers=headers, json_data=payload)
    return handle_json_response(response, response_format="text", model_class=ChatCompletionResponse)


def get_api_key(ctx: Context) -> str:
    """
    从header或环境变量中获取TripNow的API Key
    """
    # 优先从环境变量获取
    tripnow_api_key = os.getenv("tripnow_api_key", None)
    
    # 如果环境变量不存在，尝试从 headers 获取
    if not tripnow_api_key:
        # ========== 调试信息：打印 Context 的详细信息 ==========
        print("=" * 80)
        print("DEBUG: 开始调试 Context 结构")
        print("=" * 80)
        
        # 打印 Context 对象的所有属性
        print(f"\n[1] Context 类型: {type(ctx)}")
        print(f"[2] Context 的所有属性: {dir(ctx)}")
        
        # 尝试访问各种可能的属性
        ctx_attrs_to_check = [
            'request', 'request_context', 'headers', 
            'http_request', 'http_headers', 'metadata',
            'session', 'state', 'extra'
        ]
        
        for attr_name in ctx_attrs_to_check:
            attr_value = getattr(ctx, attr_name, None)
            if attr_value is not None:
                print(f"[3] ctx.{attr_name} 存在，类型: {type(attr_value)}")
                if hasattr(attr_value, '__dict__'):
                    print(f"    {attr_name} 的属性: {dir(attr_value)}")
        
        # 尝试多种方式获取 headers
        headers = None
        headers_source = None
        
        try:
            # 方式1: 从 ctx.request_context.request.headers 获取
            print("\n[4] 尝试方式1: ctx.request_context.request.headers")
            request_context = getattr(ctx, 'request_context', None)
            if request_context:
                print(f"    request_context 存在，类型: {type(request_context)}")
                print(f"    request_context 属性: {dir(request_context)}")
                request = getattr(request_context, 'request', None)
                if request:
                    print(f"    request 存在，类型: {type(request)}")
                    print(f"    request 属性: {dir(request)}")
                    headers = getattr(request, 'headers', None)
                    if headers:
                        headers_source = "ctx.request_context.request.headers"
                        print(f"    ✓ 成功获取 headers，类型: {type(headers)}")
            
            # 方式2: 如果方式1失败，尝试从 ctx.request.headers 获取
            if not headers:
                print("\n[5] 尝试方式2: ctx.request.headers")
                request = getattr(ctx, 'request', None)
                if request:
                    print(f"    request 存在，类型: {type(request)}")
                    print(f"    request 属性: {dir(request)}")
                    headers = getattr(request, 'headers', None)
                    if headers:
                        headers_source = "ctx.request.headers"
                        print(f"    ✓ 成功获取 headers，类型: {type(headers)}")
            
            # 方式3: 如果方式2也失败，尝试直接访问 ctx.headers
            if not headers:
                print("\n[6] 尝试方式3: ctx.headers")
                headers = getattr(ctx, 'headers', None)
                if headers:
                    headers_source = "ctx.headers"
                    print(f"    ✓ 成功获取 headers，类型: {type(headers)}")
            
            # 打印 headers 的详细信息
            if headers:
                print(f"\n[7] Headers 详细信息 (来源: {headers_source}):")
                print(f"    Headers 类型: {type(headers)}")
                print(f"    Headers 属性/方法: {dir(headers)}")
                
                # 尝试不同的方式访问 headers 内容
                if hasattr(headers, 'items'):
                    print(f"    Headers 内容 (通过 items()):")
                    try:
                        for key, value in headers.items():
                            print(f"      {key}: {value}")
                    except Exception as e:
                        print(f"      无法遍历 items(): {e}")
                
                if hasattr(headers, 'keys'):
                    print(f"    Headers 键 (通过 keys()):")
                    try:
                        for key in headers.keys():
                            print(f"      {key}")
                    except Exception as e:
                        print(f"      无法遍历 keys(): {e}")
                
                if isinstance(headers, dict):
                    print(f"    Headers 内容 (字典访问):")
                    for key, value in headers.items():
                        print(f"      {key}: {value}")
                
                # 尝试获取所有可能的 API Key header 名称
                print(f"\n[8] 尝试获取 API Key (从 {headers_source}):")
                api_key_candidates = [
                    "TRIPNOW_API_KEY", "tripnow-api-key", "tripnow_api_key", 
                    "TRIPNOW-API-KEY", "TripNow-Api-Key", "tripnowapikey"
                ]
                
                for key_name in api_key_candidates:
                    value = None
                    # 尝试字典访问
                    if isinstance(headers, dict):
                        value = headers.get(key_name)
                    # 尝试 get 方法
                    elif hasattr(headers, 'get'):
                        value = headers.get(key_name)
                    # 尝试属性访问
                    else:
                        value = getattr(headers, key_name, None)
                    
                    if value:
                        print(f"    ✓ 找到 {key_name}: {value[:20]}..." if len(str(value)) > 20 else f"    ✓ 找到 {key_name}: {value}")
                        tripnow_api_key = value
                        break
                    else:
                        print(f"    ✗ 未找到 {key_name}")
                
                # 如果还没找到，打印所有 header 键，方便用户查看
                if not tripnow_api_key:
                    print(f"\n[9] 所有可用的 Header 键:")
                    if isinstance(headers, dict):
                        for key in headers.keys():
                            print(f"      - {key}")
                    elif hasattr(headers, 'keys'):
                        for key in headers.keys():
                            print(f"      - {key}")
                    else:
                        print(f"      无法列出所有键")
            else:
                print("\n[7] ✗ 未能获取到 headers")
                
        except Exception as e:
            print(f"\n[ERROR] 访问 headers 时出错: {type(e).__name__}: {e}")
            import traceback
            print(f"        详细错误信息:\n{traceback.format_exc()}")
        
        print("\n" + "=" * 80)
        print(f"DEBUG: 最终结果 - tripnow_api_key = {'已设置' if tripnow_api_key else '未设置'}")
        print("=" * 80 + "\n")
    
    if not tripnow_api_key:
        raise Exception('error: TRIPNOW_API_KEY not set')
    return tripnow_api_key


def get_response_format(ctx: Context) -> str:
    """
    从header中获取数据返回格式类型
    """
    # 安全地获取 headers
    response_format = None
    try:
        request_context = getattr(ctx, 'request_context', None)
        if request_context:
            request = getattr(request_context, 'request', None)
            if request:
                headers = getattr(request, 'headers', None)
                if headers:
                    response_format = (headers.get("responseFormat")
                                      or headers.get("ResponseFormat")
                                      or headers.get("response_format"))
    except Exception:
        # 如果访问 request_context 出错，使用默认值
        pass
    
    if not response_format:
        return 'markdown'
    return response_format


async def http_post(url: str,
                   headers: dict,
                   json_data: dict) -> str:
    """
    发送HTTP POST请求
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=json_data, timeout=30.0)
            # 如果状态码不是 2xx，尝试获取错误详情
            if not response.is_success:
                error_detail = f"Status {response.status_code}"
                try:
                    error_body = response.text
                    if error_body:
                        error_detail += f": {error_body[:500]}"  # 限制错误信息长度
                except:
                    pass
                raise httpx.HTTPStatusError(
                    message=f"HTTP {response.status_code} {error_detail}",
                    request=response.request,
                    response=response
                )
            return response.text
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP request failed: {e.response.status_code} {e.response.reason_phrase}"
        try:
            error_body = e.response.text
            if error_body:
                error_msg += f"\n响应内容: {error_body[:500]}"
        except:
            pass
        raise Exception(error_msg) from e
    except httpx.HTTPError as e:
        raise Exception(f"HTTP request failed: {str(e)}") from e
    except KeyError as e:
        raise Exception(f"Failed to parse response: {str(e)}") from e


def handle_json_response(
        response: str,
        response_format: str,
        model_class: Type[Any], ) -> CallToolResult:
    """
    通用 JSON 响应处理器，用于：
    - 解析 JSON 字符串
    - 实例化 Pydantic 模型
    - 调用 .markdown() 方法生成 Markdown
    - 返回标准化的 CallToolResult

    :param response: 原始 API 返回的字符串（JSON 格式）
    :param response_format: 响应格式，可选 "json" 或 "markdown"
    :param model_class: Pydantic 模型类，如 ChatCompletionResponse
    :return: CallToolResult
    """
    if response_format == "json":
        json_response = json.loads(response)
        # 实例化模型
        try:
            vo_instance = model_class(**json_response)
        except Exception as e:
            vo_instance = ErrorResponse(**json_response)
        # 生成 Markdown（要求模型有 .markdown() 方法）
        markdown_text = vo_instance.markdown()
        return CallToolResult(
            content=[TextContent(type="text", text=markdown_text)],
            structuredContent=json_response,
            isError=False,
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=response)],
            isError=False,
        )


if __name__ == "__main__":
    # Streamable HTTP 模式
    mcp.run(transport="streamable-http")
    # STDIO 模式（标准输入输出）
    # mcp.run()
