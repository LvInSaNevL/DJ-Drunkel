# File imports
import youtube
import spotify
import utils
# Dep imports

def getSPLinks():
    ytData = youtube.get_playlist_items()
    for s in ytData:
        yt_title = s["snippet"]["title"]
        yt_artist = s["snippet"]["videoOwnerChannelTitle"]
        songFilters = ["(Official Music Video)",
                "(Lyric Video)",
                "(Official Video)"]
        for sF in songFilters:
            yt_title = yt_title.replace(sF, "")
        artistFilters = [" - Topic",
                         "(Official)",
                         "VEVO"]
        for aF in artistFilters:
            yt_artist = yt_artist.replace(aF, "")
        spotify.search(yt_title, yt_artist)

# Actual start
if __name__ == "__main__":
    # spotify.get_song_info("4rb0AyzxYLeg4p0fXxrhAm")
    getSPLinks()