import os
import requests
from datetime import datetime, timedelta, timezone

API_KEY = os.environ['BUNNY_API_KEY']
ZONE = os.environ['BUNNY_STORAGE_ZONE']
WEBHOOK_URL = os.environ['DISCORD_WEBHOOK_URL']
BASE_URL = f'https://storage.bunnycdn.com/{ZONE}'
HEADERS = { 'AccessKey': API_KEY }

# Adjust how much older your files have to be to be deleted
cutoff = datetime.now(timezone.utc) - timedelta(days=30)
deleted_count = 0
deleted_list = []

def list_items(path=''):
    r = requests.get(f'{BASE_URL}/{path}', headers=HEADERS)
    r.raise_for_status()
    return r.json()

def delete_file(full_path):
    global deleted_count
    print(f'🗑️ Deleting file: {full_path}')
    r = requests.delete(f'{BASE_URL}/{full_path}', headers=HEADERS)
    if r.status_code in (200, 204):
        print(f'✅ Deleted file: {full_path}')
        deleted_count += 1
        deleted_list.append(f"file:{full_path}")
    else:
        print(f'❌ Failed to delete file: {full_path} - {r.status_code} - {r.text}')

def delete_folder(folder_path):
    global deleted_count

    try:
        contents = list_items(folder_path + '/')
    except requests.HTTPError as e:
        print(f'⚠️ Failed to list folder {folder_path}: {e}')
        return

    for item in contents:
        full_path = f"{folder_path}/{item['ObjectName']}"
        if item['IsDirectory']:
            delete_folder(full_path)
        else:
            delete_file(full_path)

    print(f'🗑️ Deleting folder: {folder_path}/')
    r = requests.delete(f'{BASE_URL}/{folder_path}/', headers=HEADERS)
    if r.status_code in (200, 204):
        print(f'✅ Deleted folder: {folder_path}/')
        deleted_count += 1
        deleted_list.append(f"folder:{folder_path}/")
    else:
        print(f'❌ Failed to delete folder: {folder_path}/ - {r.status_code} - {r.text}')

print('📦 Checking Bunny CDN for cleanup (folders and files)...')
items = list_items()
for item in items:
    last_changed_str = item['LastChanged']
    try:
        last_changed = datetime.strptime(last_changed_str, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        last_changed = datetime.strptime(last_changed_str, '%Y-%m-%dT%H:%M:%S')
    last_changed = last_changed.replace(tzinfo=timezone.utc)
    
    if last_changed < cutoff:
        if item['IsDirectory']:
            delete_folder(item['ObjectName'])
        else:
            delete_file(item['ObjectName'])

# Webhook message
if deleted_count > 0:
    summary = f'Successfully deleted {deleted_count} item(s)'
    folders = [item.split(':', 1)[1] for item in deleted_list if item.startswith('folder:')]
    files = [item.split(':', 1)[1] for item in deleted_list if item.startswith('file:')]

    embed = {
        "title": "Bunny CDN Cleanup Report",
        "description": summary,
        "color": 3066993,
        "fields": [],
        "footer": {"text": "Bunny CDN Cleanup"}
    }

    if folders:
        embed["fields"].append({"name": "Deleted Folders", "value": ", ".join(folders), "inline": False})
    if files:
        embed["fields"].append({"name": "Deleted Files", "value": ", ".join(files), "inline": False})

    embed["fields"].append({"name": "Total Deleted", "value": str(deleted_count), "inline": True})
else:
    summary = 'No items older than 30 days were found.'
    embed = {
        "title": "Bunny CDN Cleanup Report",
        "description": summary,
        "color": 16776960,
        "fields": [{"name": "Action Taken", "value": "No folders or files were deleted.", "inline": False}],
        "footer": {"text": "Bunny CDN Cleanup"}
    }

print('\n' + summary)

try:
    requests.post(WEBHOOK_URL, json={"embeds": [embed]})
except Exception as e:
    print(f'⚠️ Failed to send Discord webhook: {e}')
