# OpenCode 配置指南

这是一份详细的 OpenCode 配置说明，包含各种使用场景的示例。

## 目录

1. [基本配置](#基本配置)
2. [MCP 服务器配置](#mcp-服务器配置)
3. [AI 提供商配置](#ai-提供商配置)
4. [实际使用示例](#实际使用示例)

---

## 基本配置

OpenCode 的配置文件位于：
- macOS/Linux: `~/.config/opencode/opencode.json`
- Windows: `%APPDATA%\opencode\opencode.json`

基本结构：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [],
  "mcp": {},
  "provider": {}
}
```

---

## MCP 服务器配置

### 1. 本地 MCP 服务（stdio 类型）

#### 示例 1：Python MCP 服务（本项目）

```json
"mcp": {
  "magic-html-extractor": {
    "type": "stdio",
    "command": "uv",
    "args": [
      "--directory",
      "/Users/fujd/Desktop/magic-html-plus-python-mcp",
      "run",
      "mcp_server.py"
    ],
    "enabled": true,
    "env": {}
  }
}
```

**说明：**
- `type`: `stdio` 表示通过标准输入/输出通信
- `command`: 启动命令（这里使用 uv）
- `args`: 命令参数
- `enabled`: 是否启用该服务
- `env`: 环境变量（可选）

#### 示例 2：Node.js MCP 服务（Filesystem）

```json
"filesystem": {
  "type": "stdio",
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "/Users/fujd/Desktop",
    "/Users/fujd/Documents"
  ],
  "enabled": true
}
```

**功能：** 允许 AI 访问指定目录的文件系统

#### 示例 3：GitHub MCP 服务

```json
"github": {
  "type": "stdio",
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-github"
  ],
  "enabled": true,
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
  }
}
```

**功能：** 允许 AI 访问 GitHub 仓库、Issue、PR 等

**获取 Token：**
1. 访问 https://github.com/settings/tokens
2. 生成新的 Personal Access Token
3. 将 Token 填入配置

### 2. 远程 MCP 服务（SSE 类型）

```json
"remote-service": {
  "type": "remote",
  "url": "http://127.0.0.1:8000/sse",
  "enabled": true,
  "oauth": false,
  "timeout": 10000
}
```

**说明：**
- `type`: `remote` 表示远程服务
- `url`: SSE 端点 URL
- `oauth`: 是否需要 OAuth 认证
- `timeout`: 超时时间（毫秒）

### 3. 常用 MCP 服务列表

| 服务名 | NPM 包 | 功能 |
|--------|--------|------|
| filesystem | `@modelcontextprotocol/server-filesystem` | 文件系统访问 |
| github | `@modelcontextprotocol/server-github` | GitHub 集成 |
| gitlab | `@modelcontextprotocol/server-gitlab` | GitLab 集成 |
| postgres | `@modelcontextprotocol/server-postgres` | PostgreSQL 数据库 |
| sqlite | `@modelcontextprotocol/server-sqlite` | SQLite 数据库 |
| brave-search | `@modelcontextprotocol/server-brave-search` | Brave 搜索 |
| google-maps | `@modelcontextprotocol/server-google-maps` | Google 地图 |
| puppeteer | `@modelcontextprotocol/server-puppeteer` | 浏览器自动化 |

---

## AI 提供商配置

### 1. 火山引擎（豆包）

```json
"volcengine": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "VolcEngine",
  "options": {
    "baseURL": "https://ark.cn-beijing.volces.com/api/v3",
    "apiKey": "你的API密钥"
  },
  "models": {
    "doubao-seed-1-8-251228": {
      "name": "doubao-seed-1-8-251228"
    }
  }
}
```

### 2. OpenAI

```json
"openai": {
  "npm": "@ai-sdk/openai",
  "name": "OpenAI",
  "options": {
    "apiKey": "sk-xxxxxxxxxxxx"
  },
  "models": {
    "gpt-4o": {
      "name": "gpt-4o"
    },
    "gpt-4o-mini": {
      "name": "gpt-4o-mini"
    }
  }
}
```

### 3. Anthropic (Claude)

```json
"anthropic": {
  "npm": "@ai-sdk/anthropic",
  "name": "Anthropic",
  "options": {
    "apiKey": "sk-ant-xxxxxxxxxxxx"
  },
  "models": {
    "claude-3-5-sonnet-20241022": {
      "name": "claude-3-5-sonnet-20241022"
    }
  }
}
```

### 4. Google (Gemini)

```json
"google": {
  "npm": "@ai-sdk/google",
  "name": "Google",
  "options": {
    "apiKey": "AIzaxxxxxxxxxxxx"
  },
  "models": {
    "gemini-2.0-flash-exp": {
      "name": "gemini-2.0-flash-exp"
    }
  }
}
```

### 5. 本地 Ollama

```json
"ollama": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Ollama",
  "options": {
    "baseURL": "http://localhost:11434/v1",
    "apiKey": "ollama"
  },
  "models": {
    "qwen2.5-coder:7b": {
      "name": "qwen2.5-coder:7b"
    },
    "deepseek-r1:7b": {
      "name": "deepseek-r1:7b"
    }
  }
}
```

**前置要求：**
1. 安装 Ollama：`brew install ollama` (macOS)
2. 启动服务：`ollama serve`
3. 下载模型：`ollama pull qwen2.5-coder:7b`

### 6. Azure OpenAI

```json
"azure": {
  "npm": "@ai-sdk/azure",
  "name": "Azure OpenAI",
  "options": {
    "resourceName": "your-resource-name",
    "apiKey": "xxxxxxxxxxxx"
  },
  "models": {
    "gpt-4o": {
      "name": "gpt-4o",
      "deploymentId": "your-deployment-id"
    }
  }
}
```

---

## 实际使用示例

### 场景 1：配置本项目的 Magic HTML Extractor MCP 服务

**步骤：**

1. 打开配置文件：
```bash
code ~/.config/opencode/opencode.json
```

2. 添加配置：
```json
{
  "mcp": {
    "magic-html-extractor": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/Users/fujd/Desktop/magic-html-plus-python-mcp",
        "run",
        "mcp_server.py"
      ],
      "enabled": true
    }
  },
  "provider": {
    "volcengine": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "VolcEngine",
      "options": {
        "baseURL": "https://ark.cn-beijing.volces.com/api/v3",
        "apiKey": "你的密钥"
      },
      "models": {
        "doubao-seed-1-8-251228": {
          "name": "doubao-seed-1-8-251228"
        }
      }
    }
  }
}
```

3. 在 OpenCode 中使用：
```
请帮我提取这个网页的内容：https://example.com/article
```

### 场景 2：配置多个 AI 提供商

```json
{
  "provider": {
    "openai": {
      "npm": "@ai-sdk/openai",
      "name": "OpenAI",
      "options": {
        "apiKey": "sk-xxxx"
      },
      "models": {
        "gpt-4o": { "name": "gpt-4o" }
      }
    },
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (本地)",
      "options": {
        "baseURL": "http://localhost:11434/v1",
        "apiKey": "ollama"
      },
      "models": {
        "qwen2.5-coder:7b": { "name": "qwen2.5-coder:7b" }
      }
    }
  }
}
```

这样可以在使用时选择不同的模型。

### 场景 3：配置文件系统和搜索能力

```json
{
  "mcp": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/fujd/Projects",
        "/Users/fujd/Documents"
      ],
      "enabled": true
    },
    "brave-search": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "enabled": true,
      "env": {
        "BRAVE_API_KEY": "你的Brave API密钥"
      }
    }
  }
}
```

**使用示例：**
- "请搜索最新的 Python 3.13 特性"
- "请读取我 Projects 目录下的 README.md"

---

## 调试技巧

### 1. 检查 MCP 服务是否正常

```bash
# 测试本项目的 MCP 服务
cd /Users/fujd/Desktop/magic-html-plus-python-mcp
uv run mcp_server.py

# 测试 Node.js MCP 服务
npx @modelcontextprotocol/server-filesystem /tmp
```

### 2. 查看日志

OpenCode 会在控制台输出 MCP 服务的日志，如果遇到问题可以查看。

### 3. 常见问题

**问题 1：MCP 服务启动失败**
- 检查命令路径是否正确
- 检查依赖是否已安装
- 查看环境变量是否配置正确

**问题 2：API 密钥无效**
- 确认密钥是否过期
- 检查密钥格式是否正确
- 验证 baseURL 是否正确

**问题 3：模型不可用**
- 检查模型名称是否正确
- 确认账户是否有权限访问该模型
- 尝试其他模型

---

## 最佳实践

1. **分离敏感信息**：不要将 API 密钥提交到版本控制
2. **按需启用**：只启用需要的 MCP 服务，避免资源浪费
3. **使用本地模型**：开发时可以使用 Ollama 等本地模型节省成本
4. **定期更新**：保持 MCP 服务和提供商包的更新

---

## 参考资源

- OpenCode 官网: https://opencode.ai
- MCP 官方文档: https://modelcontextprotocol.io
- MCP 服务列表: https://github.com/modelcontextprotocol/servers
- AI SDK 文档: https://sdk.vercel.ai

---

## 总结

本指南涵盖了 OpenCode 的主要配置场景：

✅ MCP 服务器配置（本地和远程）
✅ AI 提供商配置（多种模型）
✅ 实际使用示例
✅ 调试和最佳实践

根据你的需求选择合适的配置，开始使用 OpenCode！
