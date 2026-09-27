# -*- coding: utf-8 -*-
"""Фикстура самотеста: мини-аудит, внесённый в АУДИТЫ и в опись."""


def проверить(исх):
    try:
        return len(исх)
    except TypeError:
        return 0
