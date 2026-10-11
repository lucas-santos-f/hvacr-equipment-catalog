# Plugins

Thin wrappers that make the workflows in `agent-capabilities/` available as slash
commands in Claude Code.

Install by symlinking into the project's command directory:

```bash
mkdir -p .claude/commands
ln -s ../../plugins/add-endpoint.md .claude/commands/add-endpoint.md
ln -s ../../plugins/release-check.md .claude/commands/release-check.md
```

Then `/add-endpoint` and `/release-check` are available in a session opened on this
repo.

The commands are deliberately one line each. The procedure lives in
`agent-capabilities/`, so there is one copy of it and the command just points at it.
