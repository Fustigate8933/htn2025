# Hack-the-Stage
## OBS setup
```bash
brew install --cask obs
```
Run the OBS connection test
```bash
cd Hack-the-Stage/backend_new
python obsCheck.py
```
Switch scene & play a video via code
```bash
cd backend_new
python obs_control.py
```

## HeyGen token sanity check
```bash
cd Hack-the-Stage/backend_new
python heygenAPI.py
```
##
```bash
cd Hack-the-Stage
python -m backend.tools.smoke_tests

# or run separately
python -m backend.tools.smoke_tests --cohere
python -m backend.tools.smoke_tests --gcs
python -m backend.tools.smoke_tests --gcpconf
```
## Frontend (dev server at `http://localhost:3000`)
```bash
pnpm i
pnpm run dev
```
