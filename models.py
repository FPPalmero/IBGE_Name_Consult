from pydantic import BaseModel, Field
from typing import Dict, List

class EstadoResponse(BaseModel):
  estados: Dict[int, str] = Field(example={"11": "Rondônia", "12": "Acre", "13": "Amazonas"})

class FrequenciaNomeEstadoResponse(BaseModel):
  frequencias: Dict[str, float] = Field(example={"Rondônia": "1000.00", "Acre": "850.00", "Amazonas": "1200.00"})

class FrequenciaNomeDecadaResponse(BaseModel):
  decadas: Dict[str, int] = Field(example={"[1930-1940]": "1500", "[1940-1950]": "10000", "[1950-1960]": "25000"})

class RankingNome(BaseModel):
  ranking: int
  nome: str
  frequencia: int

class RankingResponse(BaseModel):
  ranking: Dict[str, List[RankingNome]]

