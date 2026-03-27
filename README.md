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
