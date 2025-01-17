import speech_recognition as sr
import boto3
import time
import json

s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')
lambda_client = boto3.client('lambda')  
bucket_name = "projeto-voz"  
region = "us-east-1"  # Example: us-east-1

def record_audio(filename="audio.wav"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Recording... Speak something.")
        audio = recognizer.listen(source)

    with open(filename, "wb") as file:
        file.write(audio.get_wav_data())
    print(f"Audio recorded and saved as {filename}.")
    return filename

def upload_to_s3(filename, bucket_name):
    s3_client.upload_file(filename, bucket_name, filename)
    print(f"File {filename} uploaded to S3.")

def start_transcription_job(filename, bucket_name):
    job_name = f"transcription-job-{int(time.time())}"
    media_uri = f"s3://{bucket_name}/{filename}"
    
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        LanguageCode='pt-BR',
        Media={'MediaFileUri': media_uri},
        MediaFormat='wav',
        OutputBucketName=bucket_name
    )
    print(f"Transcription job started for the file {filename}.")
    return job_name

def check_transcription_status(job_name):
    response = transcribe_client.get_transcription_job(
        TranscriptionJobName=job_name
    )
    
    status = response['TranscriptionJob']['TranscriptionJobStatus']
    if status == 'COMPLETED':
        print("Transcription completed!")
        return True  
    elif status == 'FAILED':
        print("Transcription failed.")
        return False  
    else:
        print("Transcription still in progress...")
        return False  

if __name__ == "__main__":
    audio_file = record_audio("audio.wav")
    
    upload_to_s3(audio_file, bucket_name)
    
    job_name = start_transcription_job(audio_file, bucket_name)
    
    while True:
        if check_transcription_status(job_name):
            break  
        time.sleep(2)
