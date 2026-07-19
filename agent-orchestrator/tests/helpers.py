from pathlib import Path


def write_registry(root: Path) -> Path:
    config = root / "config"
    config.mkdir(parents=True)
    (config / "providers.toml").write_text('''
[[providers]]
id = "test-provider"
display_name = "Test"
kind = "fake"
status = "active"
auth_kind = "none"
billing = "metered-api"
plan = "test"
''', encoding="utf-8")
    (config / "models.toml").write_text('''
[[models]]
id = "weak"
provider = "test-provider"
remote_id = "weak"
quality = 0.4
context_tokens = 1000
input_cost_per_million = 1.0
output_cost_per_million = 2.0
price_effective_at = "2026-01-01"
modalities = ["text"]
capabilities = ["summarization", "architecture", "file-editing"]

[[models]]
id = "strong"
provider = "test-provider"
remote_id = "strong"
quality = 0.9
context_tokens = 1000
input_cost_per_million = 5.0
output_cost_per_million = 10.0
price_effective_at = "2026-01-01"
modalities = ["text"]
capabilities = ["summarization", "architecture", "file-editing"]
''', encoding="utf-8")
    (config / "harnesses.toml").write_text('''
[[harnesses]]
id = "fake-read"
kind = "fake"
provider = "test-provider"
tool_class = "inference"
max_parallel = 4
status = "eligible"

[[harnesses]]
id = "fake-write"
kind = "fake-write"
provider = "test-provider"
tool_class = "files_write"
max_parallel = 2
status = "eligible"
''', encoding="utf-8")
    (config / "profiles.toml").write_text('''
[[profiles]]
id = "weak-read"
model = "weak"
harness = "fake-read"
status = "eligible"
success_probability = 0.86
capabilities = ["summarization", "architecture"]
tool_class = "inference"
max_parallel = 4
benchmark_version = "test-v1"

[[profiles]]
id = "strong-read"
model = "strong"
harness = "fake-read"
status = "eligible"
success_probability = 0.99
capabilities = ["summarization", "architecture"]
tool_class = "inference"
max_parallel = 4
benchmark_version = "test-v1"

[[profiles]]
id = "strong-write"
model = "strong"
harness = "fake-write"
status = "eligible"
success_probability = 0.99
capabilities = ["file-editing"]
tool_class = "files_write"
max_parallel = 2
benchmark_version = "test-v1"
''', encoding="utf-8")
    return config
