# Engineering Rules

1. **Protected Files:** `instructions/contract.md` is frozen. DO NOT alter the JSON shapes defined within.
2. **Zone Independence:** Zones must not import modules directly from one another. They communicate strictly through the data boundaries enforced by the `pipeline.py` and `streamlit_app.py`.
3. **No Silent Changes:** Do not modify logic, models, or configurations outside the explicit scope of an assigned task.
4. **Fallback Resilience:** Always ensure a mock/fallback path exists for AI models. Hardware constraints may prevent loading heavy models during demonstrations.
