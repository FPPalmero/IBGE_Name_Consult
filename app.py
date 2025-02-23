import streamlit as st
import pandas as pd
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

def fazer_request(endpoint):
  url = f"{FASTAPI_URL}{endpoint}"
  response = requests.get(url)
  if response.status_code == 200:
    return response.json()
  st.error(f"Erro {response.status_code}: Falha ao obter os dados da API")


def main():
  st.title("Consulta de Nomes no IBGE 📊")
  option = st.radio("Escolha uma consulta:", ["Frequência por Estado", "Frequência por Década", "Ranking por Estado", "Ranking por Década"])

  if option == "Frequência por Estado":
    nome = st.text_input("Digite um nome:")
    if nome:
      response = fazer_request(f"/nomes/por_estado/{nome}")
      if response:
        st.subheader(f"Frequência do nome {nome} por Estado:")
        df = pd.DataFrame(response["frequencias"].items(), columns=["Estado", "Frequência"])
        st.dataframe(df, hide_index=True)
        st.bar_chart(df, x="Estado", y="Frequência")
      else:
        st.error("Nenhuma informação encontrada.")


  elif option == "Frequência por Década":
    nome = st.text_input("Digite um nome:")
    if nome:
      response = fazer_request(f"/nomes/por_decada/{nome}")
      if response:
        st.subheader(f"Frequência do nome {nome} por Década:")
        df = pd.DataFrame(response["decadas"].items(), columns=["Década", "Quantidade"])
        st.dataframe(df, hide_index=True)
        st.bar_chart(df, x="Década", y="Quantidade")
      else:
        st.error("Nenhuma informação encontrada.")


  elif option == "Ranking por Estado":
    estados_dict = fazer_request(f"/estados/id")
    if estados_dict:
      estados_dict = estados_dict["estados"]

      nome_estado = st.selectbox("Selecione um Estado:", ["Selecione um Estado"] + list(estados_dict.values()))
      if nome_estado != "Selecione um Estado":
        localidade = [k for k, v in estados_dict.items() if v == nome_estado][0]
        response = fazer_request(f"/nomes/por_estado/ranking/{localidade}")
        
        if response:
          dados_ranking = response["ranking"]
          nome_estado = list(dados_ranking.keys())[0]
          st.subheader(f"Ranking de nomes no Estado: {nome_estado}")
          data = []

          for i in dados_ranking[nome_estado]:
            data.append([i['ranking'], i['nome'], i['frequencia']])
          df = pd.DataFrame(data, columns=["Ranking", "Nome", "Frequência"])
          st.dataframe(df, hide_index=True)
          st.bar_chart(df, x="Nome", y="Frequência")
        else:
          st.error("Nenhuma informação encontrada.")


  elif option == "Ranking por Década":
    decadas_disponiveis = ["Selecione uma década"] + list(range(1940, 2020, 10))
    decada = st.selectbox("Selecione uma década:", decadas_disponiveis)
    if decada != "Selecione uma década":
      response = fazer_request(f"/nomes/por_decada/ranking/{decada}")
      
      if response:
        st.subheader(f"Ranking de nomes na década de {decada}")
        data = []

        for i in response["ranking"][str(decada)]:
            data.append([i['ranking'], i['nome'], i['frequencia']])
        df = pd.DataFrame(data, columns=["Ranking", "Nome", "Frequência"])
        st.dataframe(df, hide_index=True)
        st.bar_chart(df, x="Nome", y="Frequência")
      else:
        st.error("Nenhuma informação encontrada.")


  else:
    st.error("Por favor, digite um nome.")


if __name__ == "__main__":
  main()