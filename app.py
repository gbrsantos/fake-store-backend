from ast import List
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote
from sqlalchemy import and_
from sqlalchemy.orm import  joinedload

from sqlalchemy.exc import IntegrityError

from logger import logger
from model import Session
from model.carrinho import Carrinho
from model.carrinhoProduto import CarrinhoProduto
from schemas import *
from flask_cors import CORS
import json

from schemas.carrinho import CarrinhoBuscaSchema, CarrinhoFinalizarSchema, CarrinhoSchema, CarrinhoViewSchema
from schemas.carrinho_produto import CarrinhoProdutoDeleteSchema, CarrinhoProdutoSchema


info = Info(title="Fake Store", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
carrinho_produto_tag = Tag(name="Carrinho Produto", description="Atualização e remoção de carrinho-produto à base")
carrinho_tag = Tag(name="Carrinho", description="Adição, visualização e finalização de carrinho")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.post('/carrinho', tags=[carrinho_tag],
          responses={"200": CarrinhoSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_carrinho(body: CarrinhoSchema):
    """Adiciona um novo Carrinho à base de dados junto com os produtos
    Retorna uma representação dos carrinho e produtos associados.
    """
    
    if(body.id_user == None):
        raise Exception("Id do usuário invalido") 
    
    if not body.produtos:
        raise Exception("Não é possível cadastrar um carrinho sem itens") 
    
    # criando conexão com a base
    session = Session()
    
    carrinho = session.query(Carrinho).filter(Carrinho.id_user == body.id_user).first()    

    if carrinho is None:
        # Se o carrinho não existe, crie um novo       
        session.add(Carrinho(id_user=body.id_user))
        carrinho = session.query(Carrinho).filter(Carrinho.id_user == body.id_user).first()          
    
    #Adicione os produtos ao carrinho
    for produto_data in body.produtos:
        carrinho_produto = CarrinhoProduto(              
            id_carrinho  = carrinho.id,       
            id_produto=produto_data.id_produto,
            nome=produto_data.nome,
            valor=produto_data.valor,
            quantidade=produto_data.quantidade,
            imagem= produto_data.imagem
        )

    produtoBuscado = session.query(CarrinhoProduto).filter(
        and_(
            CarrinhoProduto.id_carrinho == carrinho.id,
            CarrinhoProduto.id_produto == carrinho_produto.id_produto
        )
    ).first()    
    if produtoBuscado is not None: 
        produtoBuscado.quantidade += 1
        produtoBuscado.valor = produtoBuscado.valor * produtoBuscado.quantidade
        session.add(produtoBuscado)
    else:
        session.add(carrinho_produto)
    try:       
        
        # efetivando o camando de adição de novo item na tabela
        session.commit()
       
        return apresenta_carrinho(carrinho), 200

    except IntegrityError as e:
        # como a duplicidade do id de usuário é a provável razão do IntegrityError
        error_msg = "Carrinho com id de usuário já salvo na base :/"
        #logger.warning(f"Erro ao adicionar carrinho, {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        #faz o rollback da transação
        session.rollback()
        # caso um erro fora do previsto
        error_msg = "Um erro não identificado ocorreu :/"
        #logger.warning(f"Erro ao adicionar carrinho, {error_msg}")
        return {"mesage": error_msg}, 400
    finally:
        session.close()

@app.delete('/carrinho-produto', tags=[carrinho_produto_tag],
         responses={"200": CarrinhoProdutoViewSchema, "404": ErrorSchema})
def delete_carrinho_produto(query: CarrinhoProdutoDeleteSchema):
    """Faz o delete de um produto do carrinho a partir do id do mesmo    
    Retorna uma representação do carrinho-produto removido.
    """
    id_carrinho_produto = query.id
    try:
        # criando conexão com a base
        session = Session()
        # fazendo a busca do carrinho-produto
        
        ##logger.debug(f"Coletando dados sobre carrinho #{id_carrinho_produto}")
        carrinhoProduto = session.query(CarrinhoProduto).filter(CarrinhoProduto.id == id_carrinho_produto).first()     
        
        if not carrinhoProduto:
            # se o carrinho-produto não foi encontrado            
            error_msg = "Produto não encontrado na base :/"
            ##logger.warning(f"Erro ao buscar carrinho-produto '{id_carrinho_produto}', {error_msg}")
            return {"mesage": error_msg}, 404
        else:
            ##logger.debug(f"carrinho-produto encontrado")
            
            # faz o delete do carrinho-produto
            session.delete(carrinhoProduto)
            
            session.commit()
           
            #retorna uma visao de carrinho-produto como json
            result = CarrinhoProdutoViewSchema.from_orm(carrinhoProduto)
            return result.json(), 200
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Um erro não identificado ocorreu  :/"       
        ##logger.warning(f"Erro ao remover carrinho-produto, {error_msg}")
        return {"mesage": error_msg}, 400
    finally:
        session.close()

@app.post('/carrinho/finalizar', tags=[carrinho_tag],
          responses={"200": CarrinhoSchema, "409": ErrorSchema, "400": ErrorSchema})
def finalizar_carrinho(body: CarrinhoFinalizarSchema):
    """Finaliza um carrinho de compras
    Retorna uma mensagem informando o sucesso da finalização.
    """
    
    if(body.id == None):
        raise Exception("Id do carrinho invalido") 
    
    # criando conexão com a base
    session = Session()

    # Buscando o carrinho fazendo join com carrinho-produtos referente ao id do carrinho
    carrinho = session.query(Carrinho).options(joinedload(Carrinho.produtos)).\
        where(Carrinho.id == body.id).one()        


    if carrinho is None:
        # Se o carrinho não existe, joga uma exceção 
        raise Exception("Erro ao buscar carrinho") 

    #logger.debug(f"Finalizando o carrinho de id: '{carrinho.id}'")
    try:       
        # removendo os produtos da base
        for produto in carrinho.produtos:
            session.delete(produto)
        session.delete(carrinho)

        # efetivando o camando de remoção dos item na tabela
        session.commit()

        #logger.debug(f"Adicionado produto de nome: '{estabelecimento.nome}'")
        return {"mensagem": "Carrinho finalizado com sucesso"}, 200

    except IntegrityError as e:
        print(e)
        # o principal erro de  IntegrityError que pode ocorrer é a tentativa de remoção de uma chave estrangeira
        error_msg = "Não foi possível remover o carrinho, pois há produtos relacionados"
        #logger.warning(f"Não foi possível remover o carrinho, pois há produtos relacionados. Carrinho id:  '{carrinho.id}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        #faz o rollback da transação        
        session.rollback()
        # caso um erro fora do previsto
        error_msg = "Um erro não identificado ocorreu :/"
        #logger.warning(f"Não foi possível remover o carrinho, pois há produtos relacionados., {error_msg}")
        return {"mesage": error_msg}, 400
    finally:
        session.close()

@app.get('/carrinho', tags=[carrinho_tag],
         responses={"200": CarrinhoProdutoViewSchema, "404": ErrorSchema})
def get_carrinho(query: CarrinhoBuscaSchema):
    """Faz a busca por um Carrinho a partir do id do usuário
    Retorna uma representação do carrinho e carrinho-produtos associados.
    """    
    id_user = query.id_user
    try:
        # criando conexão com a base
        session = Session()

        # fazendo a busca
        ##logger.debug(f"Coletando dados sobre carrinho do usuario #{id_user}")

        carrinho = session.query(Carrinho).options(joinedload(Carrinho.produtos)).\
        where(Carrinho.id_user == id_user).one_or_none()

        if not carrinho:
            # se o carrinho não foi encontrado
            error_msg = "Carrinho não encontrado na base :/"
            # #logger.warning(f"Erro ao buscar carrinho do usuário com id: '{id_user}', {error_msg}")
            return {"mesage": error_msg}, 204
        else:
            ##logger.debug(f"Carrinho econtrado: '{carrinho.id}'")
            
            # retorna a representação de carrinho em json
            result = CarrinhoViewSchema.from_orm(carrinho)
            return result.json(), 200

    except Exception as e:
        # caso um erro fora do previsto
        #faz o rollback da transação
        session.rollback()
        error_msg = "Um erro não identificado ocorreu :/"
        print(e)
        ##logger.warning(f"Erro ao buscar carrinho do usuário com id: '{id_user}', {error_msg}")
        return {"mesage": error_msg}, 400
    finally:
        session.close()

@app.put('/carrinho-produto', tags=[carrinho_produto_tag],
          responses={"200": CarrinhoProdutoSchema, "409": ErrorSchema, "400": ErrorSchema})
def update_carrinho_produto(body: CarrinhoProdutoSchema):
    """Adiciona o carrinho-produto baseado em seu id
    Retorna uma mensagem informando que o carrinho-produto foi atualizado com sucesso.
    """
    
    if(body.id_carrinho == None):
        raise Exception("Id do carrinho inválido") 
    
    if not body.id:
        raise Exception("Id do carrinho produto inválido") 
    
    # criando conexão com a base
    session = Session()
    
    # fazendo a busca
    carrinhoProduto = session.query(CarrinhoProduto).filter(CarrinhoProduto.id == body.id).first()    

     # caso não encontre lança uma exceção
    if carrinhoProduto is None:
         raise Exception("Não foi possível buscar o carrinho")
    
    carrinhoProduto.quantidade = body.quantidade

    # atualiza o carrinho-produto na base
    session.add(carrinhoProduto)

    #logger.debug(f"Atualizando quantidade do carrinho-produto de id: '{carrinhoProduto.id}'")
    try:          
        # efetivando o camando de adição de novo item na tabela
        session.commit()
       
        return {"mensagem": "Quantidade alterada com sucesso"}, 200

    except Exception as e:
        #faz o rollback da transação
        print(e)
        session.rollback()
        # caso um erro fora do previsto
        error_msg = "Um erro não identificado ocorreu :/"
        #logger.warning(f"Erro ao atualizar quantidade de carrinho-produtos, {error_msg}")
        return {"mesage": error_msg}, 400
    finally:
        session.close()
