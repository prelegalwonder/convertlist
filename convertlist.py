#!/usr/bin/env python3

import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from plexapi.server import PlexServer
from plexapi.playlist import Playlist
from plexapi.exceptions import Unauthorized
from dotenv import load_dotenv
import requests
from typing import List, Dict, Optional
import argparse

# Load environment variables
load_dotenv()

class SpotifyToPlexampConverter:
    def __init__(self, spotify_client_id=None, spotify_client_secret=None, spotify_redirect_uri=None,
                 plex_url=None, plex_token=None):
        # Initialize Spotify client
        self.spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=spotify_client_id or os.getenv('SPOTIPY_CLIENT_ID'),
            client_secret=spotify_client_secret or os.getenv('SPOTIPY_CLIENT_SECRET'),
            redirect_uri=spotify_redirect_uri or os.getenv('SPOTIPY_REDIRECT_URI'),
            scope='playlist-read-private playlist-read-collaborative'
        ))
        
        # Initialize Plex client
        plex_url = plex_url or os.getenv('PLEX_URL')
        plex_token = plex_token or os.getenv('PLEX_TOKEN')
        
        if not plex_url:
            raise ValueError("Plex server URL is required. Set PLEX_URL environment variable or use --plex-url argument.")
        if not plex_token:
            raise ValueError("Plex token is required. Set PLEX_TOKEN environment variable or use --plex-token argument.")
        
        try:
            self.plex = PlexServer(plex_url, plex_token)
            # Test the connection
            self.plex.library.sections()
        except Unauthorized:
            raise ValueError("Invalid Plex token. Please check your token and try again.")
        except Exception as e:
            raise ValueError(f"Failed to connect to Plex server: {str(e)}")

    def get_playlist_tracks(self, playlist_url: str) -> List[Dict]:
        """Fetch tracks from a Spotify playlist."""
        playlist_id = self._extract_playlist_id(playlist_url)
        results = self.spotify_client.playlist_tracks(playlist_id)
        tracks = results['items']
        
        while results['next']:
            results = self.spotify_client.next(results)
            tracks.extend(results['items'])
            
        return tracks

    def _extract_playlist_id(self, url: str) -> str:
        """Extract playlist ID from Spotify URL."""
        # Handle different URL formats
        if 'spotify:playlist:' in url:
            return url.split('spotify:playlist:')[1]
        elif 'open.spotify.com/playlist/' in url:
            return url.split('playlist/')[1].split('?')[0]
        else:
            raise ValueError("Invalid Spotify playlist URL")

    def _search_plex_track(self, track: Dict) -> Optional[Dict]:
        """Search for a track in Plex library."""
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        
        # Search in Plex library
        results = self.plex.library.search(
            title=track_name,
            libtype='track',
            limit=1
        )
        
        if results:
            return results[0]
        return None

    def create_plexamp_playlist(self, tracks: List[Dict], playlist_name: str) -> Optional[Playlist]:
        """Create a new playlist in Plexamp."""
        # Get all music sections from Plex
        music_sections = [section for section in self.plex.library.sections() if section.type == 'artist']
        
        if not music_sections:
            raise ValueError("No music library found in Plex")
        
        # Find matching tracks in Plex
        plex_tracks = []
        for track in tracks:
            plex_track = self._search_plex_track(track)
            if plex_track:
                plex_tracks.append(plex_track)
        
        if not plex_tracks:
            raise ValueError("No matching tracks found in Plex library")
        
        # Create the playlist
        try:
            playlist = self.plex.createPlaylist(
                title=playlist_name,
                items=plex_tracks
            )
            return playlist
        except Exception as e:
            print(f"Error creating playlist: {str(e)}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Convert Spotify playlists to Plexamp playlists')
    
    # Spotify arguments
    parser.add_argument('--spotify-client-id', help='Spotify Client ID')
    parser.add_argument('--spotify-client-secret', help='Spotify Client Secret')
    parser.add_argument('--spotify-redirect-uri', help='Spotify Redirect URI')
    
    # Plex arguments
    parser.add_argument('--plex-url', help='Plex Server URL')
    parser.add_argument('--plex-token', help='Plex Authentication Token')
    
    # Required arguments
    parser.add_argument('playlist_url', help='Spotify playlist URL')
    parser.add_argument('playlist_name', help='Name for the new Plexamp playlist')
    
    args = parser.parse_args()
    
    try:
        converter = SpotifyToPlexampConverter(
            spotify_client_id=args.spotify_client_id,
            spotify_client_secret=args.spotify_client_secret,
            spotify_redirect_uri=args.spotify_redirect_uri,
            plex_url=args.plex_url,
            plex_token=args.plex_token
        )
        
        tracks = converter.get_playlist_tracks(args.playlist_url)
        playlist = converter.create_plexamp_playlist(tracks, args.playlist_name)
        if playlist:
            print(f"Playlist '{args.playlist_name}' created successfully with {len(playlist.items())} tracks!")
        else:
            print("Failed to create playlist")
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your Plex token is valid and not expired")
        print("2. Verify your Plex server URL is correct")
        print("3. Check that your Plex server is accessible")
        print("4. Ensure you have the necessary permissions on your Plex server")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
