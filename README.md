# Spotify to Plexamp Playlist Converter

This Python script allows you to convert Spotify playlists to Plexamp playlists. It fetches tracks from a Spotify playlist and creates a matching playlist in Plexamp with the tracks that exist in your Plex library.

## Prerequisites

- Python 3.6 or higher
- A Spotify Developer account
- A Plex Media Server with a music library
- Plexamp installed and configured

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/convertlist.git
cd convertlist
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` with your credentials (see Configuration section below)

## Configuration

### Spotify Setup

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Note down your Client ID and Client Secret
4. Add `http://localhost:8888/callback` to your Redirect URIs
   - This must match exactly what you set in your `.env` file
   - If you change it in one place, change it in both

### Plex Setup

1. Get your Plex token:
   - Go to https://app.plex.tv/desktop
   - Sign in to your account
   - Press F12 to open Developer Tools
   - Go to the "Application" tab
   - Look for "Local Storage" on the left
   - Click on "plex.tv"
   - Find the "myPlexAccessToken" key
   - Copy its value - this is your Plex token

2. Note your Plex Media Server URL:
   - This should be the URL of your Plex Media Server (not Plexamp)
   - For local servers: `http://your-plex-server:32400`
   - For remote servers: Use the full URL provided by Plex
   - You can find this in your Plex Media Server settings under "Network"

### Environment Variables

Create a `.env` file with the following variables:
```
# Spotify API credentials
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

# Plex credentials
PLEX_URL=http://your-plex-server:32400  # Your Plex Media Server URL
PLEX_TOKEN=your_plex_token
```

## Usage

You can use the script in two ways:

### 1. Using Environment Variables

If you've set up your `.env` file, you can run the script with just the required arguments:

```bash
python convertlist.py "https://open.spotify.com/playlist/your-playlist-id" "My Plexamp Playlist"
```

### 2. Using Command Line Arguments

You can also provide all credentials via command line:

```bash
python convertlist.py \
  --spotify-client-id your_client_id \
  --spotify-client-secret your_client_secret \
  --spotify-redirect-uri http://localhost:8888/callback \
  --plex-url http://your-plex-server:32400 \
  --plex-token your_plex_token \
  "https://open.spotify.com/playlist/your-playlist-id" \
  "My Plexamp Playlist"
```

## How It Works

1. The script authenticates with both Spotify and Plex Media Server
2. It fetches all tracks from the specified Spotify playlist
3. For each track, it searches your Plex Media Server library for a matching track
4. It creates a new playlist in your Plex Media Server, which will be available in Plexamp

## Notes

- The script will only include tracks that exist in your Plex Media Server library
- Track matching is based on track title, which might not be perfect
- The script requires both Spotify and Plex Media Server authentication to work
- Make sure your Plex Media Server is accessible and has a music library set up
- The created playlist will be available in Plexamp as it syncs with your Plex Media Server

## Troubleshooting

- If you get authentication errors, verify your credentials in the `.env` file
- If tracks aren't being found, check that your Plex Media Server music library is properly indexed
- If the playlist isn't created, verify that your Plex token has the necessary permissions
- If you can't connect to your Plex Media Server, verify the URL is correct and the server is accessible
- If you get a "No redirect_uri" error, make sure SPOTIPY_REDIRECT_URI is set in your environment variables and matches exactly what's in your Spotify Developer Dashboard
- If you get an "unauthorized" error, your Plex token might be invalid or expired. Get a new token following the instructions above.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 