import sys
# import requests
import os
import calendar
import logging.config
import traceback
import subprocess
import shutil
from datetime import datetime, timezone
from plexapi.server import PlexServer
from plexapi.playlist import Playlist
import argparse
from typing import NoReturn
import json

if os.name == 'nt':  # sys.platform == 'win32':
    import win32file
import time
from alive_progress.styles import showtime
from src.util.PlexOps import PlexOps
from src.enum.LibraryName import LibraryName
from src.enum.LibraryType import LibraryType


def main():

    host = ""
    port = ""
    token = ""

    baseurl = 'http://% s:% s' % (host,port)
    # plex_server = PlexServer(baseurl, token)

    plex_ops = PlexOps(LibraryType.MUSIC,LibraryName.MUSIC)
    # plex_ops.poll(20,516,5)
    plex_ops.create_library()
    return

    parser = argparse.ArgumentParser(description='Plex helper')
    parser.add_argument('request', metavar='Request', type=str, nargs='?',
                        help='Supported requests: (init, delete_playlist, create_playlist, create_library, delete_library)')
    parser.add_argument('-i', '--items', metavar='Items', type=str, nargs='?',
                        help='Items to be passed for the request wrapped in double quotes and separated by comma i.e create_playlist --items "jazz classics,ambient"')
    parser.add_argument('-host', '--host', metavar='Host', type=str, nargs='?',
                        help='Plex server host, default is localhost', default="localhost")
    parser.add_argument('-p','--port', metavar='Port', type=str, nargs='?',
                        help='Plex server port, default is 32400', default="32400")
    parser.add_argument('-t', '--token', metavar='Token', type=str, nargs='?',
                        help='To retreive token: Open server and click hamburger menu of any movie, then Get Info and View XML, token at the end of URL')
    parser.add_argument('-d','--drive_letter', metavar='Drive Letter', type=str, nargs='?',
                        help='Drive letter, default is f', default="f")
    parser.add_argument('-music','--music_location', metavar='Music Location', type=str, nargs='?',
                        help='Path to music folder without drive letter, default is media'+os.sep+"music", default="media"+os.sep+"music")
    parser.add_argument('-movies','--movies_location', metavar='Movies Location', type=str, nargs='?',
                        help='Path to movies folder without drive letter, default is media'+os.sep+"movies", default="media"+os.sep+"movies")
    parser.add_argument('-tv','--tv_location', metavar='TV Location', type=str, nargs='?',
                        help='Path to tv folder without drive letter, default is media'+os.sep+"tv", default="media"+os.sep+"tv")
    parser.add_argument('-music_playlist','--music_playlist_file_location', metavar='Music Playlist File Location', type=str, nargs='?',
                        help='Path to music playlist file without drive letter, default is plexutil'+os.sep+"music-playlists.json", default="plexutil"+os.sep+"music-playlists.json")

    args = parser.parse_args()

    if args.request is None:
        raise ValueError("Positional argument (request) expected but none supplied, see -h")

    request = args.request.lower()
    items = []
    if args.items is not None:
        items = [x for x in args.items.split(",")]
    host = args.host
    port = args.port
    token = args.token
    drive_letter = args.drive_letter.upper()
    music_location = drive_letter+":"+os.sep+args.music_location
    movies_location = drive_letter+":"+os.sep+args.movies_location
    tv_location = drive_letter+":"+os.sep+args.tv_location
    music_playlist_file_location = drive_letter+":"+os.sep+args.music_playlist_file_location.replace("_",os.sep)

    if not drive_letter_exists(drive_letter):
        raise FileNotFoundError("Supplied drive letter: " + drive_letter + " - does not exist")

    #check if locations provided exist
    directories_to_check = [{"music":music_location},{"movies":movies_location},{"tv":tv_location},{"Music Playlists File":music_playlist_file_location}]
    for directories in directories_to_check:
        for directory_name, location in directories.items():
            if not os.path.exists(location):
                raise FileNotFoundError(directory_name + " - path does not exist: "+ location)

    baseurl = 'http://% s:% s' % (host,port)
    plex = PlexServer(baseurl, token)

    if (request == "init"):
        deleteLibrary(plex,deleteAll=True)
        createLibrary(plex, 'Movies', 'movie', "tv.plex.agents.movie","Plex Movie",movies_location)
        createLibrary(plex, 'TV Shows', 'show', "tv.plex.agents.series","Plex TV Series",tv_location)
        createLibrary(plex, 'Music', 'music', "tv.plex.agents.music","Plex Music",music_location,music_playlist_file_location=music_playlist_file_location)
        deletePlaylist(plex, deleteAll=True)
        createPlaylist(plex,music_location, music_playlist_file_location)
    elif (request == "delete_playlist"):
        deletePlaylist(plex,items)
    elif (request == "create_playlist"):
        createPlaylist(plex,music_location, music_playlist_file_location,items)
    elif (request == "delete_library"):
        deleteLibrary(plex,items)
    elif (request == "create_library"):
        for item in items:
            if item == "movies":
                createLibrary(plex, 'Movies', 'movie', "tv.plex.agents.movie","Plex Movie",movies_location)
            elif item == "tv shows":
                createLibrary(plex, 'TV Shows', 'show', "tv.plex.agents.series","Plex TV Series",tv_location)
            elif item == "music":
                createLibrary(plex, 'Music', 'music', "tv.plex.agents.music","Plex Music",music_location,music_playlist_file_location=music_playlist_file_location)
            else:
                raise ValueError("Requested to create unsupported library: " + item)


# def deleteLibrary(plex: PlexServer, libraryNames: [str] = [], deleteAll: bool = False) -> None:
#
#     if (deleteAll):
#         [x.delete() for x in plex.library.sections()]
#     else:
#         for section in libraryNames:
#             sectionSearch = plex.library.section(section)
#             if (sectionSearch):
#                 sectionSearch.delete()
#
# def createLibrary(plex: PlexServer, libraryName: str, type: str, agent: str, scanner: str, location: str, language: str = "en-US",music_playlist_file_location: str = "") -> None:
#
#     if type == "music":
#         part = (f'/library/sections?name=Music&type=music&agent=tv.plex.agents.music'
#                 f'&scanner=Plex%20Music&language=en-US&importFromiTunes=&enableAutoPhotoTags=&location=F%3A%5Cmedia%5Cmusic&prefs%5BrespectTags%5D=1&prefs%5BaugmentWithSharedContent%5D=0&prefs%5BartistBios%5D=0&prefs%5BalbumReviews%5D=0&prefs%5BpopularTracks%5D=0&prefs%5Bgenres%5D=2&prefs%5BalbumPosters%5D=3&')
#
#         plex._server.query(part,method=plex._session.post)
#
#         track_count = 0
#         with open(music_playlist_file_location,encoding='utf-8') as file:
#             fileDict = json.load(file)
#             track_count = fileDict.get("trackCount")
#
#         attempts = 0
#         print("Waiting for Plex to build Music library")
#         while(True):
#             attempts = attempts+1
#             if attempts > 100:
#                 raise ValueError("Plex could not build Music library")
#             print("===================")
#             print("Attempt {}/{}".format(str(attempts),"100"))
#             print("Expected track count: " + str(track_count))
#             print("Current track count: " + str(len(plex.library.section(libraryName).searchTracks())))
#             if len(plex.library.section(libraryName).searchTracks()) == track_count:
#                 print("Music library built successfully")
#                 break
#             time.sleep(20)
#
#     elif type == "movie":
#         plex.library.add(name=libraryName, type=type,agent=agent,scanner=scanner, location=location,language=language)
#         plex.library.sections()
#         plex.library.section(libraryName).editAdvanced(hidden=0, enableCinemaTrailers=1, country="US", originalTitles=0, localizedArtwork=1, useLocalAssets=1, respectTags=0, useExternalExtras=1, skipNonTrailerExtras=0, useRedbandTrailers=0, includeExtrasWithLocalizedSubtitles=0, includeAdultContent=0, autoCollectionThreshold=0, enableBIFGeneration=1, augmentWithProviderContent=1, collectionMode=2)
#     elif type == "show":
#         plex.library.add(name=libraryName, type=type,agent=agent,scanner=scanner, location=location,language=language)
#         plex.library.sections()
#         plex.library.section(libraryName).editAdvanced(hidden=0, episodeSort="0", country="US", showOrdering="aired", useSeasonTitles=0, originalTitles=1, localizedArtwork=1, useLocalAssets=1, respectTags=0, useExternalExtras=1, skipNonTrailerExtras=0, useRedbandTrailers=0, includeExtrasWithLocalizedSubtitles=0, includeAdultContent=0, enableBIFGeneration=1, augmentWithProviderContent=1, flattenSeasons=0)
#         #This sets languageOverride to es-ES for spanish shows
#         #These are tvdb ids
#         shows_es = [327417,396583,388477,292262,282670,274522]
#         found_shows_es = []
#
#         attempts = 0
#         print("Waiting for es-ES shows to become available")
#         while(True):
#             attempts = attempts+1
#             if attempts > 100:
#                 raise ValueError("Plex could not populate es-ES shows")
#             shows_found = 0
#             for show in plex.library.section(libraryName).all():
#                 guids = show.guids
#                 for guid in guids:
#                     if "tvdb://" in guid.id:
#                         tvdb = guid.id.replace("tvdb://","")
#                         if int(tvdb) in shows_es:
#                             shows_found = shows_found + 1
#
#             print("===================")
#             print("Attempt {}/{}".format(str(attempts),"100"))
#             print("Expected es-ES show count: " + str(len(shows_es)))
#             print("Current es-ES show count: " + str(shows_found))
#             if shows_found == len(shows_es):
#                 print("es-ES shows ready, proceeding to update metadata")
#                 break
#             time.sleep(20)
#
#         for show in plex.library.section(libraryName).all():
#             guids = show.guids
#             for guid in guids:
#                 if "tvdb://" in guid.id:
#                     tvdb = guid.id.replace("tvdb://","")
#                     if int(tvdb) in shows_es:
#                         found_shows_es.append(show)
#
#         for found_show_es in found_shows_es:
#             found_show_es.editAdvanced(languageOverride="es-ES")
#         plex.library.section(libraryName).refresh()
#
#     else:
#         raise ValueError("Library type: "+"\'"+type+"\' not supported")
#
#
# def deletePlaylist(plex: PlexServer, playlistNames: [str] = [], deleteAll: bool = False) -> None:
#
#     if (deleteAll):
#         [x.delete() for x in plex.playlists(playlistType="audio")]
#     else:
#         for playlist in plex.playlists(playlistType="audio"):
#             if (playlist.title in playlistNames):
#                 playlist.delete()
#
#
# def createPlaylist(plex: PlexServer, music_location:str, playlistManifestLocation: str, playlistNames: [str] = []) -> None:
#
#     tracks = plex.library.section("Music").searchTracks()
#     tracksFileNameDict = dict()
#
#     for track in tracks:
#         location = track.locations[0]
#         fileName = location.replace(music_location+os.sep,"")
#         tracksFileNameDict[fileName] = track
#     
#
#     with open(playlistManifestLocation,encoding='utf-8') as file:
#         fileDict = json.load(file)
#         playlists = fileDict.get("playlists")
#
#         for playlist in playlists:
#
#             playlistName = playlist.get("playlistName")
#             songs = playlist.get("songs")
#
#             if (playlistNames and playlistName not in playlistNames):
#                 continue
#
#             plexPlaylist = []
#
#             for song in songs:
#                 fileName = song.get("fileName")
#
#                 if (tracksFileNameDict.get(fileName) is None):
#                     raise ValueError("File in music playlist: \'" + fileName + "\' does not exist in server")
#
#                 plexPlaylist.append(tracksFileNameDict.get(fileName))
#
#             plex.createPlaylist(title=playlistName, items=plexPlaylist)
#




if __name__ == '__main__':
    main()
