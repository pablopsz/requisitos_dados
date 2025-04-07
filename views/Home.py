import streamlit as st
import altair as alt
import pandas as pd

from views.data_view.skills_count import raw_data 

st.set_page_config(page_title="Análise de Requisitos", layout="centered", page_icon=":computer:")

def app() -> None:

    @st.cache_data
    def get_raw_data() -> pd.DataFrame:
        return raw_data()

    @st.cache_data
    def skills_count(raw_df: pd.DataFrame, group_cols: tuple[str]) -> pd.DataFrame:
        raw_df = raw_df.copy()
        exploded_df = raw_df.explode('jobs_hardSkills')
        new_group_cols = list(group_cols) + ['jobs_hardSkills']
        grouped_df = exploded_df.groupby(by=new_group_cols).size().reset_index(name='count')
        grouped_df = grouped_df.sort_values(by='count', ascending=False).reset_index(drop=True)
        return grouped_df

    @st.cache_data
    def create_chart(
        df: pd.DataFrame,
        hue_col: str
    ) -> alt.Chart:
        
        base = alt.Chart(df).transform_joinaggregate(
            total='sum(count)',
            groupby=['jobs_hardSkills']
        )
        
        bars = base.mark_bar().encode(
            x=alt.X('count:Q', title='Contagem'),
            y=alt.Y(
                'jobs_hardSkills:N', 
                title='Skills', 
                sort=alt.EncodingSortField(field='total', op='sum', order='descending')
            ),
            color=alt.Color(f'{hue_col}:N', title=hue_col)
        )
        
        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=3
        ).encode(
            x=alt.X('total:Q', title='Contagem'),
            y=alt.Y(
                'jobs_hardSkills:N', 
                title='Skills',
                sort=alt.EncodingSortField(field='total', op='sum', order='descending')
            ),
            text=alt.Text('total:Q', format='.0f')
        )
        
        return bars + text

    st.title('Requisitos de Vagas de Dados')

    st.sidebar.title("Filtros")

    raw_df = get_raw_data()

    group_col = st.sidebar.selectbox(
        "Selecione uma coluna para agrupar",
        options=['Palavra Chave', 'Nível']
    )

    map_group_cols = {
        'Palavra Chave': 'jobs_keyword',
        'Nível': 'jobs_level'
    }
    group_col = map_group_cols.get(group_col)

    selected_keyword = st.sidebar.multiselect(
        "Selecione uma palavra-chave",
        options=raw_df['jobs_keyword'].unique()
    )

    filtered_df = raw_df.copy()

    if selected_keyword:
        filtered_df = filtered_df[filtered_df['jobs_keyword'].isin(selected_keyword)]

    levels_selected = st.sidebar.multiselect(
        "Selecione o nível",
        options=raw_df['jobs_level'].unique()
    )

    if levels_selected:
        filtered_df = filtered_df[filtered_df['jobs_level'].isin(levels_selected)]

    locations_selected = st.sidebar.multiselect(
        "Selecione a localização",
        options=raw_df['jobs_location'].unique()
    )

    if locations_selected:
        filtered_df = filtered_df[filtered_df['jobs_location'].isin(locations_selected)]

    industries_selected = st.sidebar.multiselect(
        "Selecione a indústria",
        options=raw_df['jobs_industries'].unique()
    )

    if industries_selected:
        filtered_df = filtered_df[filtered_df['jobs_industries'].isin(industries_selected)]

    companies_selected = st.sidebar.multiselect(
        "Selecione a empresa",
        options=raw_df['jobs_company'].unique()
    )

    if companies_selected:
        filtered_df = filtered_df[filtered_df['jobs_company'].isin(companies_selected)]

    filtered_df['jobs_hardSkills'] = filtered_df['jobs_hardSkills'].apply(
        lambda x: tuple(x) if isinstance(x, list) else x
    )

    df_skills_count = skills_count(filtered_df, group_cols=(group_col,))

    col1, col2 = st.columns(2)

    with col1:
        unique_skills = df_skills_count['jobs_hardSkills'].nunique()
        st.metric(label="Número de Skills", value=unique_skills)

    with col2:
        total_jobs = filtered_df.shape[0]
        st.metric(label="Número de Vagas", value=total_jobs)

    st.subheader("Contagem de Skills")
    st.altair_chart(create_chart(df_skills_count, hue_col=group_col), use_container_width=True)

    st.write(df_skills_count)
