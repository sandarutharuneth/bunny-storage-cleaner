# Bunny Storage Cleaner
Run daily automated Bunny Storage cleaner with GitHub Actions.

> [!NOTE]
> Since **[Bunny.net](https://bunny.net)** currently doesn't provide a storage manager to delete older files to keep your cost down, especially if you're running an application with Bunny services, this will be really helpful. This is a short-term solution I made to manage my storage, and Bunny.net can introduce a storage manager at any point. Until then, this will have to do. Any contributors are welcome to push a new change.

## Installation

1) Folk my Repository
2) Add env secrets.
> Repository Settings > Secrets and Variables > Actions
```env
BUNNY_API_KEY=Your Bunny API Key
BUNNY_STORAGE_ZONE=Your Storage Zone Name
DISCORD_WEBHOOK_URL=Discord Webhook URL To Get Notified On Each Run
```
3) Adjust how much older files you need to delete. ( In `scripts/cleanup.py` Line: `12` )
```py
cutoff = datetime.now(timezone.utc) - timedelta(days=30) # Default is 30 days
```
4) Remove the comments in ( in `.github/workflows/delete_bunny_storage.yml` Line: `4 and 5`
```sh
#  schedule:
#    - cron: '0 0 * * *'
```
   
5) (Optional) Set Daily Run Time ( in `.github/workflows/delete_bunny_storage.yml` Line: `5` )
- Default is set to run at `00:00 UTC`

# Run
That's pretty much it. You don't need to do anything else. GitHub Actions will automatically run the script everyday at your set time and will send the status of the run to your Discord with the webhook.

> [!Note]
> If you find this code useful, Give a ⭐️ to my repository. Please and Thank You!
