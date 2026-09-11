# Testing Strategy

## Centralized Tests
All tests are located in `tests/` and mirror the `src/` directory structure:
- `tests/app/`
- `tests/zone1/`
- `tests/zone2/`
- `tests/zone3/`

## Execution
Run tests from the repository root:
```bash
pytest tests/
```

## Mocking
Use `MockGeminiClient` and mock inference models to ensure tests run swiftly and without expensive hardware or internet dependencies.
