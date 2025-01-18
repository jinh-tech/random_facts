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


def generate_audio_file_sync(text_to_synthesize, output_filepath='output.wav'):
    """
    Wrapper to call the asynchronous `generate_audio_file` function synchronously.
    """
    async def wrapper():
        await generate_audio_file(text_to_synthesize, output_filepath)
    
    asyncio.run(wrapper())

if __name__ == '__main__':

    text_to_synthetize='''
        Swimming Marathon Champions: Elephants are not only excellent swimmers 
        but can swim for an astonishing six hours straight! 
        Some have even been recorded traveling around 48 kilometers at a speed of 2.1 kilometers per hour.'''

    generate_audio_file_sync(text_to_synthetize)

