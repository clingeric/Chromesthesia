# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import spotipy
import spotipy.oauth2 as oauth2
import requests
from pydub import AudioSegment
import numpy as np
import os
import scipy.io.wavfile as wav
import scipy.fftpack as fft

def index(request):
    return render(request, 'home/index.html')

def meat(artist): 
    credentials = oauth2.SpotifyClientCredentials(
        client_id='c6bbc479081f433d9dd08ba3734b6077',
        client_secret='c1bc5f13ac9a421eb1ecae345ceb959c')

    token = credentials.get_access_token()
    spotify = spotipy.Spotify(auth=token)

    artist_input = artist
    results = spotify.search(q='artist:' + artist_input, type='artist')
    artist_uri = results['artists']['items'][0]['uri'].split(":")[2]

    results = spotify.artist_top_tracks(artist_uri)

    songs = []

    for track in results['tracks'][:5]:
        preview_url = track['preview_url'].replace("https://", "http://", 1) + ".mp3"
        r = requests.get(preview_url, allow_redirects=True)
        open(track['name'] + '.mp3', 'wb').write(r.content)
        songMp3 = AudioSegment.from_mp3(track['name'] + '.mp3').set_channels(1)
        os.remove(track['name'] + '.mp3')
        songMp3.export(track['name'] + '.wav', format="wav")
        import_rate, import_data = wav.read(track['name'] + '.wav')
        os.remove(track['name'] + '.wav')
        avg_freq = average_frequency(import_rate * 1.0, import_data)
        print(avg_freq)
        songs.append(avg_freq)
    # context = {'songs': songs}
    return songs

def average_frequency(rate, data):
    sample_length = len(data)
    print('sample_length')
    print(sample_length)
    k = np.arange(sample_length)
    print('k')
    print(k)
    period = sample_length / rate
    print('period')
    print(period)
    freqs = (k / period)[range(sample_length // 2)] #right-side frequency range
    print('freqs')
    print(freqs)
    fourier = abs(fft.fft(data * np.hanning(sample_length)) / sample_length)[range(sample_length / 2)] #normalize & clip to right side
    print('fourier')
    print(fourier)
    power = np.power(fourier, 2.0)
    print('power')
    print(power)
    print('result')
    print(sum(power * freqs) / sum(power))
    return sum(power * freqs) / sum(power)

def freq(request):
    songs = meat('deadmau5')
    context = {'songs': songs}
    return render(request, 'home/freq.html', context)