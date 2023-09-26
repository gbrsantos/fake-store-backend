from pydantic import BaseModel
from typing import Optional, List
from schemas import *


class CarrinhoProdutoSchema(BaseModel):
    """ Define como um novo carrinho produto a ser inserido deve ser representado
    """
    id: Optional[int]
    nome: str
    id_carrinho: Optional[int]
    id_produto: int
    quantidade: int
    valor: float
    imagem: str

class CarrinhoProdutoViewSchema(BaseModel):
    """ Define como um carrinho produto será retornado.
    """
    id: int = 1
    id_produto: int = 1
    id_carrinho: int =1 
    quantidade: int = 1
    nome: str = "Banana Prata"
    valor: float = 12.50    
    imagem: str = ""
    class Config:
        orm_mode = True

class CarrinhoProdutoDeleteSchema(BaseModel):
    """ Define como um carrinho produto será removido.
    """
    id: int