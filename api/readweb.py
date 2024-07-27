# -*- coding: utf-8 -*-

import os
import sys
import requests
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logger
import json

def readweb(url=None):
    if url is None:
        return "Error: No URL provided."

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        response = session.get(url, allow_redirects=True)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error: {e}"

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup.find():  # Check if BeautifulSoup found any tags
            return f"Error: Content is not valid HTML. {response.headers.get('Content-Type', '')}"

    except Exception as e:
        return f"Error: Failed to parse HTML - {e}"

    for script_or_style in soup(['script', 'style', 'noscript']):
        script_or_style.extract()

    text = soup.get_text(separator="\n")

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    text = ''.join([c if 32 <= ord(c) <= 126 else 's' for c in text])

    return text

if __name__ == "__main__":
    logger.debug(f"{os.path.basename(__file__)}: sys.argv: {str(sys.argv)}")
    if len(sys.argv) < 3:
        print("Error: Insufficient arguments provided.")
    else:
        function_name = sys.argv[1]
        try:
            post_data = json.loads(sys.argv[2])
            url = post_data.get("resource")
            if not url:
                print("Error: Invalid URL")
            else:
                print(readweb(url))
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON - {e}")
