# Pack development

After the [local setup](../README.md#run-locally), edit
`src/<your_package>/__init__.py` to add nodes, register them in `NODES`, and add
tests. Keep node ids in the manifest's namespace. Use the [public authoring reference](https://github.com/Kosinkadink/Dinkster/blob/main/docs/pack-authoring.md)
for the node API and manifest contract. The host supplies the API. Runtime code
imports `dinkster_api.v1` only, never another node pack; tests may use `load_pack`
from `dinkster_engine.testing`. Other engine imports remain private. Put extra
runtime requirements in both `pyproject.toml`
dependencies and manifest `requires`, pinned to the same versions. Keep `uv.lock`
committed; update the API pin and run all checks when adopting a new contract.

## Checks

```sh
uv run ruff check . tools/check-install
uv run ruff format --check . tools/check-install
uv run pyright
uv build --wheel
uv pip install --no-deps --reinstall dist/*.whl
uv run --no-sync pytest -q
uv run --no-sync dinkster-doctor .
```

Expect passing tests and `healthy: 0 error(s), 0 warning(s)` from doctor. Stop
and fix failures before publishing. The ordinary development checks need no
engine checkout, managed engine runtime or torch. See
[CI](../.github/workflows/ci.yml) for the built-wheel check, including doctor
against the installed manifest.

## Optional locked install check

To check the wheel against a published runtime and verified base:

```sh
uv build --wheel
uv run --script tools/check-install dist/*.whl --channel main
```

This Linux CPU check requires the normal probe jail. For the separate optional
CI job, set repository variable `DINKSTER_LOCKED_INSTALL_CHECK` to `true` and
`DINKSTER_INSTALL_CHANNEL` to `main` or `stable`. Use local `--mirror` for a
trusted runtime mirror and `--store` to choose the download cache. Defaults,
provisioning and refusal behavior are defined in `tools/check-install`.
