from pydantic import BaseModel, Field
from typing import List
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser


# Define um Enum para representar os tipos de trabalho possíveis em uma vaga
class WorkModel(str, Enum):
    """Modelo de trabalho da vaga de emprego"""
    hibrido = "Híbrido"
    presencial = "Presencial"
    remoto = "Remoto"
    nao_especificado = "Não especificado"


# Define um modelo Pydantic que representa a descrição da vaga, contendo todos os campos relevantes
class JobDescription(BaseModel):
    """
    Descrição unificada de uma vaga de emprego que extrai os campos e padroniza as hard_skills.
    """
    work_model: WorkModel = Field(
        description="Extraído conforme o texto, sem padronização adicional.",
        examples=["Híbrido", "Presencial", "Remoto", "Não especificado"]
    )
    role: str = Field(
        description="Cargo extraído conforme o texto, sem padronização adicional.",
        examples=["Analista de Dados", "Cientista de Dados Pleno", "Engenheiro de Dados Jr."]
    )
    hard_skills: List[str] = Field(
        description="Hard skills extraídas diretamente do texto.",
        examples=["Python", "SQL", "Power BI", "BigQuery", "Spark", "AWS", "Tableau", "Excel", "Google Sheets"]
    )
    validated_hard_skills: List[str] = Field(
        description="Hard skills padronizadas com nomes oficiais. Deve seguir convenções como 'Power BI' e 'Excel' em vez de 'Microsoft BI' ou 'MS Excel'.",
        examples=["Python", "SQL", "Power BI", "BigQuery", "Spark", "AWS", "Tableau", "Excel", "Google Sheets"]
    )
    activities: List[str] = Field(
        description="Atividades extraídas do texto, sem padronização.",
        examples=["Analisar métricas de negócio", "Desenvolver pipelines de dados", "Automatizar Processos"]
    )
    data_related: bool = Field(
        description="Indica se a vaga é relacionada a dados, extraído conforme o texto.",
        example=True
    )


# Cria um container para encapsular a descrição da vaga
class JobDescriptionContainer(BaseModel):
    description: JobDescription = Field(description="Container principal para a descrição da vaga")


# Classe que integra a extração e padronização dos dados da vaga utilizando LangChain e OpenAI
class JobChain:
    """
    Classe que:
      1. Extrai os dados estruturados da vaga (incluindo hard_skills e activities)
      2. Padroniza o campo hard_skills, gerando o campo validated_hard_skills, conforme convenções definidas.
    """
    def __init__(
            self: "JobChain", 
            parser: bool = True
        ) -> None:
        # Converte o modelo Pydantic em uma função compatível com a chamada de funções da OpenAI
        self.tool = convert_to_openai_function(JobDescriptionContainer)
        
        # Cria um template de prompt que orienta o modelo de linguagem a extrair e padronizar os dados da vaga
        self.prompt = ChatPromptTemplate.from_template(
            """Você é um sistema especializado em análise estrutural de vagas de dados. Siga rigorosamente:

1. Extraia os campos da vaga com base EXCLUSIVA no texto fornecido.
2. Para o campo "hard_skills", extraia as tecnologias mencionadas e, em seguida, padronize-as utilizando nomes oficiais.
   Adote as seguintes convenções:
   - Converta: "BI", "Microsoft BI", "PowerBI", "MS Power BI" → "Power BI"
   - Converta: "MS Excel", "Microsoft Excel" → "Excel"
   - Converta: "Python 3", "Python 4" → "Python"
   - Converta: "Google Data Studio", "Data Studio" → "Looker"
   - Converta: "PowerPoint", "Ms Power Point", "Microsoft PowerPoint" → "Power Point"
   - Converta: "ML", "Aprendizado de Máquina" → "Machine Learning"
   - Converta: "DL" → "Deep Learning"
   - Converta: "AI", "IA" → "Inteligência Artificial"
   - Converta: "git" → "Git"
   - Separe: "HTML/CSS" em "HTML" e "CSS"; "IA/NLP" em "IA" e "NLP"
3. Mantenha os demais campos (work_model, role, activities e data_related) conforme extraídos.

Texto da vaga:
###
Título: {job_title}

{description}
###
"""
        )
        
        # Configura o modelo de linguagem
        self.chat = ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0,
            top_p=1
        )
        
        # Cria uma cadeia que une o prompt com o modelo de linguagem e a função convertida, configurando a chamada da função correta
        base_chain = self.prompt | self.chat.bind(
            functions=[self.tool],
            function_call={'name': 'JobDescriptionContainer'}
        )
        
        # Se o parser estiver habilitado, adiciona um parser para extrair os dados a partir da chave "description"
        if parser:
            self.chain = base_chain | JsonKeyOutputFunctionsParser(key_name='description')
        else:
            self.chain = base_chain

    def invoke(
            self: "JobChain", 
            job_title: str, 
            description: str
        ) -> dict[str, str]:
        # Invoca a cadeia de processamento com os dados fornecidos (título e descrição da vaga)
        result = self.chain.invoke({'job_title': job_title, 'description': description})
        
        # Garante que os campos "hard_skills" e "validated_hard_skills" sejam do tipo lista, mesmo que o resultado seja um único valor
        for key in ["hard_skills", "validated_hard_skills"]:
            value = result.get(key, [])
            if not isinstance(value, list):
                result[key] = [value]
        
        # Retorna o resultado estruturado e padronizado
        return result


if __name__ == '__main__':
    # Define os dados de entrada para a vaga de emprego
    job_title = "Analista de Dados"
    description = (
        "Empresa XYZ busca um profissional para análise de dados. "
        "O trabalho será híbrido com atuação remota em parte do tempo. "
        "Requisitos: MS Excel, SQL, PowerBI, Microsoft Power Point. "
        "Atividades: Analisar métricas, desenvolver dashboards e automatizar processos. "
        "A vaga é relacionada a dados."
    )

    # Cria uma instância de JobChain e processa a descrição da vaga
    chain = JobChain()
    result = chain.invoke(job_title, description)
    
    # Exibe o resultado unificado e padronizado
    print("Resultado Unificado:")
    print(result)