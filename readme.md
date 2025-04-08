# Raspagem de dados e análise de requisitos para vagas da área de dados :mag:

## Sobre

Este projeto realiza a raspagem de dados de vagas no LinkedIn, analisa as descrições de vagas utilizando uma LLM, armazena os requisitos extraídos em um banco de dados SQLite3 e disponibiliza uma interface interativa de visualização através de um dashboard em Streamlit.

## Funcionalidades

1. **Raspagem de Dados**
   - Utiliza a biblioteca Requests para raspagem de links de vagas do LinkedIn.
   - Utiliza a biblioteca BeautifulSoup para extração de informações como título, descrição e a empresa responsável pela publicação da vaga.
   - Utiliza bibliotecas como Asyncio e Aiohttp para paralelizar as requisições de vagas.

2. **Análise de Descrição com LLM**
   - Processa o texto da descrição de cada vaga utilizando uma LLM (OpenAI API) para identificar e categorizar requisitos técnicos e comportamentais.
   - Utiliza a biblioteca LangChain para criar uma tool que padroniza a resposta da LLM.

3. **Armazenamento em SQLite3**
   - Cria um gerenciador para as operações com o banco de dados (como criação da tabela, inserção de dados e limpeza da tabela).
   - Insere os dados obtidos na tabela.

4. **Dashboard em Streamlit**
   - Interface web para explorar os dados coletados, desenvolvida com a biblioteca Streamlit.

## Estrutura do Projeto

A organização dos arquivos e pastas do projeto é apresentada a seguir:

- src: Contém o arquivo main que executa a busca, análise e inserção dos dados no banco de dados.
  - controller: Contém o arquivo da classe "DBManager", que contém os métodos para manusear.
    - skills_map: Contém o dicionário para padronizar o nome dos requisitos solicitados nas vagas.
  - services: Contém o arquivo main que executa a busca de todas a vagas e extrai os requisitos solicitados na vaga por meio de uma LLM.
    - getAllJobs: Contém a função que executa a busca das vagas baseando-se em palavra-chave, nível da vaga e localização.
    - llm: Contém a classe utilizada para extrair os requisitos da descrição da vaga.
- views: Contém o arquivo que cria o dashboard para análise dos dados obtidos.
  - get_data: Contém a função que busca e limpa os dados do banco de dados.

Para iniciar o projeto, execute o comando:  

    streamlit run "app.py"

## Resultado final

[Dash Requisitos](https://github.com/user-attachments/assets/31a7a14a-d4b3-4d7c-a8e0-3628a982d001)
