from fastapi import FastAPI, HTTPException
from typing import Dict
from models import EstadoResponse, FrequenciaNomeDecadaResponse, FrequenciaNomeEstadoResponse, RankingResponse
import httpx

app = FastAPI()

IBGE_NOMES_URL = 'https://servicodados.ibge.gov.br/api/v2/censos/nomes/'
IBGE_ESTADOS_URL = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados'
IBGE_RANKING_URL = 'https://servicodados.ibge.gov.br/api/v2/censos/nomes/ranking'


async def fazer_request(url: str, params: dict = None):
  async with httpx.AsyncClient() as client:
    try:
      response = await client.get(url=url, params=params)
      response.raise_for_status()
      result = response.json()
      return result
    except httpx.HTTPStatusError as e:
      raise HTTPException(status_code= e.response.status_code, detail=f"Erro {e.response.status_code} ao acessar {url}")
    except httpx.RequestError as e:
      raise HTTPException(status_code=500, detail="Erro ao se comunicar com o servidor.")


@app.get("/estados/id", tags=["Estados"], response_model=EstadoResponse)
async def get_estados():
  params = {'view': 'nivelado'}
  dados_estado = await fazer_request(url=IBGE_ESTADOS_URL, params=params)
  estados_dict: Dict[int, str] = {}
  estados_dict = {dados['UF-id']: dados['UF-nome'] for dados in dados_estado}
  return {"estados": estados_dict}



@app.get("/nomes/por_estado/{nome}", tags=["Nomes"], response_model=FrequenciaNomeEstadoResponse)
async def get_nome_por_estado(nome: str):
  params = {'groupBy': 'UF'}
  dados_frequencia = await fazer_request(f"{IBGE_NOMES_URL}{nome}", params=params)
  estados_dict = await get_estados()
  estados_dict = estados_dict["estados"]
  frequencia_dict = {}

  for dados in dados_frequencia:
    id_estado = int(dados['localidade'])
    if 'res' in dados and len(dados['res']) > 0:
      frequencia = dados['res'][0]['proporcao']
    else:
      frequencia = 0

    if id_estado in estados_dict:
      nome_estado = estados_dict[id_estado]
      frequencia_dict[nome_estado] = frequencia
  return {"frequencias": frequencia_dict}


@app.get("/nomes/por_decada/{nome}", tags=["Nomes"], response_model=FrequenciaNomeDecadaResponse)
async def get_nome_por_decada(nome: str):
  dados_decadas = await fazer_request(f'{IBGE_NOMES_URL}{nome}')
  decada_dict = {}

  for dados in dados_decadas:
    if 'res' in dados and len(dados['res']) > 0:
      for i in dados['res']:
        periodo = i['periodo']
        frequencia = i['frequencia']
        decada_dict[periodo] = frequencia
  return {"decadas": decada_dict}


@app.get("/nomes/por_estado/ranking/{localidade}", tags=["Nomes"], response_model=RankingResponse)
async def get_ranking_por_estado(localidade: int):
  params = {"localidade": localidade}
  dados_frequencia = await fazer_request(IBGE_RANKING_URL, params=params)
  estados_dict = await get_estados()
  estados_dict = estados_dict["estados"]
  
  if localidade not in estados_dict:
    raise HTTPException(status_code=404, detail="Estado não encontrado com o código fornecido.")
  nome_estado = estados_dict[localidade]
  ranking_dict = {nome_estado: []}
  
  for dados in dados_frequencia:
    for i in dados['res']:
      nome_frequencia_ranking = {
        "ranking": i["ranking"],
        "nome": i["nome"],
        "frequencia": i["frequencia"]
      }
      ranking_dict[nome_estado].append(nome_frequencia_ranking)
  return {"ranking": ranking_dict}


@app.get("/nomes/por_decada/ranking/{decada}", tags=["Nomes"], response_model=RankingResponse)
async def get_ranking_por_decada(decada: int):
  params = {"decada": decada}
  dados_frequencia = await fazer_request(IBGE_RANKING_URL, params=params)
  decada_convertida = str(decada)
  ranking_dict = {decada_convertida: []}
  
  for dados in dados_frequencia:
    for i in dados['res']:
      nome_frequencia_ranking = {
        "ranking": i["ranking"],
        "nome": i["nome"],
        "frequencia": i["frequencia"]
      }
      ranking_dict[decada_convertida].append(nome_frequencia_ranking)
  return {"ranking": ranking_dict}

