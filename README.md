# Hack-the-Stage

## Frontend (dev server at `http://localhost:3000`)
```bash
pnpm i
pnpm run dev
```
## Speech to Text 
```bash
cd Hack-the-Stage/backend
uvicorn main:app --reload 
curl -X POST http://127.0.0.1:8000/dev/local-audio-to-text
```
## response text
python services/answer_question.py

## HeyGen token sanity check
```bash
cd Hack-the-Stage/backend_new
python heygenAPI.py
```

## Smoke Tests

Quickly verify that the **Cohere API key** and **Google Cloud Storage credentials** are working (upload, list, signed URL).

```bash
cd Hack-the-Stage
python -m backend.tools.smoke_tests

# or run separately
python -m backend.tools.smoke_tests --cohere
python -m backend.tools.smoke_tests --gcs
python -m backend.tools.smoke_tests --gcpconf
```
