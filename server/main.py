from pathlib import Path
import boto3

from typing import BinaryIO
from openai import OpenAI
import docx
import logging
from uuid  import uuid4
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()


logger = logging.getLogger(__name__)

try:
    import magic
except Exception as e:
    logger.exception(f"Failed to initialize libmagic: {str(e)}")

try:
    client = OpenAI()
except Exception as e:
    logger.exception(f"Failed to initialize openai client: {str(e)}")


def get_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def get_text_from_pdf(file_path: str) -> str:
    raise NotImplementedError()

def get_audio_for_text(input_text: str) -> str:
    # TODO: Name based on first few words
    # file_name = input_text[:40]
    speech_file_path = Path(__file__).parent / str(uuid4()) / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=input_text
    )

    response.stream_to_file(speech_file_path)
    return speech_file_path

def upload_file_to_bucket():
    raise NotImplementedError()
    ...

def get_file_type_for_file(uploaded_file: BinaryIO) -> str:
    mime = magic.Magic(mime=True)
    return mime.from_file(uploaded_file) # TODO: path?

def get_signed_url_for_file_path(file_path: str) -> str:
    raise NotImplementedError()


def upload_file_to_s3(file_name: str, bucket: str, object_name: str|None=None) -> bool:
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified, file_name is used
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        logger.debug(response)
    except Exception:
        logger.exception("Failed to upload to s3")
        return False
    return True


def get_audio_file_for_upload(upload_file: UploadFile):
    """
    1. (optional)  Upload input file to storage bucket
    2. Infer file type (python magic)
    3. use correct library for file type to extract text  from  the file (PDF or doc)
    4. get audio from  text
    """
    # TODO:
    # uploaded_path = upload_file_to_bucket(upload_file)
    # logger.info(f"Uploaded file to path {uploaded_path}.")
    # seek(0)
    try:
        file_type = get_file_type_for_file(uploaded_file=upload_file.file)
    except Exception:
        logger.exception("Couldn't infer file type. Defaulting to docx.")
        file_type = "docx"
    logger.info(f"Inferred file type:  {file_type}.")

    if not (file_type == "docx" or file_type  == "pdf"):
        raise ValueError()
    input_text = None
    if file_type == 'docx':
        input_text = get_text_from_docx(upload_file.file)
    elif file_type ==  'pdf':
        input_text = get_text_from_pdf(upload_file.file)
    if not input_text:
        raise ValueError()
    logger.info("Dictating the following: "+input_text[:200]+"...")
    speech_path = get_audio_for_text(input_text)
    logger.info(f"Saved audio to {speech_path}")
    # TODO
    # uploaded_speech_path = None
    # with open(speech_path, 'rb') as speech_file:
    #     uploaded_speech_path = upload_file_to_bucket(speech_file)
    # logger.info(f"Uploaded audio to {speech_path}")
    # signed_url = get_signed_url_for_file_path(uploaded_speech_path)
    # logger.info(f"Signed URL of speech path: {signed_url}")
    # return signed_url
    return FileResponse(path=speech_path, filename=upload_file.filename, media_type='audio/mpeg')


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    logger.info("Uploaded file", extra={"filename": file.filename})
    signed_url = get_audio_file_for_upload(file)
    content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Upload File</title>
</head>
<body>
<form action="/uploadfile/" enctype="multipart/form-data" method="post">
    <input type="file" name="file">
    <input type="submit">
</form>
<a href="{signed_url}">Uploaded file: {signed_url}</a>
</body>
</html>
    '''
    return HTMLResponse(content=content)

@app.get("/")
async def main():
    content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Upload File</title>
</head>
<body>
<form action="/uploadfile/" enctype="multipart/form-data" method="post">
    <input type="file" name="file">
    <input type="submit">
</form>
</body>
</html>
    '''
    return HTMLResponse(content=content)


if __name__ == '__main__':
    main()
