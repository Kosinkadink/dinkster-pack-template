# dinkster-pack-template

Create a Dinkster node pack with one text node, tests, a wheel build and registry
publishing. Requires Python 3.12+, Git and [uv](https://docs.astral.sh/uv/).

## Run locally

Use **Use this template** to create a repository, or clone this repository for a
local trial. From the clone, choose a permanent pack name instead of `maple-text`:

```sh
uv run --no-project --python 3.12 tools/rename.py maple-text
uv sync --python 3.12
uv build --wheel
uv pip install --no-deps --reinstall dist/*.whl
uv run --no-sync pytest -q
uv run --no-sync dinkster-doctor .
```

Stop and fix failures before submitting a pack. Use only a disposable registry
for trial packs.

## Reference and operating notes

- [Development checks and runtime install check](docs/development.md).
- [Publisher setup and release procedure](docs/publishing.md).
- [Pack authoring reference](https://github.com/Kosinkadink/Dinkster/blob/main/docs/pack-authoring.md): public node API and manifest contract.
- [Registry submission guide](https://github.com/Kosinkadink/Dinkster/blob/main/docs/registry-submission.md): disposable example, admission, findings and withdrawal.
- [Node documentation](docs/nodes/).
