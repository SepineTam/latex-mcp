# latex-mcp
Enable AI agents to compile TeX files with LaTeX inside a Docker container.

## Quickly Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- Recommended hardware: 4GB or higher
- Network access to GitHub Container Registry (ghcr.io)

### Configuration in Claude Code

Create a `.mcp.json` file in your project root. This configuration is ideal for team collaboration as it uses `${PWD}` environment variable that works across different machines:

```json
{
  "mcpServers": {
    "latex-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--mount",
        "type=bind,src=${PWD},dst=${PWD}",
        "-w",
        "${PWD}",
        "ghcr.io/sepinetam/latex-mcp:latest"
      ]
    }
  }
}
```
