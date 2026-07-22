import hashlib
import re
import sys
from pathlib import Path


turn = int(sys.argv[1])
speaker = sys.argv[2]
prefix_length = int(sys.argv[3])
prefix_sha256 = sys.argv[4]

raw = Path("dialogue.md").read_bytes()
text = raw.decode("utf-8")
prefix = raw[:prefix_length]

if hashlib.sha256(prefix).hexdigest() != prefix_sha256:
    raise SystemExit("existing transcript prefix was modified")
if text.count("<!-- APPEND_NEXT_TURN -->") != 1:
    raise SystemExit("append marker missing or duplicated")
if len(re.findall(r"<!-- TURN \d+ -->", text)) != turn:
    raise SystemExit("unexpected number of turns")
if text.count(f"<!-- TURN {turn} -->") != 1:
    raise SystemExit("new turn marker missing or duplicated")

tail = raw[prefix_length:].decode("utf-8")
expected_start = f"<!-- TURN {turn} -->\n**{speaker}:**"
if not tail.startswith(expected_start):
    raise SystemExit("new contribution has wrong speaker or format")
body = tail[len(expected_start):].split("<!-- APPEND_NEXT_TURN -->", 1)[0]
words = re.findall(r"\b[\wÄÖÜäöüß’-]+\b", body, flags=re.UNICODE)
if not 100 <= len(words) <= 185:
    raise SystemExit(f"new contribution has {len(words)} words")
