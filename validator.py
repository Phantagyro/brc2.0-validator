import json
import sys
import argparse
from jsonschema import validate, ValidationError

# Updated schemas following official BRC2.0 proposal
DEPLOY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "BRC2.0 Deploy Operation",
    "type": "object",
    "required": ["p", "op", "tick", "max", "lim"],
    "properties": {
        "p": {"type": "string", "const": "brc-20"},  # Standard BRC-20 protocol
        "op": {"type": "string", "enum": ["deploy"]},
        "tick": {
            "type": "string",
            "minLength": 1,
            "maxLength": 6,  # Support up to 6-byte tickers
            "pattern": "^[a-zA-Z0-9]+$"  # Allow mixed case for compatibility
        },
        "max": {
            "type": "string",
            "pattern": "^[0-9]+$"
        },
        "lim": {  # Standard BRC-20 limit field
            "type": "string", 
            "pattern": "^[0-9]+$"
        },
        "dec": {
            "type": "string",
            "pattern": "^[0-9]+$",
            "default": "18"
        }
    },
    "additionalProperties": False
}

MINT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "BRC2.0 Mint Operation", 
    "type": "object",
    "required": ["p", "op", "tick", "amt"],
    "properties": {
        "p": {"type": "string", "const": "brc-20"},
        "op": {"type": "string", "enum": ["mint"]},
        "tick": {
            "type": "string",
            "minLength": 1,
            "maxLength": 6,
            "pattern": "^[a-zA-Z0-9]+$"
        },
        "amt": {
            "type": "string",
            "pattern": "^[0-9]+$"
        }
    },
    "additionalProperties": False
}

TRANSFER_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "BRC2.0 Transfer Operation",
    "type": "object", 
    "required": ["p", "op", "tick", "amt"],
    "properties": {
        "p": {"type": "string", "const": "brc-20"},
        "op": {"type": "string", "enum": ["transfer"]},
        "tick": {
            "type": "string",
            "minLength": 1,
            "maxLength": 6,
            "pattern": "^[a-zA-Z0-9]+$"
        },
        "amt": {
            "type": "string",
            "pattern": "^[0-9]+$"
        }
    },
    "additionalProperties": False
}

# New BRC2.0 operations
CALL_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "BRC2.0 Call Operation",
    "type": "object",
    "required": ["p", "op", "tick", "func"],
    "properties": {
        "p": {"type": "string", "const": "brc-20"},
        "op": {"type": "string", "enum": ["call"]},
        "tick": {
            "type": "string",
            "minLength": 1,
            "maxLength": 6,
            "pattern": "^[a-zA-Z0-9]+$"
        },
        "func": {"type": "string"},
        "args": {"type": "array"}
    },
    "additionalProperties": False
}

TRANSACT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "BRC2.0 Transact Operation",
    "type": "object",
    "required": ["p", "op", "tick"],
    "properties": {
        "p": {"type": "string", "const": "brc-20"},
        "op": {"type": "string", "enum": ["transact"]},
        "tick": {
            "type": "string",
            "minLength": 1,
            "maxLength": 6,
            "pattern": "^[a-zA-Z0-9]+$"
        },
        "data": {"type": "object"}
    },
    "additionalProperties": False
}

WITHDRAW_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "BRC2.0 Withdraw Operation",
    "type": "object",
    "required": ["p", "op", "tick", "amt"],
    "properties": {
        "p": {"type": "string", "const": "brc-20"},
        "op": {"type": "string", "enum": ["withdraw"]},
        "tick": {
            "type": "string",
            "minLength": 1,
            "maxLength": 6,
            "pattern": "^[a-zA-Z0-9]+$"
        },
        "amt": {
            "type": "string",
            "pattern": "^[0-9]+$"
        }
    },
    "additionalProperties": False
}

def validate_ticker_rules(tick, op):
    """Validate ticker according to 6-byte proposal rules"""
    warnings = []
    
    # 4-byte tickers (standard)
    if len(tick) == 4:
        if not tick.isupper():
            warnings.append("4-byte tickers should be uppercase for consistency")
    
    # 5-byte self-mint tickers
    elif len(tick) == 5:
        if op != "mint":
            warnings.append("5-byte tickers are reserved for self-mint operations")
        if not tick.startswith(tick[0].upper()):
            warnings.append("5-byte tickers should start with uppercase")
    
    # 6-byte tickers with snipe protection
    elif len(tick) == 6:
        if not any(c.islower() for c in tick):
            warnings.append("6-byte tickers should include lowercase letters for snipe protection")
    
    return warnings

def smart_checks(inscription):
    """Enhanced validation with official BRC2.0 rules"""
    errors = []
    warnings = []
    
    # Protocol check
    p = inscription.get("p", "")
    if p != "brc-20":
        errors.append(f"Protocol should be 'brc-20', got '{p}'")
    
    # Ticker validation
    tick = inscription.get("tick", "")
    op = inscription.get("op", "")
    
    if len(tick) < 1 or len(tick) > 6:
        errors.append(f"Ticker '{tick}' must be 1-6 characters long")
    
    if not tick.replace("-", "").replace("_", "").isalnum():
        warnings.append(f"Ticker '{tick}' contains special characters - may not be supported by all indexers")
    
    # Apply ticker rules
    ticker_warnings = validate_ticker_rules(tick, op)
    warnings.extend(ticker_warnings)
    
    # Operation-specific checks
    if op == "deploy":
        if "lim" not in inscription:
            errors.append("Deploy operation missing required 'lim' field")
        
        # Remove non-standard vesting checks
        if "meta" in inscription:
            warnings.append("'meta' field with custom properties may not be indexed by standard indexers")
    
    # Amount validation for numeric fields
    for field in ["max", "lim", "amt"]:
        if field in inscription:
            try:
                int(inscription[field])
            except ValueError:
                errors.append(f"Field '{field}' must be a valid integer string")
    
    return errors, warnings

def main():
    parser = argparse.ArgumentParser(description="BRC2.0 JSON Schema Validator (Official Spec Compliant)")
    parser.add_argument("file", nargs="?", help="Path to JSON inscription file. Reads stdin if omitted.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()

    try:
        if args.file:
            with open(args.file, "r") as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        sys.exit(1)

    # Choose schema based on operation
    op = data.get("op")
    schema_map = {
        "deploy": DEPLOY_SCHEMA,
        "mint": MINT_SCHEMA, 
        "transfer": TRANSFER_SCHEMA,
        "call": CALL_SCHEMA,
        "transact": TRANSACT_SCHEMA,
        "withdraw": WITHDRAW_SCHEMA
    }
    
    schema = schema_map.get(op)
    if not schema:
        print(f"❌ Unsupported or missing 'op' field: {op}")
        print(f"   Supported operations: {', '.join(schema_map.keys())}")
        sys.exit(1)

    # Validate JSON schema
    try:
        validate(instance=data, schema=schema)
        print("✅ JSON Schema validation passed.")
    except ValidationError as ve:
        print(f"❌ JSON Schema validation error: {ve.message}")
        print(f"   Failed at: {' -> '.join(str(p) for p in ve.absolute_path)}")
        sys.exit(1)

    # Run enhanced smart checks
    errors, warnings = smart_checks(data)
    
    if errors:
        print("❌ Validation errors:")
        for err in errors:
            print(f"   • {err}")
        sys.exit(1)
    
    if warnings:
        print("⚠️  Validation warnings:")
        for warn in warnings:
            print(f"   • {warn}")
        
        if args.strict:
            print("❌ Strict mode enabled: treating warnings as errors")
            sys.exit(1)
    
    if not warnings:
        print("✅ All validations passed. Inscription follows official BRC2.0 specification.")

if __name__ == "__main__":
    main()
