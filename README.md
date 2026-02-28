# latex-mcp

[![Publish to PyPI](https://github.com/SepineTam/latex-mcp/actions/workflows/release-pypi.yml/badge.svg)](https://github.com/SepineTam/latex-mcp/actions/workflows/release-pypi.yml)
[![Build and Push Docker Images](https://github.com/SepineTam/latex-mcp/actions/workflows/release-docker.yml/badge.svg)](https://github.com/SepineTam/latex-mcp/actions/workflows/release-docker.yml)
[![PyPI version](https://img.shields.io/pypi/v/latex-mcp.svg)](https://pypi.org/project/latex-mcp/)
[![License: AGPL 3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/SepineTam/latex-mcp/issues/new)

Enable AI agents to compile TeX files with LaTeX inside a Docker container.

## Quickly Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- Recommended hardware: 4GB or higher
- Network access to [GitHub Container Registry](https://github.com/SepineTam/latex-mcp/pkgs/container/latex-mcp)

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
