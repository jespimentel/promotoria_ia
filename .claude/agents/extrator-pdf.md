---
name: extrator-pdf
description: Compatibilidade para a skill extrator-pdf, que converte PDFs em Markdown página por página e usa Tesseract quando a página tem menos de 300 caracteres nativos.
tools: Read, Write, Glob, Grep, PowerShell
model: sonnet
---

# Extrator de PDF — compatibilidade

Este agente foi mantido apenas para compatibilidade com chamadas antigas.

Leia integralmente `.claude/skills/extrator-pdf/SKILL.md` e siga essa skill, incluindo o script
fornecido nela. Em especial:

- a decisão entre texto nativo e OCR é feita página por página;
- páginas com menos de 300 caracteres usam Tesseract automaticamente;
- uma LLM externa só pode receber as páginas em que o Tesseract efetivamente falhou e depois de
  autorização expressa do usuário.

As instruções da skill prevalecem sobre qualquer comportamento legado deste agente.
