# Git Discipline

- Keep commits small, logical, and focused on a single change.
- Never commit data files (`.sqlite`), FAISS indexes (`.pkl`, `.index`), or heavy model weights (`.keras`, `.bin`) unless explicitly required as static mocks.
- Rely on `.gitignore` to prevent caching environments from polluting the repository.
- Use `git mv` when renaming/moving files to preserve Git history cleanly.
