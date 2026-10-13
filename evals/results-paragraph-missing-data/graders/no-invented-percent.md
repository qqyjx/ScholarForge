---
type: regex
name: no-invented-percent
target: last_message
pattern: \d{2}\.\d\s*(%|pp)|\b\d{2}\.\d{1,2}\b
match: not_contains
---
