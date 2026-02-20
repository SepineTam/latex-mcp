#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : compiler.py

import asyncio
import glob
import os
import re
from pathlib import Path
from typing import List, Tuple

from .command import LaTeXCommand
from .types import CleanInput, CleanResult, CompileInput, CompileMode, CompileResult


class LaTeXCompiler:
    """
    LaTeX compiler implementation.

    Supports both automatic (latexmk) and manual compilation modes.
    """

    # Auxiliary file extensions to clean
    AUX_EXTENSIONS = [
        ".aux", ".log", ".out", ".toc", ".lof", ".lot",
        ".fls", ".fdb_latexmk", ".bbl", ".blg", ".nav",
        ".snm", ".vrb", ".dvi", ".ps", ".idx", ".ilg",
        ".ind", ".glo", ".gls", ".acn", ".acr", ".ist",
        ".bcf", ".run.xml", ".xdv", ".synctex.gz",
    ]

    @classmethod
    async def compile(cls, params: CompileInput) -> CompileResult:
        """
        Compile a TeX file.

        Args:
            params: Compilation parameters.

        Returns:
            CompileResult with success status, PDF path, and log.
        """
        # Validate working directory
        working_dir = Path(params.working_dir)
        if not working_dir.exists():
            return CompileResult(
                success=False,
                errors=[f"Working directory does not exist: {params.working_dir}"],
            )

        # Validate tex file
        tex_path = working_dir / params.tex_file
        if not tex_path.exists():
            return CompileResult(
                success=False,
                errors=[f"TeX file does not exist: {params.tex_file}"],
            )

        # Choose compilation mode
        if params.mode == CompileMode.AUTO:
            return await cls._compile_auto(params)
        else:
            return await cls._compile_manual(params)

    @classmethod
    async def _compile_auto(cls, params: CompileInput) -> CompileResult:
        """
        Compile using latexmk (automatic mode).

        Args:
            params: Compilation parameters.

        Returns:
            CompileResult with compilation results.
        """
        try:
            cmd = LaTeXCommand.build_latexmk_command(
                compiler=params.compiler,
                tex_file=params.tex_file,
                options=params.options,
            )
        except ValueError as e:
            return CompileResult(
                success=False,
                errors=[str(e)],
            )

        # Run compilation
        process, stdout, stderr = await cls._run_command(
            cmd, params.working_dir
        )

        # Parse output
        log = stdout.decode("utf-8", errors="replace")
        errors, warnings = cls._parse_log(log)

        # Check for success
        success = process.returncode == 0

        # Determine PDF path
        pdf_path = None
        if success:
            tex_stem = Path(params.tex_file).stem
            pdf_path = f"{tex_stem}.pdf"

        # Clean if requested
        if params.clean_after and success:
            await cls._clean_aux_files(params.working_dir, params.tex_file)

        return CompileResult(
            success=success,
            pdf_path=pdf_path,
            log=log,
            errors=errors,
            warnings=warnings,
        )

    @classmethod
    async def _compile_manual(cls, params: CompileInput) -> CompileResult:
        """
        Compile using manual compilation chain.

        Args:
            params: Compilation parameters.

        Returns:
            CompileResult with compilation results.
        """
        try:
            cmd = LaTeXCommand.build_compile_command(
                compiler=params.compiler,
                tex_file=params.tex_file,
                options=params.options,
            )
        except ValueError as e:
            return CompileResult(
                success=False,
                errors=[str(e)],
            )

        all_log = []
        all_errors = []
        all_warnings = []

        # Run multiple compilation passes
        for i in range(params.compile_times):
            process, stdout, stderr = await cls._run_command(
                cmd, params.working_dir
            )

            log = stdout.decode("utf-8", errors="replace")
            all_log.append(f"--- Pass {i + 1} ---\n{log}")

            errors, warnings = cls._parse_log(log)
            all_errors.extend(errors)
            all_warnings.extend(warnings)

            # Run bibtex on first pass if bibliography specified
            if i == 0 and params.bibliography:
                await cls._run_bibtex(params)

            # If compilation failed, stop
            if process.returncode != 0:
                break

        success = process.returncode == 0

        # Determine PDF path
        pdf_path = None
        if success:
            tex_stem = Path(params.tex_file).stem
            pdf_path = f"{tex_stem}.pdf"

        # Clean if requested
        if params.clean_after and success:
            await cls._clean_aux_files(params.working_dir, params.tex_file)

        return CompileResult(
            success=success,
            pdf_path=pdf_path,
            log="\n".join(all_log),
            errors=list(set(all_errors)),  # Deduplicate
            warnings=list(set(all_warnings)),
        )

    @classmethod
    async def _run_bibtex(cls, params: CompileInput) -> Tuple[int, bytes, bytes]:
        """
        Run bibtex for bibliography processing.

        Args:
            params: Compilation parameters.

        Returns:
            Tuple of (return_code, stdout, stderr).
        """
        tex_stem = Path(params.tex_file).stem
        try:
            cmd = LaTeXCommand.build_bibtex_command(tex_stem)
            return await cls._run_command(cmd, params.working_dir)
        except ValueError:
            # bibtex not available, skip
            return (0, b"", b"")

    @classmethod
    async def _run_command(
        cls, cmd: List[str], cwd: str
    ) -> Tuple[asyncio.subprocess.Process, bytes, bytes]:
        """
        Run a command asynchronously.

        Args:
            cmd: Command and arguments.
            cwd: Working directory.

        Returns:
            Tuple of (process, stdout, stderr).
        """
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return process, stdout, stderr

    @classmethod
    def _parse_log(cls, log: str) -> Tuple[List[str], List[str]]:
        """
        Parse LaTeX log for errors and warnings.

        Args:
            log: Compilation log text.

        Returns:
            Tuple of (errors, warnings).
        """
        errors = []
        warnings = []

        # Error patterns
        error_patterns = [
            r"^! (.+)$",
            r"^l\.(\d+) (.+)$",
            r"Error: (.+)",
        ]

        # Warning patterns
        warning_patterns = [
            r"Warning: (.+)",
            r"LaTeX Warning: (.+)",
            r"Package (\w+) Warning: (.+)",
            r"Overfull \\hbox",
            r"Underfull \\hbox",
        ]

        lines = log.split("\n")
        for line in lines:
            # Check for errors
            for pattern in error_patterns:
                match = re.search(pattern, line)
                if match:
                    errors.append(line.strip())
                    break

            # Check for warnings
            for pattern in warning_patterns:
                if re.search(pattern, line):
                    warnings.append(line.strip())
                    break

        return errors, warnings

    @classmethod
    async def clean(cls, params: CleanInput) -> CleanResult:
        """
        Clean auxiliary files.

        Args:
            params: Clean parameters.

        Returns:
            CleanResult with list of removed files.
        """
        working_dir = Path(params.working_dir)
        if not working_dir.exists():
            return CleanResult(
                success=False,
                message=f"Working directory does not exist: {params.working_dir}",
            )

        removed_files = await cls._clean_aux_files(
            params.working_dir, params.tex_file
        )

        return CleanResult(
            success=True,
            removed_files=removed_files,
            message=f"Removed {len(removed_files)} auxiliary file(s)",
        )

    @classmethod
    async def _clean_aux_files(
        cls, working_dir: str, tex_file: str = None
    ) -> List[str]:
        """
        Remove auxiliary files.

        Args:
            working_dir: Working directory.
            tex_file: Specific tex file (optional).

        Returns:
            List of removed file paths.
        """
        removed = []
        base_path = Path(working_dir)

        if tex_file:
            # Clean for specific file
            stem = Path(tex_file).stem
            for ext in cls.AUX_EXTENSIONS:
                pattern = str(base_path / f"{stem}{ext}")
                for file_path in glob.glob(pattern):
                    try:
                        os.remove(file_path)
                        removed.append(file_path)
                    except OSError:
                        pass
        else:
            # Clean all auxiliary files in directory
            for ext in cls.AUX_EXTENSIONS:
                pattern = str(base_path / f"*{ext}")
                for file_path in glob.glob(pattern):
                    try:
                        os.remove(file_path)
                        removed.append(file_path)
                    except OSError:
                        pass

        return removed
