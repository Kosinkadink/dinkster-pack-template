# dinkster-pack-template

Create a Dinkster node pack with one text node, tests, a wheel build and registry publishing.
Requires Python 3.12+, Git and [uv](https://docs.astral.sh/uv/).

## Create and test

1. Click **Use this template**, create your repository, and clone it.
   For a local trial, clone this repository instead; no new GitHub repository is required.
2. From the clone, choose your permanent pack name (replace `maple-text` below):

```sh
python tools/rename.py maple-text
uv sync --python 3.12
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv build --wheel
uv pip install --no-deps --reinstall dist/*.whl
uv run --no-sync pytest -q
uv run --no-sync dinkster-doctor .
```

The tests pass and doctor reports `healthy: 0 error(s), 0 warning(s)`.
Stop and fix any failure before submitting. Tests call `execute` on plain values;
doctor independently checks registration, schemas and the pack boundary.
The development environment pins the published `dinkster-api==0.0.2`; no engine checkout is needed.

Edit `src/<your_package>/__init__.py` to add nodes, register them in `NODES`, and add tests.
Node ids belong to your manifest's namespace. Import Dinkster through `dinkster_api.v1` only,
never another node pack. The host supplies that API; extra runtime requirements go in both
`pyproject.toml` dependencies and manifest `requires`, pinned to the same versions.
Keep `uv.lock` committed; update the API pin and run all checks when adopting a new contract.

## Publish

Register your publisher and obtain a token from your registry operator.
On your repository, add the Actions secret `DINKSTER_REGISTRY_TOKEN` and variable
`DINKSTER_REGISTRY_URL` (the registry origin, for example your disposable registry's
`http://127.0.0.1:8791`; hosted Actions needs an HTTPS registry it can reach).
Never put the token in a file tracked by Git or a command argument.

For a local disposable registry, set the token privately in your shell's
`DINKSTER_REGISTRY_TOKEN` environment variable, then run:

```sh
python tools/publish.py dist/*.whl --registry http://127.0.0.1:8791
```

The command reports the candidate id and state until it is accepted and its release is active.
Rejection, operator review, HTTP errors and a five-minute timeout fail the command.
Inspect the candidate before retrying; an uncertain HTTP result may already have submitted it.
Use only the disposable registry for trial packs.

For a real release, set the same new version in `pyproject.toml` and `dinkster-pack.toml`,
run `uv lock` and the checks above, commit, and push a matching `v<version>` tag.
Actions builds and tests on every push and pull request; version tags submit that exact wheel
through the documented single-pack HTTP endpoint and report its candidate state.
The template repository itself and the unrenamed `my-pack` example cannot submit.

See the [pack authoring reference](https://github.com/Kosinkadink/Dinkster/blob/main/docs/pack-authoring.md)
for the public node API and manifest contract.
