# Grab Harvester

[![LinkedIn](https://img.shields.io/badge/%40alexcamargos-230A66C2?style=social&logo=LinkedIn&label=LinkedIn&color=white)](https://www.linkedin.com/in/alexcamargos)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Code Style: pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge)](https://github.com/pre-commit/pre-commit)
[![CI Status](https://img.shields.io/github/actions/workflow/status/alexcamargos/grab-harvester/ci.yml?logo=github&label=CI&style=for-the-badge)](https://github.com/alexcamargos/grab-harvester/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/github/alexcamargos/grab-harvester?logo=codecov&logoColor=white&style=for-the-badge)](https://codecov.io/gh/alexcamargos/grab-harvester)
[![Last Commit](https://img.shields.io/github/last-commit/alexcamargos/grab-harvester?style=for-the-badge&logo=github)](https://github.com/alexcamargos/grab-harvester/commits/main)

> Um downloader de arquivos em lote, leve, concorrente e robusto para Python.

---

- [Grab Harvester](#grab-harvester)
  - [O Problema](#o-problema)
  - [A Solução: Grab Harvester](#a-solução-grab-harvester)
    - [Principais Funcionalidades](#principais-funcionalidades)
  - [Como Rodar Localmente](#como-rodar-localmente)
    - [1. Clone o repositório](#1-clone-o-repositório)
    - [2. Configuração e Execução](#2-configuração-e-execução)
      - [Opção A: Usando uv (Recomendado)](#opção-a-usando-uv-recomendado)
      - [Opção B: Usando pip](#opção-b-usando-pip)
  - [Como Usar](#como-usar)
    - [Uso Simples (Script Rápido)](#uso-simples-script-rápido)
    - [Uso Avançado (Integração em Projetos)](#uso-avançado-integração-em-projetos)
  - [Aprendizados e Arquitetura](#aprendizados-e-arquitetura)
  - [Autor](#autor)
  - [Licença](#licença)

---

## O Problema

Muitas vezes, projetos de software ou análise de dados precisam baixar um grande volume de arquivos de diversas URLs. Realizar essa tarefa de forma manual ou com scripts simples pode ser:

* **Lento e Ineficiente:** Baixar arquivos um por um (sequencialmente) não aproveita a capacidade da rede e do processador, tornando o processo demorado.
* **Frágil:** Scripts simples geralmente não lidam bem com falhas de rede, interrupções ou erros de permissão no disco, exigindo intervenção manual para reiniciar.
* **Redundante:** É comum que o processo reinicie do zero, baixando novamente arquivos que já foram transferidos com sucesso, desperdiçando tempo e banda.


## A Solução: Grab Harvester

O **Grab Harvester** foi criado para resolver exatamente esses problemas, oferecendo uma forma simplificada e poderosa de buscar múltiplos arquivos. Ele automatiza o processo com foco em performance e confiabilidade.


### Principais Funcionalidades

* **Downloads Concorrentes:** Utiliza um pool de threads para baixar vários arquivos simultaneamente, acelerando drasticamente o tempo total da operação.
* **Verificação de Integridade:** Antes de iniciar um download, o sistema verifica se o arquivo já existe no destino. Se existir, compara o tamanho do arquivo local com o remoto (`Content-Length`). O download só é refeito se o arquivo local estiver incompleto, economizando recursos.
* **Tratamento Robusto de Erros:** Captura e encapsula exceções comuns de rede (usando `httpx`) e de operações de arquivo (I/O), como `NetworkDownloadError` e `FileOperationError`. Isso permite que a aplicação que o utiliza possa tratar as falhas de forma granular, sem que o programa inteiro pare inesperadamente.
* **Simplicidade de Uso:** Oferece uma interface limpa e direta para iniciar o processo de download, abstraindo toda a complexidade de gerenciamento de threads e tratamento de erros.


## Como Rodar Localmente

Para executar este projeto em sua máquina, você precisará do [Python 3.11+](https://www.python.org/downloads/) instalado.

### 1. Clone o repositório

```bash
git clone https://github.com/alexcamargos/grab-harvester.git
cd grab-harvester
```

### 2. Configuração e Execução

#### Opção A: Usando uv (Recomendado)

O [uv](https://github.com/astral-sh/uv) é um gerenciador de pacotes extremamente rápido.

1.  **Instale as dependências:**
    ```bash
    uv sync
    ```

2.  **Execute o exemplo ou os testes:**
    ```bash
    uv run examples/library_example.py
    uv run pytest
    ```

#### Opção B: Usando pip

1.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate   # Windows
    ```

2.  **Instale as dependências:**
    ```bash
    pip install httpx loguru tqdm
    pip install pytest pytest-mock  # Para rodar os testes
    ```

3.  **Execute:**
    ```bash
    python examples/library_example.py
    pytest
    ```


## Como Usar

O Grab Harvester pode ser utilizado tanto para scripts rápidos quanto integrado em sistemas maiores.

### Uso Simples (Script Rápido)

A função `download` é a maneira mais rápida de começar. Ela aceita uma lista de URLs (strings) ou objetos `DownloadTask`.

```python
from grabharvester import download

urls = [
    "https://www.python.org/static/img/python-logo.png",
    "https://httpbin.org/image/jpeg"
]

# Baixa os arquivos usando 4 threads simultâneas
download(urls, max_threads=4, destination_dir="./downloads")
```

### Uso Avançado (Integração em Projetos)

Para maior controle e aderência aos princípios SOLID (Injeção de Dependência), utilize as classes `DownloadManager` e `DownloadService`.

```python
from pathlib import Path
from grabharvester import DownloadManager, DownloadService, DownloadTask

# 1. Instancie o serviço (pode ser mockado em testes)
service = DownloadService()

# 2. Inicialize o gerenciador
manager = DownloadManager(service, max_threads=2)

# 3. Defina as tarefas
tasks = [
    DownloadTask(url='https://www.python.org/static/img/python-logo.png'),
    DownloadTask(
        url='https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png',
        destination_path=Path('./google_logo.png')
    ),
]

# 4. Execute
print("Iniciando downloads...")
results = manager.run(tasks)

print(f"Sucessos: {len(results.successes)}")
print(f"Falhas: {len(results.failures)}")
```


## Aprendizados e Arquitetura

O desenvolvimento do Grab Harvester foi uma excelente oportunidade para aplicar e aprofundar conceitos importantes de engenharia de software em Python.

1. **Programação Concorrente:** A principal melhoria de performance veio do uso de `concurrent.futures.ThreadPoolExecutor`. A escolha por threads em vez de processos (`ProcessPoolExecutor`) foi estratégica, pois a tarefa de download é majoritariamente limitada por I/O (espera de rede), cenário onde threads são mais eficientes e consomem menos memória.
2. **Design Orientado a Objetos e Inversão de Dependência:** A lógica de download foi encapsulada na classe `DownloadService`. Isso não apenas organiza o código, mas também facilita os testes. Em vez de chamar `httpx.get` diretamente no código principal, ele é usado dentro de um serviço, o que permite "mockar" a biblioteca `httpx` nos testes unitários e simular respostas de rede (sucesso, falha, etc.) sem depender de uma conexão real.
3. **Exceções Customizadas:** Criar exceções específicas como `NetworkDownloadError` e `FileOperationError` em vez de propagar as exceções genéricas (`httpx.RequestError`, `IOError`) torna a API do `Grab Harvester` mais clara e estável. O código que utiliza a biblioteca sabe exatamente que tipo de problemas esperar, sem precisar conhecer os detalhes das dependências internas (como `httpx`).
4. **Testes Unitários Abrangentes com `pytest` e `mocker`:** A qualidade do projeto é garantida por uma suíte de testes que cobre os principais cenários:
    * Download bem-sucedido.
    * Falhas de rede.
    * Erros de escrita em disco.
    * Lógica para pular downloads de arquivos já existentes e completos.
    * Lógica para refazer downloads de arquivos incompletos.

    O uso do `mocker` foi fundamental para isolar o `DownloadService` de sistemas externos (rede e sistema de arquivos), garantindo testes rápidos, determinísticos e confiáveis.
5. **Automação de Qualidade (Pre-commit):** Integração de ferramentas de linter e formatadores automáticos via `pre-commit`. Isso assegura a criação de código melhor estruturado e formatado, mantendo a base de código limpa e consistente automaticamente.


## Autor

Feito com :heart: por [Alexsander Lopes Camargos](https://github.com/alexcamargos) :wave: Entre em contato!

[![GitHub](https://img.shields.io/badge/-AlexCamargos-1ca0f1?style=flat-square&labelColor=1ca0f1&logo=github&logoColor=white&link=https://github.com/alexcamargos)](https://github.com/alexcamargos)
[![Twitter Badge](https://img.shields.io/badge/-@alcamargos-1ca0f1?style=flat-square&labelColor=1ca0f1&logo=twitter&logoColor=white&link=https://twitter.com/alcamargos)](https://twitter.com/alcamargos)
[![Linkedin Badge](https://img.shields.io/badge/-alexcamargos-1ca0f1?style=flat-square&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/alexcamargos/)](https://www.linkedin.com/in/alexcamargos/)
[![Gmail Badge](https://img.shields.io/badge/-alcamargos@vivaldi.net-1ca0f1?style=flat-square&labelColor=1ca0f1&logo=Gmail&logoColor=white&link=mailto:alcamargos@vivaldi.net)](mailto:alcamargos@vivaldi.net)


## Licença

Este projeto está sob a licença [MIT](LICENSE).
