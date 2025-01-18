import lmnt
import wave
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from lmnt.api import Speech


LMNT_API_KEY = os.environ.get('LMNT_API_KEY')


async def generate_audio_file(text_to_synthetize, output_filepth='output.wav'):
    async with Speech(LMNT_API_KEY) as speech:
        synthesis = await speech.synthesize(
            text_to_synthetize, 
            voice='lily', 
            format='wav', 
            return_durations=True
        )
        with open(output_filepth, 'wb') as f:
            f.write(synthesis['audio'])

        duration = get_audio_duration(output_filepth)
            
        return duration, synthesis['durations']

def generate_audio_file_sync(text_to_synthesize, output_filepath='output.wav'):
    """
    Wrapper to call the asynchronous `generate_audio_file` function synchronously.
    Returns the duration of the generated audio in seconds.
    """
    async def wrapper():
        return await generate_audio_file(text_to_synthesize, output_filepath)
    
    return asyncio.run(wrapper())

def generate_audio_and_update_state(text, state, output_filepath='output.wav'):
    """
    Generates audio from text and updates the state dictionary with the audio file path and duration.
    
    Args:
        text (str): Text to synthesize into audio
        state (dict): State dictionary to update
        output_filepath (str): Path where the audio file will be saved
    
    Returns:
        dict: Updated state dictionary with audio_filepath and duration
    """
    try:
        duration, synthesis_durations = generate_audio_file_sync(text, output_filepath)
        state['audio_filepath'] = output_filepath
        state['audio_duration'] = duration
        state['synthesis_durations'] = synthesis_durations
        return state
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        state['audio_filepath'] = None
        state['audio_duration'] = None
        state['synthesis_durations'] = None
        return state

def get_audio_duration(audio_filepath):
    """
    Gets the duration of a WAV audio file in seconds.
    
    Args:
        audio_filepath (str): Path to the WAV file
        
    Returns:
        float: Duration of the audio in seconds
    """
    with wave.open(audio_filepath, 'rb') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
        return duration

if __name__ == '__main__':

    text_to_synthetize='''
        Swimming Marathon Champions: Elephants are not only excellent swimmers '''

    duration = generate_audio_file_sync(text_to_synthetize)

    print(duration)
