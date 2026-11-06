# FROZEN.md — Version 2 Frozen Declaration

> **Version Status**: ⛔ FROZEN  
> **Date of Freeze**: 2025-03 (approx)  
> **Freeze Reason**: Superseded by `v3/` engine refactor. Code migrated to `v3/rpa_engine/`.

---

This directory (`v2/`) is the **first production RPA system**. It is no longer the active development target.

---

## What was this?

| Aspect | Detail |
|--------|--------|
| Purpose | Production RPA for multiple departments |
| Contents | `A-docs/`, `ConsultDepartment/`, `FinanceDepartment/`, `SafetyandQualityDepartment/`, `ScienceandTechnologyInnovationDepartment/`, `SuperVisionDepartment/` |
| License | Apache License 2.0 |

---

## Directory Layout (preserved as-is)

```
v2/
├── A-docs/                    # 验收/方案文档归档（2026-10-24 实测：原 AcceptanceReport/ 已更名）
├── ConsultDepartment/         # Consultation department scripts
├── FinanceDepartment/         # Finance department scripts
├── SafetyandQualityDepartment/            # Safety and quality department
├── ScienceandTechnologyInnovationDepartment/  # Science and technology innovation
└── SuperVisionDepartment/     # Supervision department (feng/ + zeng/1 + zeng/2)
```

> 2026-10-24 注记：本目录实测**无** `BaseDEMO/`、**无** `ArchivedAcceptanceReport/`；
> 原树中的这两项为历史记录，保留于此仅作追溯，实际布局以本节上方代码块为准。

---

## Migration Guidance

- New development must use `v3/rpa_engine/` only.
- This directory is kept **as historical reference only**.
