import pandas as pd
from src.controller.db_manager import DBManager

def raw_data() -> pd.DataFrame:
    db = DBManager()
    # Obtém todos os registros da tabela 'jobs' em um DataFrame
    jobs = db.get_data()
    jobs = jobs.dropna(subset=['jobs_hardSkills'])
    jobs = jobs[jobs['jobs_data_related'] != "0.0"]
    jobs = jobs[jobs['jobs_hardSkills'] != ""]
    # Dicionário para padronizar os valores da coluna 'jobs_keyword'
    replacements = {
        "Data Analyst": "Analista de Dados",
        "Data Engineer": "Engenheiro de Dados",
        "Data Science": "Ciência de Dados"
    }
    jobs['jobs_keyword'] = jobs['jobs_keyword'].replace(replacements)

    for index, row in jobs.iterrows():
        # Obtém a string de hard skills
        skills_str = row['jobs_hardSkills']
        # Converte a string em uma lista de skills
        skills_list = parse_skills(skills_str)
        # Remove valores duplicados da lista de skills
        skills_list = list(set(skills_list))
        # Atualiza o DataFrame com a lista de skills
        jobs.at[index, 'jobs_hardSkills'] = skills_list

    return jobs

# Função que recebe uma string de skills separadas por vírgula e retorna uma lista de skills limpas
def parse_skills(
        skills_str: str
    ) -> list[str]:
    # Divide a string por vírgulas e remove espaços em branco de cada skill
    return [skill.strip() for skill in skills_str.split(',')]


if __name__ == "__main__":
    ...
