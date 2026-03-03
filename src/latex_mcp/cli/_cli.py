#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : _cli.py

import argparse

from ..servers import latex_mcp


def main():
    parser = argparse.ArgumentParser(description="LaTeX MCP Server")
    parser.add_argument(
        "-t",
        "--transport",
        choices=["stdio", "sse", "http", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    args = parser.parse_args()

    # Map http to streamable-http
    transport = "streamable-http" if args.transport == "http" else args.transport
    latex_mcp.run(transport=transport)
