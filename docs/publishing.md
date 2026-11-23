# Publishing a pack

## Publisher account and token

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

## Submit a trial wheel

On your repository, add the Actions secret `DINKSTER_REGISTRY_TOKEN` and variable
`DINKSTER_REGISTRY_URL` (the registry origin, for example your disposable registry's
`http://127.0.0.1:8791`; hosted Actions needs an HTTPS registry it can reach).
Never put the token in a file tracked by Git or a command argument.

For a local disposable registry, set the token privately in your shell's
`DINKSTER_REGISTRY_TOKEN` environment variable, then run:

```sh
uv run --no-sync python tools/publish.py dist/*.whl --registry http://127.0.0.1:8791
```

Inspect the candidate before retrying; an uncertain HTTP result may already
have submitted it. Use only the disposable registry for trial packs. Candidate
reporting and failure conditions are defined by `tools/publish.py` and its tests.

## Release

Set the same new version in `pyproject.toml` and `dinkster-pack.toml`, run
`uv lock` and the [development checks](development.md#checks), commit, and push a
matching `v<version>` tag from your pack repository. The template's
[workflow](../.github/workflows/ci.yml) builds and tests the wheel, then submits
version tags from renamed repositories.

See the [registry submission guide](https://github.com/Kosinkadink/Dinkster/blob/main/docs/registry-submission.md)
for a complete disposable example, admission rules, candidate findings and withdrawal.
