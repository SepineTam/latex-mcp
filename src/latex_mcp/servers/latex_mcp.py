#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : latex_mcp.py

import json
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from ..core.command import LaTeXCommand
from ..core.compiler import LaTeXCompiler
from ..core.types import CleanInput, CompileInput, CompileMode, CompilerType

latex_mcp = FastMCP(
    name="latex-mcp",
)


@latex_mcp.tool(
    name="latex_compile",
)
async def latex_compile(
    tex_file: str = "main.tex",
    mode: str = "auto",
    compiler: str = "pdflatex",
    working_dir: str = "/workspace",
    bibliography: Optional[str] = None,
    compile_times: int = 2,
    options: Optional[List[str]] = None,
    clean_after: bool = False,
) -> str:
    """
    Compile a TeX file to PDF using LaTeX.

    Args:
        tex_file: Path to the main .tex file (relative to working_dir)
        mode: Compilation mode - 'auto' uses latexmk, 'manual' uses direct compiler
        compiler: LaTeX compiler to use - 'pdflatex', 'xelatex', or 'lualatex'
        working_dir: Working directory for compilation
        bibliography: Path to .bib file (only used in manual mode)
        compile_times: Number of compilation passes, 1-5 (only used in manual mode)
        options: Additional compiler options
        clean_after: Whether to clean auxiliary files after compilation

    Returns:
        JSON string with success status, pdf_path, log, errors, and warnings
    """
    # Convert string parameters to enum types
    try:
        mode_enum = CompileMode(mode)
        compiler_enum = CompilerType(compiler)
    except ValueError as e:
        return json.dumps({
            "success": False,
            "errors": [f"Invalid parameter: {e}"],
        }, indent=2)

    params = CompileInput(
        tex_file=tex_file,
        mode=mode_enum,
        compiler=compiler_enum,
        working_dir=working_dir,
        bibliography=bibliography,
        compile_times=compile_times,
        options=options or [],
        clean_after=clean_after,
    )

    result = await LaTeXCompiler.compile(params)

    response = {
        "success": result.success,
        "pdf_path": result.pdf_path,
        "log": result.log,
        "errors": result.errors,
        "warnings": result.warnings,
    }

    return json.dumps(response, indent=2, ensure_ascii=False)


@latex_mcp.tool(
    name="latex_list_compilers",
)
async def latex_list_compilers() -> str:
    """
    List all available LaTeX compilers in the environment.

    Returns:
        JSON string with compilers list, aux_commands list, and latexmk_available bool
    """
    compilers = LaTeXCommand.list_available_compilers()
    aux_commands = LaTeXCommand.list_available_aux_commands()
    latexmk_available = LaTeXCommand.is_latexmk_available()

    response = {
        "compilers": compilers,
        "aux_commands": aux_commands,
        "latexmk_available": latexmk_available,
    }

    return json.dumps(response, indent=2, ensure_ascii=False)


@latex_mcp.tool(
    name="latex_clean",
)
async def latex_clean(
    working_dir: str = "/workspace",
    tex_file: Optional[str] = None,
) -> str:
    """
    Clean auxiliary files generated during LaTeX compilation.

    Args:
        working_dir: Working directory to clean
        tex_file: Specific .tex file to clean auxiliary files for.
                  If None, cleans all auxiliary files in the directory.

    Returns:
        JSON string with success status, removed_files list, and message
    """
    params = CleanInput(
        working_dir=working_dir,
        tex_file=tex_file,
    )

    result = await LaTeXCompiler.clean(params)

    response = {
        "success": result.success,
        "removed_files": result.removed_files,
        "message": result.message,
    }

    return json.dumps(response, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    latex_mcp.run()
