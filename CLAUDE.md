# Claude Development Rules

## JSON Serialization Rule
**ALWAYS use `mode='json'` in Pydantic model_dump() for API responses**

```python
# Correct ✅
return response(data={"hero": hero_out.model_dump(mode='json')})

# Incorrect ❌
return response(data={"hero": hero_out.model_dump()})
```

This ensures:
- UUID objects are converted to strings
- datetime objects are converted to ISO format
- All data types are properly serialized for JSON

## Commands
- Tests: (to be determined)
- Lint: (to be determined)
- Typecheck: (to be determined)