import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class DBManager:
    def __init__(
            self:"DBManager", 
            db_path:str=os.getenv('DB_PATH')
        )-> None:
        self.db_path = db_path

    # Cria a tabela 'jobs' no banco de dados
    def create_table(
            self:"DBManager",
        )-> None:
        # Abre uma conexão com o banco de dados
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Executa o comando SQL para criar a tabela 'jobs'
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                jobs_id INTEGER PRIMARY KEY AUTOINCREMENT,
                jobs_url TEXT NOT NULL UNIQUE,
                jobs_keyword TEXT,
                jobs_title TEXT,
                jobs_location TEXT,
                jobs_level TEXT,
                jobs_company TEXT,
                jobs_industries TEXT,
                jobs_workModel TEXT,
                jobs_role TEXT,
                jobs_description TEXT,
                jobs_hardSkills TEXT,
                jobs_activities TEXT,
                jobs_data_related TEXT
            );
            """)
            # Confirma as alterações no banco de dados
            conn.commit()

    # Insere uma nova vaga
    def insert_job(
            self: "DBManager", 
            job_data: dict[str, str]
        ) -> None:
        # Abre uma conexão com o banco de dados
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Lista de colunas que podem conter listas e precisam ser convertidas para string
            cols_to_check = ['jobs_industries', 'jobs_hardSkills', 'jobs_activities']
            for col in cols_to_check:
                col_data = job_data.get(col)
                # Se os dados forem do tipo lista, converte-os para uma string separada por vírgulas
                if isinstance(col_data, list):
                    job_data[col] = ', '.join(map(str, col_data))
            try:
                # Executa o comando SQL para inserir os dados na tabela 'jobs'
                cursor.execute("""
                INSERT INTO jobs (
                    jobs_url,
                    jobs_keyword,
                    jobs_title,
                    jobs_location,
                    jobs_level,
                    jobs_company,
                    jobs_industries,
                    jobs_workModel,
                    jobs_role,
                    jobs_description,
                    jobs_hardSkills,
                    jobs_activities,
                    jobs_data_related
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_data.get('jobs_url'),
                    job_data.get('jobs_keyword'),
                    job_data.get('jobs_title'),
                    job_data.get('jobs_location'),
                    job_data.get('jobs_level'),
                    job_data.get('jobs_company'),
                    job_data.get('jobs_industries'),
                    job_data.get('jobs_workModel'),
                    job_data.get('jobs_role'),
                    job_data.get('jobs_description'),
                    job_data.get('jobs_hardSkills'),
                    job_data.get('jobs_activities'),
                    job_data.get('jobs_data_related')
                ))
            # Captura erro de integridade, como tentativa de inserir uma URL duplicada
            except sqlite3.IntegrityError:
                print(f"A vaga com a URL '{job_data.get('url')}' já existe no banco de dados.")
            # Captura outros erros que possam ocorrer durante a inserção
            except Exception as e:
                print(f"Erro ao inserir dados: {e}")
            else:
                # Se não ocorrer erro, confirma as alterações no banco de dados
                conn.commit()

    # Recupera todos os dados da tabela 'jobs' e retorna um DataFrame do pandas
    def get_data(
            self: "DBManager",
        ) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM jobs"
            df = pd.read_sql_query(query, conn)
        return df

    # Remove todos os registros da tabela 'jobs'
    def clear_table(
            self: "DBManager",
        ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM jobs")
            conn.commit()

    # Atualiza as hard skills normalizadas na tabela utilizando um mapeamento de normalização
    def update_normalized_skills(
            self:"DBManager", 
            mapping:dict=None
        ) -> None:
        # Importa o mapeamento padrão de skills, se disponível
        from skills_map.skills_map import NORMALIZATION_MAPPING
        import sqlite3  # Importa sqlite3 novamente para garantir o acesso na função

        # Usa o mapping padrão se nenhum for fornecido
        mapping = mapping or NORMALIZATION_MAPPING

        # Função auxiliar para normalizar uma única skill, ignorando diferenças de maiúsculas/minúsculas
        def normalize_skill(
                skill: str, 
                mapping: dict
            ) -> str:
            """Normaliza uma única skill, ignorando diferenças de case."""
            if not skill:
                return skill
            skill_clean = skill.strip()
            # Verifica se a skill existe no mapeamento e retorna a versão normalizada
            for key, value in mapping.items():
                if skill_clean.lower() == key.lower():
                    return value
            return skill_clean

        # Função auxiliar para normalizar uma lista de skills representada como string separada por vírgulas
        def normalize_skills_list(
                skills_str: str, 
                mapping: dict
            ) -> str:
            """
            Recebe uma string com as hard skills separadas por vírgula, 
            normaliza cada item e retorna uma nova string padronizada.
            Caso skills_str seja None, retorna None.
            """
            if not skills_str:
                return skills_str  # Pode ser None ou uma string vazia
            # Divide a string em itens, removendo espaços extras
            skills = [s.strip() for s in skills_str.split(',') if s.strip()]
            normalized = [normalize_skill(s, mapping) for s in skills]
            return ", ".join(normalized)

        # Recupera os dados atuais do banco de dados
        df = self.get_data()

        # Aplica a normalização na coluna 'jobs_hardSkills' para cada registro
        df['jobs_hardSkills'] = df['jobs_hardSkills'].apply(lambda x: normalize_skills_list(x, mapping))

        # Atualiza os registros no banco de dados com as skills normalizadas
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for _, row in df.iterrows():
                cursor.execute(
                    "UPDATE jobs SET jobs_hardSkills = ? WHERE jobs_id = ?",
                    (row['jobs_hardSkills'], row['jobs_id'])
                )
            conn.commit()

        print("Padronização das hard skills aplicada com sucesso.")


if __name__ == "__main__":
    db = DBManager()
    db.update_normalized_skills()
