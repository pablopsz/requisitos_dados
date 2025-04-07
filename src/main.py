from controller.db_manager import DBManager
from services.getAllJobs.getAllJobs import main as jobs_main
from services.llm.chain import JobChain as LLM
import pandas as pd
import time

# map_level = {"Estágio": 1, "Assistente": 2, "Analista": 3, "Pleno-Sênior": 4}

# map_locations = {
#     "Estados Unidos": {"location":"Estados%20Unidos", "geoId": 103644278},
#     "Brasil": {"location": "Brasil", "geoId":106057199},
#     "Rio de Janeiro": {"location": "Rio%20de%20Janeiro%20e%20Regi%C3%A3o", "geoId":90009575},
#     "São Paulo": {"location":"S%C3%A3o%20Paulo%20e%20Regi%C3%A3o", "geoId":90009574}
# }


def get_llm_info(
    jobs: pd.DataFrame
    ) -> pd.DataFrame:

    llm = LLM() # Instância do modelo de linguagem
    new_jobs = [] # Lista para armazenar as novas informações das vagas
    for _, job in jobs.iterrows():
        llm_data = llm.invoke(job['jobs_title'], job['jobs_description']) # Invocação do modelo de linguagem
        new_row = {
            'jobs_url': job['jobs_url'],
            'jobs_keyword': job['jobs_keyword'],
            'jobs_title': job['jobs_title'],
            'jobs_location': job['jobs_location'],
            'jobs_level': job['jobs_level'],
            'jobs_company': job['jobs_company'],
            'jobs_industries': job['jobs_industries'],
            'jobs_workModel': llm_data.get('work_model', None),
            'jobs_role': llm_data.get('role', None),
            'jobs_description': job['jobs_description'],
            'jobs_hardSkills': llm_data.get('hard_skills', None),
            'jobs_activities': llm_data.get('activities', None),
            'jobs_data_related': llm_data.get('data_related', None)
        }
        new_jobs.append(new_row) # Adição da nova linha

    return pd.DataFrame(new_jobs) # Retorno do DataFrame com as novas informações


def run(
    keyword: str, 
    location: str, 
    level: str, 
    total_jobs: int = 1000, 
    insert_jobs: bool = True
    ) -> pd.DataFrame:

    jobs = jobs_main(keyword, location, level, total_jobs) # Busca de vagas
    jobs = get_llm_info(jobs) # Obtenção de informações do modelo de linguagem
    if insert_jobs: # Inserção das vagas no banco de dados
        db = DBManager() # Instância do gerenciador de banco de dados
        for _, job in jobs.iterrows():
            db.insert_job(job) # Inserção da vaga
    return jobs

if __name__ == '__main__':
    start = time.time()

    # Configuração para vagas nos Estados Unidos (em inglês)
    us_keywords = ["Data Analyst", "Data Engineer"]
    us_locations = ["United States"]  # localização em inglês


    # Configuração para vagas no Brasil (em português)
    pt_keywords = ["Ciência de Dados", "Analista de Dados", "Engenheiro de Dados"]
    pt_locations = ["Brasil", "São Paulo", "Rio de Janeiro"]
    
    levels = ["Estágio", "Assistente", "Analista", "Pleno-Sênior"]

    all_jobs = []

    # Busca para vagas nos Estados Unidos
    for keyword in us_keywords:
        for location in us_locations:
            for level in levels:
                print(f"Buscando vagas para '{keyword}' in '{location}' at level '{level}'...")
                jobs = run(keyword, location, level, 1, insert_jobs=True)
                all_jobs.append(jobs)

    # # Busca para vagas no Brasil
    # for keyword in pt_keywords:
    #     for location in pt_locations:
    #         for level in levels:
    #             print(f"Buscando vagas para '{keyword}' em '{location}' no nível '{level}'...")
    #             run(keyword, location, level, 100, insert_jobs=True)


    print(f"Tempo total de execução: {time.time() - start:.2f} segundos.")
