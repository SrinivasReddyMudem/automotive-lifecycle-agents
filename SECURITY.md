# Security Policy

## Scope

This repository contains AI agent configuration files, skill definitions,
Python command-line tools, and documentation for automotive software
engineering use cases.

**It does not contain:**
- Real vehicle software
- ECU firmware or binaries
- Production safety-critical code
- Proprietary automotive supplier data
- Real customer information

---

## Responsible disclosure

If you discover a security vulnerability in this repository:

1. Do NOT open a public GitHub issue for the vulnerability
2. Email the repository owner directly with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
3. Allow reasonable time for a response before public disclosure

---

## Security considerations for users

### AI-generated content is not a substitute for engineering review

All outputs from these agents are advisory only. No output from these
agents should be used in a production vehicle software project without:
- Review by a qualified engineer in the relevant domain
- Compliance with your organisation's development process
- Appropriate verification and validation activities

### Synthetic data only

All examples in this repository use synthetic data. Users must ensure
they do not input real proprietary code, customer data, or confidential
vehicle parameters into any AI tool, including Claude.

### Cybersecurity analysis outputs

TARA analysis outputs produced by the iso21434-tara skill and safety-and-cyber-lead
agent are illustrative examples. They do not constitute a formal ISO 21434
cybersecurity assessment and require review by a qualified cybersecurity
engineer before use.

### Functional safety analysis outputs

HARA outputs and ASIL calculations produced by these tools require review
and approval by a qualified functional safety engineer per ISO 26262
before use in any project. The ASIL calculator implements a lookup table
based on published methodology — it is not a qualified safety tool.

---

## Python tool security

The Python tools in `tools/` are simple command-line scripts with no
network access, no file write operations beyond stdout, and no external
dependencies. They process only the command-line arguments provided.

Users should review these scripts before running them in environments
with restricted execution policies.
