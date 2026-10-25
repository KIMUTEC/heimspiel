---
description: Checkpoint-Commit vor einer größeren Änderung
argument-hint: [geplante Änderung]
allowed-tools: Bash(git add:*), Bash(git commit:*), Bash(git status:*), Bash(node tools/check.mjs)
---
Führ `node tools/check.mjs` aus, dann `git add -A && git commit -m "Checkpoint vor $ARGUMENTS"`. Wenn nichts zu committen ist, sag das einfach.
