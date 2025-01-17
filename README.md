
## Passo 1: Criar o ambiente virtual

python3.13 -m venv nome_do_ambiente

## Passo 2: Ativar o ambiente

source nome_do_ambiente/bin/activate

## Passo 3 - seguir o restante do tutorial do documento



** oq isso faz ? vai criar um ambiente isolado dentro dessa pasta que vc criou, essas bibliotecas
1. Pré-requisitos
Certifique-se de que você possui:
    • Conta AWS ativa com permissões para os serviços: Transcribe, Lambda, EC2 e CloudWatch.
    • Python 3.x instalado no seu ambiente local.
    • AWS CLI configurado com suas credenciais. Configure com o comando:
aws configure
    • Um bucket S3 configurado para armazenar arquivos de áudio e transcrições.
    • Dependências Python necessárias. Instale-as com:
pip install boto3 pyaudio SpeechRecognition
    • Um Security Group configurado para as instâncias EC2.

2. Criar uma IAM Role
    1. No Console AWS, acesse IAM > Roles > Create Role.
    2. Escolha o tipo de entidade confiável como AWS Service e selecione Lambda.
    3. Anexe as seguintes permissões gerenciadas:
        ◦ AmazonEC2FullAccess
        ◦ AmazonS3FullAccess
        ◦ CloudWatchLogsFullAccess
        ◦ AmazonTranscribeFullAccess
    4. Dê um nome para a role, como VoiceEC2ManagerRole, e conclua.
Nota: Este tutorial utiliza permissões de acesso total (Full Access) para simplificação. Em projetos reais, sempre aplique a política de menor privilégio.

3. Criar um Bucket S3
    1. Acesse S3 > Create Bucket.
    2. Dê um nome único para o bucket (ex.: voice-ec2-manager).
    3. Escolha a região (ex.: us-east-1) e mantenha as configurações padrão.
    4. Clique em Create Bucket.

4. Configurar o Security Group
    1. No Console AWS, vá para EC2 > Security Groups.
    2. Crie ou edite um Security Group com as seguintes regras de entrada:
        ◦ Porta 22 (SSH) - Para conexões remotas (caso necessário).
        ◦ Porta 80 (HTTP) - Para acesso web (opcional).
    3. Salve e copie o ID do Security Group (ex.: sg-0abc123def4567890), pois ele será usado no código da Lambda.

5. Configurar a Função AWS Lambda
    1. No Console AWS, acesse Lambda > Create Function.
    2. Escolha Author from scratch e preencha:
        ◦ Nome: VoiceEC2Manager
        ◦ Runtime: Python 3.x
    3. Anexe a role criada anteriormente (VoiceEC2ManagerRole) à função Lambda.
    4. Substitua o código padrão pela função Lambda abaixo:

import boto3
import json

## Clientes da AWS para interagir com os serviços EC2 e S3
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')

## Configuração padrão
AMI_ID = 'ami-09115b7bffbe3c5e4'  # ID da AMI para Amazon Linux 2023
INSTANCE_TYPE = 't2.micro'  # Tipo de instância padrão
SSH_KEY_NAME = 'SUA_CHAVE_SSH'  # Nome da chave SSH configurada na AWS
SECURITY_GROUP_ID = 'SEU_GRUPO_DE_SEGURANCA'  # ID do grupo de segurança associado às instâncias

## Palavras-chave para identificar ações nos comandos de voz
CREATE_KEYWORDS = ['criar', 'crie', 'lançar', 'lance']  # Comandos para criar instâncias
DELETE_KEYWORDS = ['deletar', 'delete', 'terminar', 'termine', 'finalizar', 'finalize']  # Comandos para deletar instâncias

def get_s3_transcription(event):
    """
    Obtém a transcrição de um arquivo armazenado no S3.
    
    Args:
        event: Dados do evento do S3 que acionaram a função Lambda.
    
    Returns:
        A transcrição extraída do arquivo JSON gerado pelo Amazon Transcribe.
    """
    bucket_name = event['Records'][0]['s3']['bucket']['name']  # Nome do bucket S3
    file_key = event['Records'][0]['s3']['object']['key']  # Nome do arquivo no bucket
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)  # Faz o download do arquivo
    transcription_data = json.loads(response['Body'].read().decode('utf-8'))  # Carrega o conteúdo do JSON
    return transcription_data['results']['transcripts'][0]['transcript']  # Retorna o texto transcrito

def get_vpc_and_subnet_ids():
    """
    Obtém o ID da VPC e de uma sub-rede associada.
    
    Returns:
        Tuple contendo o ID da VPC e o ID da sub-rede.
    """
    vpcs = ec2_client.describe_vpcs()  # Lista todas as VPCs
    vpc_id = vpcs['Vpcs'][0]['VpcId']  # Seleciona a primeira VPC encontrada
    
    subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])  # Filtra sub-redes da VPC
    subnet_id = subnets['Subnets'][0]['SubnetId']  # Seleciona a primeira sub-rede encontrada
    
    return vpc_id, subnet_id

def create_instance(subnet_id):
    """
    Cria uma instância EC2 com as configurações padrão.
    
    Args:
        subnet_id: ID da sub-rede onde a instância será criada.
    """
    ec2_client.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        MinCount=1,  # Número mínimo de instâncias a lançar
        MaxCount=1,  # Número máximo de instâncias a lançar
        SecurityGroupIds=[SECURITY_GROUP_ID],  # Grupo de segurança associado
        SubnetId=subnet_id,  # Sub-rede onde a instância será lançada
        KeyName=SSH_KEY_NAME,  # Chave SSH para acesso à instância
    )

def terminate_instances():
    """
    Finaliza todas as instâncias EC2 em execução na conta.
    """
    instances = ec2_client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]  # Filtra apenas instâncias em execução
    )
    instance_ids = [instance['InstanceId'] for reservation in instances['Reservations'] for instance in reservation['Instances']]  # Obtém os IDs das instâncias
    
    if instance_ids:
        ec2_client.terminate_instances(InstanceIds=instance_ids)  # Finaliza as instâncias encontradas

def lambda_handler(event, context):
    """
    Função Lambda que processa comandos de voz transcritos para gerenciar instâncias EC2.
    
    Args:
        event: Evento que acionou a função (geralmente relacionado ao S3).
        context: Informações sobre o ambiente de execução da função Lambda.
    
    Returns:
        Um dicionário com o status e a mensagem da operação realizada.
    """
    transcription = get_s3_transcription(event)  # Obtém a transcrição do comando de voz
    print(f"Received transcription: {transcription}")  # Loga a transcrição para debugging

    _, subnet_id = get_vpc_and_subnet_ids()  # Obtém IDs da VPC e sub-rede

    # Ação: criar instância
    if any(keyword in transcription for keyword in CREATE_KEYWORDS):  # Verifica se o comando pede para criar uma instância
        create_instance(subnet_id)
        return {"status": "success", "message": "Instance created with default AMI!"}

    # Ação: deletar instâncias
    elif any(keyword in transcription for keyword in DELETE_KEYWORDS):  # Verifica se o comando pede para deletar instâncias
        terminate_instances()
        return {"status": "success", "message": "All running instances have been terminated."}

    # Comando não reconhecido
    return {"status": "error", "message": "Unrecognized command."}

    5. Clique em Deploy para salvar a função.

6. Configurar o Evento do S3 para Disparar a Lambda
    1. No Console AWS, acesse o bucket S3 criado anteriormente.
    2. Vá para Properties > Event Notifications > Create Event Notification.
    3. Configure:
        ◦ Nome: TriggerLambda
        ◦ Evento: PUT (Upload de arquivos)
        ◦ Prefixo/Sufixo: .json
        ◦ Destination: Escolha a função Lambda criada (VoiceEC2Manager).
    4. Salve a configuração.

7. Executar o Script Localmente
Crie o script Python para capturar o áudio e interagir com o serviço S3 e Transcribe. Aqui está o código:

## Importação das bibliotecas necessárias
import speech_recognition as sr  	# Reconhecimento de fala
import boto3  				# AWS SDK para interagir com serviços AWS
import time  				# Manipulação de tempo
import json  				# Manipulação de dados JSON

## Inicializando os clientes da AWS
s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')
lambda_client = boto3.client('lambda')

bucket_name = "YOUR_BUCKET_NAME"  # Nome do bucket S3
region = "YOUR_REGION"  # Região AWS

## Função para gravar áudio
def record_audio(filename="audio.wav"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    with open(filename, "wb") as file:
        file.write(audio.get_wav_data())
    return filename

## Função para enviar o áudio para o S3
def upload_to_s3(filename, bucket_name):
    s3_client.upload_file(filename, bucket_name, filename)

## Função para iniciar a transcrição no Amazon Transcribe
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
    return job_name

## Função para verificar o status da transcrição
def check_transcription_status(job_name):
    response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
    status = response['TranscriptionJob']['TranscriptionJobStatus']
    
    if status == 'COMPLETED':
        return True
    elif status == 'FAILED':
        return False
    else:
        return False

## Fluxo principal
if __name__ == "__main__":
    audio_file = record_audio("audio.wav")
    upload_to_s3(audio_file, bucket_name)
    job_name = start_transcription_job(audio_file, bucket_name)
    
    while True:
        if check_transcription_status(job_name):
            break
        time.sleep(2) # Aguarda 2 segundos antes de verificar o status novamente

Para executar o script:
python voice_command.py
O áudio será capturado, enviado para o S3, processado pelo Amazon Transcribe e, uma vez que o arquivo JSON de transcrição for gerado, a função Lambda será acionada para gerenciar as instâncias EC2 com base nos comandos de voz.
Os logs de execução da função Lambda podem ser acessados no CloudWatch Logs.
