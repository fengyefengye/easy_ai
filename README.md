# easy_ai
它的调用链基本是这样：
```
src/main.py
  -> langchain_demo.run_agent(question, enable_mcp)
     -> load_settings()
     -> create_chat_model(settings)
     -> get_builtin_tools()
     -> 可选：load_mcp_tools(settings.mcp_servers_file)
     -> AgentService(model, tools, system_prompt)
     -> AgentService.ask(question)
        -> LangChain create_agent(...)
        -> agent.invoke({"messages": [...]})
        -> 提取最终答案 + 中间输出 + 工具调用
```

当前 `src/main.py` 默认输出 JSON，结构如下：
```json
{
  "answer": "最终答案",
  "intermediate_outputs": [
    {"type": "ai", "content": "..."},
    {"type": "tool", "content": "...", "tool_name": "calculator", "tool_call_id": "..."}
  ],
  "tool_calls": [
    {"id": "...", "name": "calculator", "args": {"expression": "1+2"}}
  ],
  "workflow": {
    "agent_init": {
      "model": "gpt-4o-mini",
      "system_prompt": "...",
      "tools": ["calculator", "current_time", "..."]
    },
    "invoke_input_messages": [
      {"role": "user", "content": "现在UTC时间是多少"}
    ],
    "conversation": [
      {"type": "ai_tool_call", "tool_name": "current_time", "tool_call_id": "...", "args": {}},
      {"type": "tool_output", "tool_name": "current_time", "tool_call_id": "...", "content": "2026-...+00:00"},
      {"type": "ai_output", "content": "当前UTC时间是..."}
    ],
    "final_result": "当前UTC时间是..."
  }
}
```

## 执行方式

### 1) 安装依赖
```bash
conda activate your_env_name
python -m pip install -e ".[dev]"
```

说明：`-e` 是可编辑安装，源码仍在当前仓库目录，不会拷贝一份到环境里；代码改动会立刻生效。

### 2) 配置密钥（推荐 `.env`，无需每次手动输入）
先复制模板并填写：
```bash
cp src/langchain_demo/config/.env.example src/langchain_demo/config/.env
```

程序会自动读取 `src/langchain_demo/config/.env`，且 `.env` 已被 `.gitignore` 忽略，不会上传到 GitHub。

也支持手动 `export`（可选）：
```bash
export OPENAI_API_KEY="你的key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-4o-mini"
export LLM_TEMPERATURE="0.2"
```

可选（Agent 系统提示词）：
```bash
export AGENT_SYSTEM_PROMPT="你是一个严谨的智能体助手。优先使用工具来获取事实，结论简洁准确。"
```

MCP 工具改为读取本地配置文件（默认路径：`src/langchain_demo/config/mcp_servers.json`）。
当前默认已写入以下 4 个服务：
- `filesystem`
- `git`
- `fetch`
- `time`

并且代码会对 MCP 工具做“只读过滤”，会拦截名字里含 `write/edit/create/update/delete/remove/commit/push...` 的工具。

MCP 运行前建议确认（尤其在 WSL）：
```bash
which uvx
uvx --version
```

如果没有 `uvx`：
```bash
python -m pip install uv
```

### 3) 运行

基础 QA 模式（不走工具）：
```bash
python src/main.py "法国首都是什么" --mode qa
```

Agent 模式（默认，包含内置工具）：
```bash
python src/main.py "现在UTC时间是多少"
```

Agent + MCP 模式（会读取 `src/langchain_demo/config/mcp_servers.json`）：
```bash
python src/main.py "帮我查一下今天的天气" --mode agent --enable-mcp
```

## 更多样例

### 样例 1：QA 模式
```bash
python src/main.py "请用三条总结MCP是什么" --mode qa
```

预期特征：
- `tool_calls` 为空
- `workflow.conversation` 只有 `ai_output`

### 样例 2：Agent 调用内置时间工具
```bash
python src/main.py "现在UTC时间是多少"
```

预期特征：
- `tool_calls` 包含 `current_time`
- `workflow.conversation` 顺序通常是：
  - `ai_tool_call`
  - `tool_output`
  - `ai_output`

### 样例 3：Agent 调用计算器工具
```bash
python src/main.py "计算 pi*100，并保留两位小数"
```

预期特征：
- `tool_calls` 包含 `calculator`
- `tool_calls[0].args` 中通常能看到表达式参数

### 样例 4：一次问题触发多个工具
```bash
python src/main.py "现在UTC时间是多少，并计算 12345*678"
```

预期特征：
- `tool_calls` 里可能同时出现 `current_time` 与 `calculator`
- `workflow.conversation` 会出现多组 `ai_tool_call -> tool_output`

### 样例 5：启用 MCP（只读工具）
```bash
python src/main.py "读取README.md前10行并告诉我项目是做什么的" --mode agent --enable-mcp
```

预期特征：
- `workflow.agent_init.tools` 会比未启用 MCP 时更多
- 若模型选择 MCP 工具，会在 `tool_calls` 里看到对应工具名

### 样例 6：检查当前加载了哪些工具
```bash
python src/main.py "请先告诉我你当前可用的工具名，再回答1+1等于几"
```

预期特征：
- `workflow.agent_init.tools` 展示完整工具列表
- `conversation` 中仍可看到实际工具调用轨迹

### 样例 7：不兼容网关时的错误输出
当 `OPENAI_BASE_URL` 不兼容工具调用协议时，会返回结构化错误，而不是直接崩溃：

```json
{
  "answer": "模型调用失败。请检查 OPENAI_BASE_URL 是否兼容 OpenAI Chat Completions 工具调用协议，原始错误: ...",
  "workflow": {
    "error": "..."
  }
}
```

建议优先使用：
```env
OPENAI_BASE_URL=https://api.openai.com/v1
```
