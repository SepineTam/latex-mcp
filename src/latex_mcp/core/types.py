#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : types.py

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CompilerType(str, Enum):
    """LaTeX compiler types."""
    PDFLATEX = "pdflatex"
    XELATEX = "xelatex"
    LUALATEX = "lualatex"


class CompileMode(str, Enum):
    """Compilation mode."""
    AUTO = "auto"       # Use latexmk for automatic compilation
    MANUAL = "manual"   # Manual compilation chain


class CompileInput(BaseModel):
    """Input parameters for LaTeX compilation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    tex_file: str = Field(
        ...,
        description="Path to the main .tex file (relative to working_dir)",
        min_length=1,
    )
    mode: CompileMode = Field(
        default=CompileMode.AUTO,
        description="Compilation mode: 'auto' uses latexmk, 'manual' uses specified compiler",
    )
    compiler: CompilerType = Field(
        default=CompilerType.PDFLATEX,
        description="LaTeX compiler to use: pdflatex, xelatex, or lualatex",
    )
    working_dir: str = Field(
        default="/workspace",
        description="Working directory for compilation",
    )
    bibliography: Optional[str] = Field(
        default=None,
        description="Path to bibliography file (.bib), only used in manual mode",
    )
    compile_times: int = Field(
        default=2,
        description="Number of compilation passes (1-5), only used in manual mode",
        ge=1,
        le=5,
    )
    options: List[str] = Field(
        default_factory=list,
        description="Additional compiler options",
    )
    clean_after: bool = Field(
        default=False,
        description="Whether to clean auxiliary files after compilation",
    )


class CompileResult(BaseModel):
    """Result of LaTeX compilation."""
    model_config = ConfigDict(
        validate_assignment=True,
    )

    success: bool = Field(
        ...,
        description="Whether compilation succeeded",
    )
    pdf_path: Optional[str] = Field(
        default=None,
        description="Path to the generated PDF file (relative to working_dir)",
    )
    log: str = Field(
        default="",
        description="Compilation log output",
    )
    errors: List[str] = Field(
        default_factory=list,
        description="List of error messages from compilation",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warning messages from compilation",
    )


class CleanInput(BaseModel):
    """Input parameters for cleaning auxiliary files."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    working_dir: str = Field(
        default="/workspace",
        description="Working directory to clean",
    )
    tex_file: Optional[str] = Field(
        default=None,
        description="Specific .tex file to clean auxiliary files for. If None, cleans all",
    )


class CleanResult(BaseModel):
    """Result of cleaning auxiliary files."""
    model_config = ConfigDict(
        validate_assignment=True,
    )

    success: bool = Field(
        ...,
        description="Whether cleaning succeeded",
    )
    removed_files: List[str] = Field(
        default_factory=list,
        description="List of removed auxiliary files",
    )
    message: str = Field(
        default="",
        description="Status message",
    )
