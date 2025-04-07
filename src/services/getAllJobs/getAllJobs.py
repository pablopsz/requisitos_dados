import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

def main(
    keyword: str, 
    location: str, 
    level: str, 
    total_jobs: int
) -> pd.DataFrame:
    return asyncio.run(async_main(keyword, location, level, total_jobs)) # Execução da função assíncrona

async def async_main(
    keyword: str, 
    location: str, 
    level: str, 
    total_jobs: int
) -> pd.DataFrame:
    session = aiohttp.ClientSession() # Sessão do cliente
    sem = asyncio.Semaphore(10) # Semáforo para controle de concorrência
    jobs_urls = await get_jobs_async(keyword, location, level, total_jobs, session, sem) # Busca de URL das vagas
    jobs_data = await fetch_all_jobs_info(jobs_urls, session, sem) # Raspagem de informações das vagas
    await session.close() # Fechamento da sessão
    df = pd.DataFrame(jobs_data)
    df['jobs_keyword'] = keyword
    df['jobs_location'] = location
    df['jobs_level'] = level
    return df

async def get_jobs_async(
    keyword: str, 
    location: str,
    level: str,
    total_jobs: int,
    session: aiohttp.ClientSession, 
    sem: asyncio.Semaphore, 
) -> list[str]:
    tasks = [fetch_jobs(keyword, location, level, start, session, sem) for start in range(0, total_jobs, 10)] # Criação de tarefas para busca de vagas
    results = await asyncio.gather(*tasks) # Execução das tarefas
    jobs_url = [url for urls in results if urls for url in urls] # Desempacotamento dos resultados
    return jobs_url[:total_jobs]

async def fetch_jobs(
    keyword: str,
    location: str, 
    level: str, 
    start: int, 
    session: aiohttp.ClientSession, 
    sem: asyncio.Semaphore, 
    max_retries: int = 10
) -> list[str]:
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search" # API do LinkedIn
    map_level = {"Estágio": 1, "Assistente": 2, "Analista": 3, "Pleno-Sênior": 4} # Mapeamento dos níveis de experiência
    map_locations = {
    "Estados Unidos": {"location":"Estados%20Unidos", "geoId": 103644278}, 
    "Brasil": {"location": "Brasil", "geoId":106057199}, 
    "Rio de Janeiro": {"location": "Rio%20de%20Janeiro%20e%20Regi%C3%A3o", "geoId":90009575},
    "São Paulo": {"location":"S%C3%A3o%20Paulo%20e%20Regi%C3%A3o", "geoId":90009574}
    } # Mapeamento de localizações
    location_dict = map_locations.get(location, {"location": "Brasil", "geoId": 106057199}) # Localização padrão
    params = {
        "keywords": keyword, # Palavras chave da busca de vagas
        "location": location_dict.get("location", ""), # Localização
        "geoId": location_dict.get("geoId", ""), # ID da localização
        "position": "1",
        "pageNum": "0",
        "start": start, # Início da busca
        "f_TPR": "",
        "f_E": map_level.get(level, "") if level else "", # Nível de experiência
    }
    retries = 0
    while retries < max_retries: # Tentativas de conexão
        async with sem: # Semáforo para controle de concorrência
            async with session.get(url, params=params) as response: # Requisição GET
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    jobs_list = soup.find_all("li") # Lista de vagas
                    jobs_url = [job.find("a")["href"] for job in jobs_list if job.find("a")] # URL das vagas
                    return jobs_url
                retries += 1
                wait_time = 5 * retries
                await asyncio.sleep(wait_time)
    return []

async def fetch_all_jobs_info(
    jobs_urls: list[str],
    session: aiohttp.ClientSession, 
    sem: asyncio.Semaphore
) -> list[dict[str, str]]:
    tasks = [fetch_jobs_info(url, session, sem) for url in jobs_urls] # Criação de tarefas para busca de informações das vagas
    results = await asyncio.gather(*tasks) # Execução das tarefas
    return [job for job in results if job] # Desempacotamento dos resultados

async def fetch_jobs_info(
    url: str,
    session: aiohttp.ClientSession, 
    sem: asyncio.Semaphore, 
    max_retries: int = 10
) -> dict[str, str] | None:
    retries = 0
    while retries < max_retries: # Tentativas de conexão
        async with sem: # Semáforo para controle de concorrência
            async with session.get(url) as response: # Requisição GET
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "" # Título da vaga
                    company = soup.find("a", class_="topcard__org-name-link topcard__flavor--black-link").get_text(strip=True) if soup.find("a", class_="topcard__org-name-link topcard__flavor--black-link") else "" # Empresa
                    description = soup.find("div", class_="description__text description__text--rich").get_text(strip=True) if soup.find("div", class_="description__text description__text--rich") else "" # Descrição da vaga
                    try:
                        industries = soup.find_all("span", class_="description__job-criteria-text description__job-criteria-text--criteria")[3].get_text(strip=True) if soup.find_all("span", class_="description__job-criteria-text description__job-criteria-text--criteria") else "" # Indústrias
                    except:
                        industries = ""
                    data_dict = {
                        "jobs_title": title,
                        "jobs_company": company,
                        "jobs_industries": industries,
                        "jobs_description": description,
                        "jobs_url": url,
                    }
                    return data_dict
                retries += 1
                wait_time = 6 * retries
                await asyncio.sleep(wait_time)
                continue
    return None


if __name__ == "__main__":
    keyword = "Dados"
    location = "Brasil"
    level = "Estágio"
    total_jobs = 1000
    jobs = main(keyword, location, level, total_jobs)
    jobs.to_excel("jobs.xlsx", index=False)
