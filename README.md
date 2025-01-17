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

### **2. Criar Ambiente Virtual**
1. Crie um diretório para o projeto e navegue até ele:
   ```bash
   mkdir gerenciamento-ec2 && cd gerenciamento-ec2

   No terminal, execute: python3.13 -m venv venv (Para preparar o ambiente e baixar as dependecias apenas na pasta)
                         source venv/bin/activate
2. Instale as dependências:
   pip install boto3 pyaudio SpeechRecognition

##▶️ Execução do Projeto
1. Gravar Comandos de Voz: python voice_command.py
2. Processamento na AWS:
   O áudio é enviado ao Amazon Transcribe para conversão em texto.
   A função Lambda analisa o texto e executa o comando EC2 correspondente.
3. Logs e Monitoramento
Confira logs de execução no CloudWatch para verificar o status de cada operação.

##🔧 Personalização
Adicionando comandos: Atualize a função Lambda para incluir novos comandos de voz.
Idiomas: Configure o Amazon Transcribe para suportar outros idiomas.



