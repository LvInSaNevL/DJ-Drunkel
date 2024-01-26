import youtube
import spotify

async def playlist(): 
    yt_counts = await youtube.get_playlist_len()
    sp_counts = await spotify.get_playlist_len()
    return f'''
We have {sp_counts} songs in the [Spotify Playlist](<https://open.spotify.com/playlist/7iAnRkjRC4RqbkzjeSRi85>)
And {yt_counts} songs in the [YouTube Playlist](https://www.youtube.com/playlist?list=PLRDuNIkwpnsdsAaytTIOtkaQGcsdy_fJH)
'''

def help():
    return f'''
* `>add [url]` adds the song to the appropriate playlist, you can only send one at a time for now unfortunately
* `>playlists` returns links to both playlists as well as how many songs are in each
* `>help` returns this message
* `>ping` pong
'''