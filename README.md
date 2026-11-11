# dinkster-pack-template

Create a Dinkster node pack with one text node, tests, a wheel build and registry publishing.
Requires Python 3.12+, Git and [uv](https://docs.astral.sh/uv/).

## Create and test

1. Click **Use this template**, create your repository, and clone it.
   For a local trial, clone this repository instead; no new GitHub repository is required.
2. From the clone, choose your permanent pack name (replace `maple-text` below):

```sh
uv run --no-project --python 3.12 tools/rename.py maple-text
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

1. Open [Dinkster publisher accounts](https://id.dinkster.org/registry) and sign in
   with your Dinkster account. New authors choose **Create a Dinkster account**,
   enter a handle, email and password, and check their email. Under **Verify your
   email or resend verification**, enter the emailed token and click **Verify
   email**, then sign in with the handle and password. **Resend verification
   email** replaces the previous token; only the newest email works. If no email
   arrives, contact support rather than making another account. Social sign-in
   such as GitHub is optional when offered. The registry itself has no separate
   sign-in, and no social-provider account is required.
2. Choose your personal account or an organization you own or administer, then
   click **Claim publisher**. The publisher name is your Dinkster handle or
   organization slug, bound to its immutable account id. It does not prove
   ownership of a matching GitHub name. Existing registry names and `dinkster`
   are reserved; claiming a name does not grant official status.
3. Enter your renamed pack name to limit the token to that pack (or leave it
   blank for all packs owned by the publisher). Choose an expiry in the future,
   at most 90 days away, then click **Create token**.
4. Save the token immediately in your secret manager. It is shown once only;
   refreshing the page or token list cannot recover it. **Revoke token** on the
   same page refuses subsequent registry requests. Create a replacement before
   expiry and update your workflow secret; do not reuse a revoked token.

No server access or operator command is needed for these steps. On a disposable
or self-hosted registry, use its identity service's `/registry` page instead.

On your repository, add the Actions secret `DINKSTER_REGISTRY_TOKEN` and variable
`DINKSTER_REGISTRY_URL` (the registry origin, for example your disposable registry's
`http://127.0.0.1:8791`; hosted Actions needs an HTTPS registry it can reach).
Never put the token in a file tracked by Git or a command argument.

For a local disposable registry, set the token privately in your shell's
`DINKSTER_REGISTRY_TOKEN` environment variable, then run:

```sh
uv run --no-sync python tools/publish.py dist/*.whl --registry http://127.0.0.1:8791
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

See the [registry submission guide](https://github.com/Kosinkadink/Dinkster/blob/main/docs/registry-submission.md)
for a complete disposable example, admission rules, candidate findings and withdrawal.
The [pack authoring reference](https://github.com/Kosinkadink/Dinkster/blob/main/docs/pack-authoring.md)
covers the public node API and manifest contract.
