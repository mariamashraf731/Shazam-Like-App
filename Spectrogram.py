import librosa
from PIL import Image
from scipy import signal
from imagehash import hex_to_hash ,phash


class Spectrogram():

    @staticmethod 
    def Features(data, SamplingRate):       
        f, d, colorMesh = signal.spectrogram(data, fs=SamplingRate, window='hann')
        melspectro = librosa.feature.melspectrogram(data, sr=SamplingRate,S=colorMesh)
        mfccs = librosa.feature.mfcc(data.astype('float64'), sr=SamplingRate, S=colorMesh)
        chroma_stft = librosa.feature.chroma_stft(data, sr=SamplingRate, S=colorMesh)
        
        return [colorMesh,melspectro, mfccs, chroma_stft]

    @staticmethod
    def Hash(array):
        arr = Image.fromarray(array)
        hash = phash(arr, hash_size=16).__str__()
        return hash

    @staticmethod
    def getSimilarity(song1,song2):
        similarity = 1 - (hex_to_hash(song1) - hex_to_hash(song2))/256.0
        return similarity

    @staticmethod
    def create_dict(song_name, Hashes):
        song = {
            song_name: {
                "spectrogram_hash": Hashes[0],
                "melspectrogram": Hashes[1],
                "mfcc": Hashes[2],
                "chroma_stft": Hashes[3]
            }
        }
        return song

