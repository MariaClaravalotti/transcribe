# Gerenciamento de EC2 Controlado por Voz

Este projeto permite gerenciar instâncias EC2 na AWS utilizando comandos de voz. Ele combina serviços da AWS, como Lambda, Transcribe e EC2, com tecnologias Python para processamento de áudio e comandos.

---

## 🚀 **Visão Geral**

O projeto usa comandos de voz para realizar operações em instâncias EC2, como iniciar, parar e listar instâncias. O fluxo do projeto inclui:

1. **Entrada de voz:** Captação de áudio via microfone.
2. **Processamento de áudio:** Envio do áudio para um bucket S3.
3. **Transcrição:** Uso do Amazon Transcribe para transformar o áudio em texto.
4. **Execução de comandos:** Análise da transcrição e realização de operações EC2 via Lambda.

---

## 🛠 **Recursos Utilizados**

### **AWS Services**
- **Amazon EC2:** Gerenciamento de instâncias.
- **Amazon S3:** Armazenamento de arquivos de áudio e resultados de transcrição.
- **Amazon Transcribe:** Conversão de áudio em texto.
- **AWS Lambda:** Execução de lógica backend.
- **CloudWatch:** Monitoramento e logging.

### **Tecnologias**
- **Python 3.13:** Linguagem principal do projeto.
- **Bibliotecas Python:**
  - `boto3`: Integração com a AWS.
  - `pyaudio`: Gravação de áudio.
  - `SpeechRecognition`: Processamento de voz local.

---

## ⚙️ **Configuração Inicial**

### **1. Pré-requisitos**
- Conta AWS com permissões para EC2, S3, Transcribe e Lambda.
- AWS CLI configurado com suas credenciais.
- Python 3.13 instalado no sistema.
- Microfone para entrada de voz.

**⚙️ Configuração do Ambiente Virtual**

**1.Crie um diretório para o projeto e navegue até ele:**
   "bash"
   mkdir gerenciamento-ec2 && cd gerenciamento-ec2

   No terminal, execute: -python3.13 -m venv venv (Para preparar o ambiente e 
   baixar as dependecias apenas na pasta)
                         -source venv/bin/activate
**📦2. Instalar as Dependências**
   pip install boto3 pyaudio SpeechRecognition

**🔒3.Security Group configurado para as instâncias EC2.**
Assegure-se de ter um Security Group configurado para as instâncias EC2, permitindo comunicação e controle adequados.

**🛠️4.Criar uma IAM Role**
    1. No Console AWS, acesse IAM > Roles > Create Role.
    2. Escolha o tipo de entidade confiável como AWS Service e selecione 
    Lambda.

**📝5.Anexe as seguintes permissões gerenciadas:**
        ◦ ✅AmazonEC2FullAccess
        ◦ ✅AmazonS3FullAccess
        ◦ ✅CloudWatchLogsFullAccess
        ◦ ✅AmazonTranscribeFullAccess   

**🏷️6.Dê um nome para a role, como VoiceEC2ManagerRole, e conclua.**
 
Nota: Este tutorial utiliza permissões de acesso total (Full Access) para simplificação. Em projetos reais, sempre aplique a política de menor privilégio.

**🪣 7.Criar um Bucket S3**
    1. Acesse S3 > Create Bucket.
    2. Dê um nome único para o bucket (ex.: voice-ec2-manager).
    3. Escolha a região (ex.: us-east-1) e mantenha as configurações padrão.
    4. Clique em Create Bucket.

 **🌐8.Configurar o Security Group**
    1. No Console AWS, vá para EC2 > Security Groups.
    2. Crie ou edite um Security Group com as seguintes regras de entrada:
        ◦ 🟢Porta 22 (SSH) - Para conexões remotas (caso necessário).
        ◦ 🟢Porta 80 (HTTP) - Para acesso web (opcional).
    3. Salve e copie o ID do Security Group (ex.: sg-0abc123def4567890), pois ele será usado no código da Lambda.  

**🖥️9.Configurar a Função AWS Lambda**
    1. No Console AWS, acesse Lambda > Create Function.
    2. Escolha Author from scratch e preencha:
        ◦ Nome: VoiceEC2Manager
        ◦ Runtime: Python 3.x
    3. Anexe a role criada anteriormente (VoiceEC2ManagerRole) à função 
       Lambda.
    4. Substitua o código padrão pela função Lambda abaixo:    
      https://github.com/nolascojoao/automated-ec2-voice- 
      launcher/blob/main/lambda_function.py 
    5.Clique em Deploy para salvar a função.  

**⚡10.Configurar o Evento do S3 para Disparar a Lambda** 
    1.No Console AWS, acesse o bucket S3 criado anteriormente.
    2. Vá para Properties > Event Notifications > Create Event Notification.
    3. Configure:
        ◦ Nome: TriggerLambda
        ◦ Evento: PUT (Upload de arquivos)
        ◦ Prefixo/Sufixo: .json
        ◦ Destination: Escolha a função Lambda criada (VoiceEC2Manager).
    4.Salve a configuração.
    
**🐍11.Executar o Script Localmente**
Crie o script Python para capturar o áudio e interagir com o serviço S3 e Transcribe. Aqui está o código:https://github.com/nolascojoao/automated-ec2-voice-launcher/blob/main/voice_command.py
 
### **▶️ Execução do Projeto**
1. Gravar Comandos de Voz: python voice_command.py
2. Processamento na AWS:
   O áudio é enviado ao Amazon Transcribe para conversão em texto.
   A função Lambda analisa o texto e executa o comando EC2 correspondente.
3. Logs e Monitoramento
Confira logs de execução no CloudWatch para verificar o status de cada operação.

### **🔧Personalização**
Adicionando comandos: Atualize a função Lambda para incluir novos comandos de voz.
Idiomas: Configure o Amazon Transcribe para suportar outros idiomas.



