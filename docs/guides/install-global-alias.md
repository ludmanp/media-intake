# Global Alias Install

The project-owned entrypoint is:

```text
/Users/mark/Projects/AI/media-intake/bin/media-intake
```

Expose it globally through `~/bin`:

```bash
mkdir -p /Users/mark/bin
ln -sfn /Users/mark/Projects/AI/media-intake/bin/media-intake /Users/mark/bin/media-intake
```

Verify:

```bash
/Users/mark/bin/media-intake --help
command -v media-intake
```

If `command -v media-intake` does not resolve, ensure `/Users/mark/bin` is on `PATH`.
For zsh, add this to `~/.zshrc`:

```bash
export PATH="$HOME/bin:$HOME/.local/bin:$PATH"
```
