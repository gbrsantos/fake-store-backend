from pydantic import BaseModel
from typing import Optional, List
from model.carrinho import Carrinho
from schemas.carrinho_produto import CarrinhoProdutoSchema, CarrinhoProdutoViewSchema


class CarrinhoSchema(BaseModel):
    """ Define como um novo carrinho a ser inserido deve ser representado
    """
    id_user: int
    produtos: List[CarrinhoProdutoSchema]

class CarrinhoFinalizarSchema(BaseModel):
    """ Define como um carrinho a ser finalizado deve ser representado
    """
    id: int

class CarrinhoBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no id do carrinho.
    """
    id_user: int = 1

class CarrinhoViewSchema(BaseModel):
    """ Define como um carrinho será retornado: carrinho + carrinho produtos.
    """
    id: int 
    id_user: int    
    produtos: Optional[List[CarrinhoProdutoViewSchema]]

    class Config:
        orm_mode = True        
    
def apresenta_carrinho(carrinho: Carrinho):
    """ Retorna uma representação do estabelecimento seguindo o schema definido em
        CarrinhoViewSchema.
    """
    result = []
    for produto in carrinho.produtos: 
        result.append({
            "id": produto.id,
            "nome": produto.nome,
            "id_produto": produto.id_produto,
            "id_carrinho": carrinho.id,
            "quantidade": len(carrinho.produtos),
            "valor": produto.valor
        })
    return {
        "id": carrinho.id,
        "id_user": carrinho.id_user,
        "produtos": result
    }