```markdown
# BRC2.0 Validator CLI Tool

**A Python-powered validator for official BRC-20/BRC2.0 JSON inscriptions — ensuring compliance with indexer standards.**

---

## 📌 Overview

**BRC2.0** is built on the proven BRC-20 standard with enhanced programmable features. This validator ensures your inscriptions follow the official specification and will be properly indexed.

**Key Features:**
- ✅ Official BRC-20/BRC2.0 schema validation  
- ✅ Support for 4-byte, 5-byte, and 6-byte tickers
- ✅ Validates `deploy`, `mint`, `transfer`, `call`, `transact`, `withdraw` operations
- ✅ Snipe protection validation for 6-byte tickers
- ✅ Strict mode for production validation

---

## 🚀 Installation

```bash
git clone https://github.com/Phantagyro/brc2.0-validator.git
cd brc2.0-validator
pip install jsonschema
```

---

## 🧪 Usage

### Basic validation:
```bash
python3 brc2_validator.py inscription.json
```

### Strict mode (warnings as errors):
```bash
python3 brc2_validator.py inscription.json --strict
```

### From stdin:
```bash
cat inscription.json | python3 brc2_validator.py
```

---

## 📋 Supported Operations

| Operation | Description | Required Fields |
|-----------|-------------|----------------|
| `deploy` | Deploy new token | `p`, `op`, `tick`, `max`, `lim` |
| `mint` | Mint tokens | `p`, `op`, `tick`, `amt` |
| `transfer` | Transfer tokens | `p`, `op`, `tick`, `amt` |
| `call` | Call function | `p`, `op`, `tick`, `func` |
| `transact` | Execute transaction | `p`, `op`, `tick` |
| `withdraw` | Withdraw tokens | `p`, `op`, `tick`, `amt` |

---

## 🎯 Ticker Rules

- **4-byte tickers**: Standard format (e.g., `TEST`, `COIN`)
- **5-byte tickers**: Self-mint only (e.g., `TOKEN`) 
- **6-byte tickers**: With snipe protection (e.g., `MyToken`)

---

## 📝 Example

**Deploy inscription:**
```json
{
  "p": "brc-20",
  "op": "deploy",
  "tick": "TEST", 
  "max": "1000000000",
  "lim": "10000",
  "dec": "8"
}
```

**Validation result:**
```
✅ JSON Schema validation passed.
✅ All validations passed. Inscription follows official BRC2.0 specification.
```

---

## 🤝 Contributing

This validator follows the official BRC2.0 specification. Pull requests welcome for:
- Bug fixes
- Performance improvements  
- Additional validation rules

---

## 🔗 References

- [Official BRC-20 Documentation](https://layer1.gitbook.io/layer1-foundation/protocols/brc-20)
- [6-byte Ticker Proposal](https://github.com/bestinslot-xyz/OPI/pull/67)
- [BRC2.0 Enhancement Proposal](https://docs.bestinslot.xyz/brc2.0)

---

## 📄 License

MIT License

**Maintainer:** [Phantagyro](https://github.com/Phantagyro)  
**Last Updated:** July 2025

