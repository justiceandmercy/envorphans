# envorphans

Find environment variables defined in your `.env` files that are **never referenced** anywhere in your source code.

Dead env vars accumulate fast: renamed features, abandoned experiments, copy-pasted templates. `envorphans` scans your `.env*` files, collects every defined variable, then searches your source tree for references (`process.env.X`, `os.getenv("X")`, `os.environ["X"]`, `${X}`, and more) and reports the ones that nothing reads.

## Features

- Auto-discovers `.env` and `.env.*` files (skips `.env.example`, `.env.sample`, `.env.template`).
- Recognizes references across JS/TS, Python, Go, Rust, Ruby, Java, shell, YAML, JSON, TOML, and Markdown.
- Zero dependencies — pure Python 3.8+.
- Text or JSON output.
- `--strict` flag for CI: exits non-zero when orphans are found.

## Install

```bash
pip install envorphans
```

Or from source:

```bash
git clone https://github.com/yourname/envorphans
cd envorphans
pip install -e .
```

## Usage

```bash
# scan current directory
envorphans

# scan a project
envorphans ./my-app

# JSON output (for tooling)
envorphans ./my-app --format json

# fail CI on orphans
envorphans ./my-app --strict

# custom extensions / ignored dirs
envorphans . --extensions py,js,ts --ignore node_modules,dist
```

Example output:

```
Found 3 orphaned environment variable(s):
  - LEGACY_API_KEY
  - OLD_FEATURE_FLAG
  - UNUSED_DB_HOST

Scanned 2 env file(s), 14 referenced var(s).
```

## How it works

1. Walks the tree for `.env*` files and parses `KEY=value` lines (including `export KEY=...`).
2. Walks source files (respecting ignored directories) and applies a set of reference patterns.
3. Reports `defined - referenced`.

## License

MIT
