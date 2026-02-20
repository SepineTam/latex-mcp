#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : command.py

import shutil
from typing import Dict, List, Optional

from .types import CompilerType


class LaTeXCommand:
    """
    LaTeX command management.

    Manages paths and availability of LaTeX compilers and auxiliary tools.
    """

    # Default command paths (will be verified at runtime)
    _COMPILER_PATHS: Dict[CompilerType, str] = {
        CompilerType.PDFLATEX: "pdflatex",
        CompilerType.XELATEX: "xelatex",
        CompilerType.LUALATEX: "lualatex",
    }

    # Auxiliary commands for bibliography, index, etc.
    _AUX_COMMANDS: Dict[str, str] = {
        "bibtex": "bibtex",
        "biber": "biber",
        "makeindex": "makeindex",
        "makeglossaries": "makeglossaries",
        "latexmk": "latexmk",
    }

    # Cache for found commands
    _cached_compilers: Optional[Dict[CompilerType, Optional[str]]] = None
    _cached_aux: Optional[Dict[str, Optional[str]]] = None

    @classmethod
    def _find_command(cls, command: str) -> Optional[str]:
        """
        Find the full path to a command.

        Args:
            command: Command name to find.

        Returns:
            Full path to command or None if not found.
        """
        path = shutil.which(command)
        return path

    @classmethod
    def get_compiler_path(cls, compiler: CompilerType) -> Optional[str]:
        """
        Get the path to a LaTeX compiler.

        Args:
            compiler: Compiler type.

        Returns:
            Full path to compiler or None if not found.
        """
        if cls._cached_compilers is None:
            cls._cache_compilers()

        return cls._cached_compilers.get(compiler)

    @classmethod
    def _cache_compilers(cls) -> None:
        """Cache compiler paths."""
        cls._cached_compilers = {}
        for compiler_type, command in cls._COMPILER_PATHS.items():
            path = cls._find_command(command)
            cls._cached_compilers[compiler_type] = path

    @classmethod
    def get_aux_command(cls, name: str) -> Optional[str]:
        """
        Get the path to an auxiliary command.

        Args:
            name: Auxiliary command name (e.g., 'bibtex', 'biber').

        Returns:
            Full path to command or None if not found.
        """
        if cls._cached_aux is None:
            cls._cache_aux_commands()

        return cls._cached_aux.get(name)

    @classmethod
    def _cache_aux_commands(cls) -> None:
        """Cache auxiliary command paths."""
        cls._cached_aux = {}
        for name, command in cls._AUX_COMMANDS.items():
            path = cls._find_command(command)
            cls._cached_aux[name] = path

    @classmethod
    def list_available_compilers(cls) -> List[str]:
        """
        List all available LaTeX compilers.

        Returns:
            List of available compiler names.
        """
        if cls._cached_compilers is None:
            cls._cache_compilers()

        return [
            compiler.value
            for compiler, path in cls._cached_compilers.items()
            if path is not None
        ]

    @classmethod
    def list_available_aux_commands(cls) -> List[str]:
        """
        List all available auxiliary commands.

        Returns:
            List of available auxiliary command names.
        """
        if cls._cached_aux is None:
            cls._cache_aux_commands()

        return [
            name
            for name, path in cls._cached_aux.items()
            if path is not None
        ]

    @classmethod
    def is_latexmk_available(cls) -> bool:
        """
        Check if latexmk is available.

        Returns:
            True if latexmk is available.
        """
        return cls.get_aux_command("latexmk") is not None

    @classmethod
    def build_compile_command(
        cls,
        compiler: CompilerType,
        tex_file: str,
        options: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Build a compilation command.

        Args:
            compiler: Compiler type.
            tex_file: Path to .tex file.
            options: Additional compiler options.

        Returns:
            Command as list of strings.
        """
        compiler_path = cls.get_compiler_path(compiler)
        if compiler_path is None:
            raise ValueError(f"Compiler {compiler.value} not found")

        cmd = [
            compiler_path,
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
        ]

        if options:
            cmd.extend(options)

        cmd.append(tex_file)

        return cmd

    @classmethod
    def build_latexmk_command(
        cls,
        compiler: CompilerType,
        tex_file: str,
        options: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Build a latexmk command.

        Args:
            compiler: Compiler type.
            tex_file: Path to .tex file.
            options: Additional compiler options.

        Returns:
            Command as list of strings.
        """
        latexmk_path = cls.get_aux_command("latexmk")
        if latexmk_path is None:
            raise ValueError("latexmk not found")

        # Map compiler to latexmk flag
        pdf_flag = {
            CompilerType.PDFLATEX: "-pdf",
            CompilerType.XELATEX: "-xelatex",
            CompilerType.LUALATEX: "-lualatex",
        }

        cmd = [
            latexmk_path,
            pdf_flag.get(compiler, "-pdf"),
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
        ]

        # Set the specific compiler if not pdflatex
        if compiler == CompilerType.PDFLATEX:
            pass  # Default, no need to specify
        elif compiler == CompilerType.XELATEX:
            cmd.append("-xelatex")
        elif compiler == CompilerType.LUALATEX:
            cmd.append("-lualatex")

        if options:
            cmd.extend(options)

        cmd.append(tex_file)

        return cmd

    @classmethod
    def build_bibtex_command(cls, aux_file: str) -> List[str]:
        """
        Build a bibtex command.

        Args:
            aux_file: Path to .aux file (without extension).

        Returns:
            Command as list of strings.
        """
        bibtex_path = cls.get_aux_command("bibtex")
        if bibtex_path is None:
            raise ValueError("bibtex not found")

        return [bibtex_path, aux_file]

    @classmethod
    def build_clean_command(cls, tex_file: str) -> List[str]:
        """
        Build a latexmk clean command.

        Args:
            tex_file: Path to .tex file.

        Returns:
            Command as list of strings.
        """
        latexmk_path = cls.get_aux_command("latexmk")
        if latexmk_path is None:
            raise ValueError("latexmk not found")

        return [latexmk_path, "-c", tex_file]
