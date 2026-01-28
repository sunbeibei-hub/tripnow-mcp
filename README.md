# MCP Server 航班管家

<img src="./image/航班管家LOGO（图形商标）.png" alt="产品Logo" width="200">

**版本**: v1

## 产品描述

**短描述（20字）**: 一站式航铁票务查询 实时动态智能追踪

**长描述（50-100字）**: 覆盖机票、火车票实时查询，航铁动态精准追踪，内置铁路航空领域知识库，解答出行高频问题，为MCP广场用户提供一站式出行信息服务

**分类**: 出行服务

**标签**: 票务查询，实时动态，航铁问答，出行资讯

## 功能特性

本 MCP Server 产品提供以下 Tools(工具/能力):

### Tool1: 航铁票务实时查询

#### 详细描述
支持机票、火车票实时查询，根据出发地、目的地、出行日期，快速返回对应航班/车次核心信息，高效满足出行票务查询需求

#### 调试所需的输入参数
**输入**:
- 出发地（字符串）：出行的起始地点
- 目的地（字符串）：出行的目的地
- 出行日期（字符串）：计划出行的具体日期
- 票务类型（字符串）：机票/火车票

**输出**:
- 对应航班/车次的实时信息，含编号、出发到达时间、坐席/舱位等相关内容

#### 最容易被唤起的 Prompt 示例
```
帮我查询明天北京到上海的火车票
```

### Tool2: 航铁动态精准追踪

#### 详细描述
支持列车、航班动态实时查询，返回列车位置、检票口等信息及航班起降、登机口等状态，同步说明延误等异常原因

#### 调试所需的输入参数
**输入**:
- 航铁编号（字符串）：列车车次/航班号
- 查询类型（字符串）：列车动态/航班动态

**输出**:
- 对应航铁的实时动态信息，含位置/状态、配套设施、异常原因等

#### 最容易被唤起的 Prompt 示例
```
帮我看看G123次列车现在到哪了
```

### Tool3: 航铁知识智能问答

#### 详细描述
内置铁路、航空领域知识库，针对票务政策、退改签、行李规定等高频问题，快速给出精准、规范的解答

#### 调试所需的输入参数
**输入**:
- 问题内容（字符串）：铁路/航空领域的出行相关问题

**输出**:
- 基于知识库的专业、准确的问题解答内容

#### 最容易被唤起的 Prompt 示例
```
学生票每年能买几次，要什么证件核验
```

## 可适配平台

方舟，Python，Cursor

## 前置要求

- Python >= 3.11
- TripNow API Key（需要从产品服务开通链接提交申请获取）

## 鉴权方式

**APIKey**：通过产品服务开通链接提交申请，审核通过后获取专属APIKey，调用接口时在请求头中携带该APIKey完成鉴权

**服务开通链接（整体产品）**: [产品服务开通链接待补充]

## 安装部署

### 客户部署服务（情况一）

若客户采用此方式，需提供 api key 以直接调取服务，具体步骤如下：

1. 从产品服务开通链接提交申请，获取专属APIKey；
2. 查阅产品官方接口文档，按规范构造请求参数；
3. 在自有系统/平台中集成接口，请求时携带APIKey；
4. 接收接口返回的JSON格式数据，解析并展示。

### 安装步骤

#### 1. 克隆或下载项目

```bash
cd tripnow-mcp
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或者使用 pip 直接安装：

```bash
pip install httpx>=0.25.0 mcp>=1.0.0 pydantic>=2.0.0
```

### 配置 API Key

有两种方式配置 API Key：

#### 方式一：环境变量（推荐）

在运行 MCP 服务器之前，设置环境变量：

```bash
export TRIPNOW_API_KEY="your_api_key_here"
```

#### 方式二：HTTP Header

在 MCP 客户端配置中，可以通过 HTTP Header 传递 API Key：

- `TRIPNOW_API_KEY`
- `tripnow-api-key`
- `tripnow_api_key`

## 使用方法

### 一、STDIO 方式（本地运行）

#### Python 方式：直接运行

```bash
python api_mcp.py
```

#### 在 MCP 客户端中配置

在您的 MCP 客户端配置文件（如 Cursor 的 `mcp.json`）中添加：

```json
{
  "mcpServers": {
    "tripnow": {
      "command": "python",
      "args": [
        "/path/to/tripnow-mcp/api_mcp.py"
      ],
      "env": {
        "TRIPNOW_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```


### 二、Streamable HTTP 方式（推荐）

如果您的 MCP 服务器部署在远程服务器上，可以使用 Streamable HTTP 方式：

```json
{
  "mcpServers": {
    "tripnow": {
      "url": "https://your-server.com/tripnow-mcp",
      "headers": {
        "TRIPNOW_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

## API 工具说明

### chat_completions

调用 TripNow 旅行助手 API，可以查询火车票、机票、酒店等旅行相关信息。该工具支持以下三种主要功能：

1. **航铁票务实时查询**：根据出发地、目的地、出行日期查询机票或火车票信息
2. **航铁动态精准追踪**：根据航铁编号查询列车或航班的实时动态信息
3. **航铁知识智能问答**：回答铁路、航空领域的出行相关问题

#### 参数说明

- `messages` (List[dict]): 消息列表，支持多轮对话
  - 每个消息包含：
    - `role` (str): 消息角色，如 `'user'`, `'assistant'`, `'system'`
    - `content` (str): 消息内容

#### 返回格式

返回标准的 ChatCompletion 响应，包含：
- 模型回复内容
- Token 使用统计
- 响应元数据

## 使用示例

### 示例 1：航铁票务实时查询

```python
# 查询火车票
messages = [
    {
        "role": "user",
        "content": "帮我查询明天北京到上海的火车票"
    }
]

# 调用 chat_completions 工具
result = await chat_completions(messages=messages)
```

```python
# 查询机票
messages = [
    {
        "role": "user",
        "content": "帮我查一下北京到上海的机票，日期是2024年12月25日"
    }
]
```

### 示例 2：航铁动态精准追踪

```python
# 查询列车动态
messages = [
    {
        "role": "user",
        "content": "帮我看看G123次列车现在到哪了"
    }
]
```

```python
# 查询航班动态
messages = [
    {
        "role": "user",
        "content": "CA1234航班现在什么状态"
    }
]
```

### 示例 3：航铁知识智能问答

```python
# 询问票务政策
messages = [
    {
        "role": "user",
        "content": "学生票每年能买几次，要什么证件核验"
    }
]
```

```python
# 询问退改签政策
messages = [
    {
        "role": "user",
        "content": "火车票退票手续费怎么算"
    }
]
```

### 示例 4：多轮对话查询

```python
# 第一轮：查询机票
messages = [
    {
        "role": "user",
        "content": "我想从北京飞往上海"
    }
]

# 第二轮：继续对话
messages.append({
    "role": "assistant",
    "content": "为您找到了以下航班..."
})

messages.append({
    "role": "user",
    "content": "帮我看看最早那班的状态"
})
```

## 响应格式示例

### 成功响应

```markdown
## TripNow 旅行助手回复

- **模型**: tripnow-travel-pro
- **响应ID**: chatcmpl-xxx

### 回复内容

为您找到了以下从北京到长沙的火车班次：
1. G501 次，08:00-14:30，二等座 ¥553
2. G503 次，10:00-16:30，二等座 ¥553
...

### Token使用统计
- **提示词Token**: 25
- **完成Token**: 150
- **总Token**: 175
```

### 错误响应

如果 API Key 未设置或无效，会返回错误信息：

```
⚠️ **错误**: error: TRIPNOW_API_KEY not set
```

## 项目结构

```
tripnow-mcp/
├── api_mcp.py          # MCP 服务器主文件
├── models.py           # 数据模型定义
├── markdown_utils.py   # Markdown 工具函数
├── requirements.txt    # Python 依赖
├── pyproject.toml      # 项目配置
└── README.md          # 本文件
```

## 开发说明

### 运行开发服务器

```bash
python api_mcp.py
```

服务器将启动在 Streamable HTTP 模式下，可以通过 HTTP 请求调用。

### 代码结构说明

- **api_mcp.py**: 
  - 定义 MCP 服务器实例
  - 实现 `chat_completions` 工具
  - 处理 API Key 获取和 HTTP 请求

- **models.py**:
  - `Message`: 消息模型
  - `ChatCompletionResponse`: API 响应模型
  - `ErrorResponse`: 错误响应模型

- **markdown_utils.py**:
  - 提供 Markdown 格式化工具函数

## 常见问题

### Q1: 如何获取 TripNow API Key？

A: 请访问 TripNow 官方网站或联系客服获取 API Key。

### Q2: API Key 应该放在哪里？

A: 推荐使用环境变量 `TRIPNOW_API_KEY`，也可以通过 HTTP Header 传递。

### Q3: 支持哪些传输方式？

A: 目前支持 STDIO 和 Streamable HTTP 两种方式。

### Q4: 如何测试 MCP 服务器？

A: 可以使用 MCP 客户端（如 Cursor）连接服务器，然后通过 AI 助手调用 `chat_completions` 工具进行测试。

### Q5: 响应格式是什么？

A: 默认返回文本格式，也可以通过配置返回 JSON 格式。

## 支持协议

遵循MCP广场平台服务协议，同时遵守铁路、航空领域相关信息服务规范

## License

专有商业协议

## 相关链接

- [TripNow 官方网站](https://tripnowengine.133.cn/tripnow-ai-open-platform/#/)
- [MCP 协议文档](https://modelcontextprotocol.io)
- [产品服务开通链接](https://tripnowengine.133.cn/tripnow-ai-open-platform/#/engine)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 正式版本发布
- 支持航铁票务实时查询（机票、火车票）
- 支持航铁动态精准追踪（列车、航班动态）
- 支持航铁知识智能问答（票务政策、退改签、行李规定等）
- 支持多轮对话
- 支持 STDIO 和 Streamable HTTP 传输方式
