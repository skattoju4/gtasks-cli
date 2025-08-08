# gtasks-cli

A CLI tool to manage your Google Tasks, developed in collaboration with Gemini.

## Authentication

This tool supports multiple authentication methods to suit your environment.

### Automatic Flow (`--auth-flow auto`)

This is the default and recommended method. The tool will automatically:
1.  Try to open your default graphical web browser.
2.  If a graphical browser is not available, it will look for the `carbonyl` CLI browser.
3.  If neither is found, it will fall back to the manual flow.

### Carbonyl Flow (`--auth-flow carbonyl`)

This method specifically uses the `carbonyl` CLI browser. You must have `carbonyl` installed for this to work. You can install it with `npm install -g carbonyl`. Please note that `carbonyl` is not supported on all platforms, for example, Android is not supported.

### Manual Flow (`--auth-flow manual`)

This method does not require a browser. The tool will print an authentication URL. You will need to copy this URL into a browser on any machine, authenticate, and then paste the final redirect URL back into the CLI.

### Non-Interactive/CI Flow

For use in CI/CD pipelines or other non-interactive environments, you can pre-authenticate.
1.  Run the tool once locally in an interactive environment to generate a `token.json` file. This file contains your refresh token.
2.  Set the content of `credentials.json` and `token.json` as environment variables or secrets in your CI system (e.g., `CREDENTIALS_JSON` and `TOKEN_JSON`).
3.  The CI script can then write these to files before running the tool, allowing it to authenticate non-interactively.
