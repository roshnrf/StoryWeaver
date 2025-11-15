# Data Directory

## Overview

This directory contains sample session data and example files for the StoryWeaver Speech Therapy platform.

---

## Files

### `sessions.csv`

Sample session data showing the system's outputs across multiple practice sessions.

**Columns:**
- `timestamp`: ISO 8601 timestamp of session
- `transcription`: Child's spoken description (Whisper output)
- `errors`: JSON array of detected errors with corrections
- `story`: Generated practice story (pipe-separated sections)

**Sample Size:** 6 sessions (anonymized pilot data)

**Privacy Note:** ⚠️ This data contains NO personally identifiable information. All names are fictional characters (Leo, Lilly, Pip, etc.).

---

## Error Types in Dataset

### Grammar Errors
```json
{
  "error_type": "grammar",
  "incorrect_phrase": "any phone",
  "corrected_phrase": "a phone",
  "explanation": "Use 'a' for positive statements"
}
```

### Phonological Errors
```json
{
  "error_type": "phonological",
  "incorrect_phrase": "UN",
  "corrected_phrase": "Run",
  "explanation": "Say /r/ first, like a roaring lion"
}
```

### Articulation Errors
```json
{
  "error_type": "articulation",
  "incorrect_phrase": "thaw",
  "corrected_phrase": "saw",
  "explanation": "Put your tongue behind your teeth for /s/"
}
```

---

## Story Generation Examples

### Input: "I have any phone"
**Detected Error:** Grammar - "any" → "a"

**Generated Story:**
```
Leo the little lion cub loved to play!
One sunny afternoon, Leo found a bright yellow block.
"Roar!" he cheered happily. "I have a phone!"
```

### Input: "UN!"
**Detected Error:** Phonological - missing /r/ sound

**Generated Story:**
```
Dash the puppy loved to play outside.
"Time to run!" Dash barked happily.
He stretched his paws and dashed across the grass.
```

---

## Using This Data

### Load Sessions Data

```python
import pandas as pd
import json

# Load CSV
df = pd.read_csv('data/sessions.csv')

# Parse errors JSON
df['errors'] = df['errors'].apply(lambda x: json.loads(x) if pd.notna(x) else [])

# Display summary
print(f"Total sessions: {len(df)}")
print(f"Sessions with errors: {df['errors'].apply(len).sum()}")
```

### Analyze Error Patterns

```python
# Extract all error types
error_types = []
for errors in df['errors']:
    if isinstance(errors, list):
        for err in errors:
            error_types.append(err.get('error_type', 'unknown'))

# Count frequency
from collections import Counter
print(Counter(error_types))
# Output: {'grammar': 4, 'phonological': 2, 'articulation': 1}
```

---

## Data Statistics

| Metric | Value |
|--------|-------|
| Total Sessions | 6 |
| Unique Transcriptions | 4 |
| Total Errors Detected | 7 |
| Grammar Errors | 4 (57%) |
| Phonological Errors | 2 (29%) |
| Articulation Errors | 1 (14%) |
| Sessions with No Errors | 1 (17%) |
| Average Story Length | ~150 words |

---

## Privacy & Ethics

✅ **Safe for Public Repository:**
- No real names or identifying information
- Fictional character names only
- No audio files included
- Timestamps anonymized (dates only)
- Educational examples

❌ **Do NOT Include:**
- Raw audio recordings
- Real children's names
- School/location information
- Detailed personal information

---

## Adding Your Own Data

### For Local Testing

1. Create `data/local_sessions/` (gitignored)
2. Add your session files there
3. Use same CSV format
4. Keep offline and private

### CSV Format

```csv
timestamp,transcription,errors,story
2025-01-01T12:00:00,"text here","[{\"error_type\":\"...\"}]","story here"
```

---

## Citation

If you use this data in research, please cite:

```bibtex
@dataset{storyweaver_sessions_2024,
  title = {StoryWeaver Sample Sessions Dataset},
  author = {Rauof, Roshan A and Fariha, Reem},
  year = {2024},
  note = {Sample data from StoryWeaver speech therapy pilot study}
}
```

---

## Questions?

For questions about the data:
- Open an issue on GitHub
- Email: storyweaver@example.com

Last updated: November 2024