# Track

Sync with Time's Pulse.

## Local Development

```bash
pip install -r requirements.txt
cp src/local_env.example.py src/local_env.py
python src/run_local.py
```

## Deployment

1. Fork this repository
2. Enable GitHub Actions in repository settings:
   - Actions permissions: Allow all actions and reusable workflows
   - Workflow permissions: Read and write permissions
3. Enable GitHub Pages in repository settings:
   - Source: GitHub Actions
4. Add repository secrets:
   - `QWEATHER_KEY`: QWeather API key
   - `QWEATHER_PUBLIC_ID`: QWeather Public ID

Actions will automatically run every 30 minutes to update content.

## Configuration

- Edit `config.py` to customize RSS feeds and cities (Find city codes: [LocationList](https://github.com/qwd/LocationList))
- Edit `.github/workflows/update.yml` to change update frequency