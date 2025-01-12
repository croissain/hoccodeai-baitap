from openai import OpenAI
import os
from os.path import dirname, join
from dotenv import load_dotenv
from pypdf import PdfReader
# from time import time

# CONSTANTS
CHUNK_SIZE = 2000
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"]
TARGET_LANGUAGE = "English"

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

OpenAI.api_key = os.getenv("LOCAL_API_KEY")

client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("LOCAL_API_KEY"))


def validate_file(file_path: str) -> tuple[bool, str]:
    """Validate the file path and extension"""
    if not os.path.exists(file_path):
        return False, f"File path '{file_path}' does not exist."

    if not file_path.endswith(tuple(SUPPORTED_EXTENSIONS)):
        return (
            False,
            f"File extension '{file_path.split('.')[-1]}' is not supported. Supported extensions are {', '.join(SUPPORTED_EXTENSIONS)}.",
        )

    return True, "Success"


def read_file(file_path: str) -> tuple[bool, str]:
    """Read content from file based on extension"""
    try:
        _, ext = os.path.splitext(file_path)

        if ext.lower() == ".pdf":
            with open(file_path, "rb") as file:
                pdf_reader = PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return True, text
        else:
            with open(file_path, "r", encoding="utf-8") as file:
                return True, file.read()
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str) -> bool:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)

        _, ext = os.path.splitext(file_path)

        if ext.lower() == ".pdf":
            print("Writing to PDF...")
        else:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

        print("File written successfully.")
        return True
    except Exception as e:
        print(f"Error writing file: {str(e)}")
        return False


def chunk_text(text) -> list[str]:
    """Split text into manageable chunks"""
    return [text[i : i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]


def translate_chunk(chunk: str) -> str:
    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            n=1,
            max_tokens=500,
            temperature=0.7,
            top_p=1,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful assistant that translates {TARGET_LANGUAGE}.",
                },
                {
                    "role": "user",
                    "content": f"Translate the following text into {TARGET_LANGUAGE}: {chunk}",
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error translating chunk: {str(e)}")
        return None


def main():
    try:
        while True:
            # Input file
            input_pdf_path = input("Path: ")
            if not input_pdf_path.strip():
                continue

            # Validate file
            is_valid, message = validate_file(input_pdf_path)
            if not is_valid:
                print(message)
                continue

            # Create output file path
            base_filename = os.path.basename(input_pdf_path)
            file_name, ext = os.path.splitext(base_filename)
            # output_path = join(dirname(__file__), f"{file_name}_translated{ext}")
            output_path = join(dirname(__file__), f"{file_name}_translated.txt")

            # Read file
            success, content = read_file(input_pdf_path)
            if not success:
                print(content)
                continue

            # Translate
            chunks = chunk_text(content)
            translated_chunks = []

            print("Translating...")
            for i, chunk in enumerate(chunks, 1):
                print(f"Chunks {i}/{len(chunks)} are translating...")
                translated = translate_chunk(chunk)
                if translated:
                    translated_chunks.append(translated)
                # time.sleep(1)  # Avoid rate limit

            # Write file
            if translate_chunk:
                write_file(output_path, "\n".join(translated_chunks))

    except KeyboardInterrupt:
        print("\nExiting...")
        exit()


if __name__ == "__main__":
    main()
