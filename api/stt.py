# -*- coding: utf-8 -*-

import subprocess
import sys
import json
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logger

def _remove_timestamps(transcription):
    lines = transcription.split("\n")
    cleaned_lines = [line.split("]  ", 1)[-1] if "]  " in line else line for line in lines]

    return "\n".join(cleaned_lines)


def transcribeAudio(files, options):
    logger.info(f"{transcribeAudio.__name__}: parameters: file path: {files}; options: {str(options)}")
    if not isinstance(files, list):
        return (f"No sound file received - {str(files)}")

    trascription = []
    for file in files:
        trascription.append(transcribeFile(file, options))

    return '\n'.join(trascription)

def transcribeFile(file, options):
    try:
        if len(file) < 1:
            raise Exception(f"No sound file received - {str(sys.argv)}")

        language = options.get('lang', 'en') if isinstance(options, dict) else 'en'
        output_format = options.get('output_type', 'txt') if isinstance(options, dict) else 'txt'
        model = options.get('model', 'tiny') if isinstance(options, dict) else 'tiny'

        cmd = f"""
        source ~/Projects/Python/whisper/bin/activate && \
        whisper {file} --model {model} --output_format txt --language {language} && \
        deactivate
        """

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, executable="/bin/bash")

        if result.returncode != 0:
            raise Exception(f"Error occurred: {result.stderr}")

        transcription = result.stdout.strip()
        return _remove_timestamps(transcription)

        # os.remove(file)
    except Exception as e:
        print(f"file name: {file}; Error: {type(e).__name__}; message: {str(e)}")

if __name__ == "__main__":
    if logger is None:
        print(f"{__name__} - logger is None")
        logger.init_logging(None, False)

    logger.debug(f"{__name__}: sys.argv: {str(sys.argv)}")
    if len(sys.argv) > 1:
        function_name = sys.argv[1] if sys.argv[1] else "transcribeAudio"
        logger.debug(f"{__name__}: function_name : {function_name}")
        func = globals().get(function_name)
        if callable(func):
            options = sys.argv[2] if len(sys.argv) > 2 else "{}"
            options = json.loads(options)
            files = sys.argv[3] if len(sys.argv) > 3 else "[]"
            files = json.loads(files)
            print(func(files, options))
        else:
            print(f"Error: {function_name} function not found!")
            logger.error(f"{__name__}: Error: {function_name} function not found!")
    else:
        logger.error(f"{__name__}: Error: Invalid or missing data!")
        print("Error: Invalid or missing data!")


