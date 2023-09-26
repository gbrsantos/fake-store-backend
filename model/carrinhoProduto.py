from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  model import Base


class CarrinhoProduto(Base):
    __tablename__ = 'carrinho_produto'

    id = Column("id", Integer, primary_key=True)
    id_produto = Column(Integer, nullable= False)    
    id_carrinho = Column(Integer, ForeignKey('carrinho.id'), nullable= False)    
    nome = Column(String(140))
    valor = Column(Float)
    quantidade = Column(Integer, nullable= False)
    imagem = Column(String(255))

    data_insercao = Column(DateTime, default=datetime.utcnow, nullable= False)

    # Definição do relacionamento entre o carrinho e carrinho-produto.
    # Aqui está sendo definido o relacionamento one-to-many com carrinho-produto
    carrinho = relationship('Carrinho', back_populates='produtos')

    def __init__(self, id_carrinho:Integer, id_produto:Integer, nome: String(140), valor:Float, quantidade:Integer, imagem: String,
                 data_insercao:Union[DateTime, None] = None):
        """
        Cria um Carrinho Produto

        Arguments:
            id_produto: id do produto dummyjson.
            valor: valor esperado para o produto
            nome: nome do produto
            quantidade : quantidade de produtos
            id_carrinho: id do carrinho
            imagem: referência da imagem
            data_insercao: data de quando o produto foi inserido à base
        """
        self.id_produto = id_produto
        self.nome = nome
        self.valor = valor
        self.quantidade = quantidade
        self.id_carrinho = id_carrinho
        self.imagem = imagem

        # se não for informada, será o data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao


