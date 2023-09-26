from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  model import Base


class Carrinho(Base):
    __tablename__ = 'carrinho'

    id = Column("id", Integer, primary_key=True,  autoincrement=True)
    id_user = Column(Integer, unique= True, nullable= False)    
    data_insercao = Column(DateTime, default=datetime.utcnow, nullable= False)

    # Definição do relacionamento entre carrinho e carrinho-produto

    # Aqui está sendo definido o relacionamento one-to-many com carrinho-produto
    produtos = relationship('CarrinhoProduto', back_populates='carrinho')

    def __init__(self, id_user:Integer,
                 data_insercao:Union[DateTime, None] = None):
        """
        Cria um Carrinho

        Arguments:
            id_user: id do usuário
            data_insercao: data de quando o produto foi inserido à base
        """
        self.id_user = id_user

        # se não for informada, será o data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao


