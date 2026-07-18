# Browser Fallback for the Full Screenshot

The automated QA runner now sends the PNG through Vibe's native image-attachment channel.
Use Vibe Work only when the project-local multimodal runner is unavailable:

1. Open [Vibe Work / Mistral](https://chat.mistral.ai/).
2. Start a new Work task.
3. Upload the entire `browser-bundle` folder prepared beside this file. Mistral Work
   accepts folders and PNG files.
4. Open `BROWSER_QA_PROMPT.md`, paste its contents as the task prompt, and submit.
5. Verify that the response starts with `FULL_IMAGE_INSPECTED: YES` and reports
   `1440 × 900`. Reject the report if it cannot state both.
6. Save the accepted report as `docs/FULL_QA_REPORT.md` before starting repair work.

Do not upload only the source code: the full-resolution screenshot is the primary evidence
that prevents another source-only false green.
