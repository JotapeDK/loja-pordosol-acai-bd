from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from typing import List
import sqlite3
import uvicorn
import bcrypt
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
CAMINHO_BANCO = BASE_DIR / "banco.db"

app = FastAPI(title="Açaí Pôr do Sol - Login e Cadastro")
app.add_middleware(
    SessionMiddleware,
    secret_key="12345SECRETKEY54321"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/cadastrar_usuario")
def cadastrar_usuario(
        gmail: str = Form(...),
        usuario: str = Form(...),
        senha: str = Form(...),
        confirmar_senha: str = Form(...)
):

    if senha != confirmar_senha:
        return {
            "sucesso": False,
            "mensagem": "As senhas não coincidem Digite a mesma senha nos dois campos"
        }

    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()

    try:
        senha_hash = bcrypt.hashpw(
            senha.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
        
        cursor.execute(
            "INSERT INTO usuarios (gmail, usuario, senha) VALUES (?, ?, ?)",
            (gmail, usuario, senha_hash)
        )
        conexao.commit()
        conexao.close()
        return {
            "sucesso": True,
            "mensagem": "Cadastro realizado com sucesso! Agora você pode fazer login"
        }
    except sqlite3.IntegrityError:
        conexao.close()
        return {
            "sucesso": False,
            "mensagem": "Este nome de usuário já está cadastrado. Escolha outro"
        }



@app.post("/fazer_login")
def processar_login(
    request: Request,
    usuario: str = Form(...),
    senha: str = Form(...)
):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id, senha FROM usuarios WHERE usuario = ?",
        (usuario,)
    )
    resultado_login = cursor.fetchone()
    

    if resultado_login and bcrypt.checkpw(
        senha.encode("utf-8"),
        resultado_login[1].encode("utf-8")
    ):
        usuario_id = resultado_login[0]
        request.session["usuario_id"] = usuario_id
        cursor.execute(
            "SELECT id FROM carrinho WHERE usuario_id = ?",
            (usuario_id,)
        )
        resultado_carrinho = cursor.fetchone()

        if resultado_carrinho:
            carrinho_id = resultado_carrinho[0]
        else:
            cursor.execute(
                "INSERT INTO carrinho (usuario_id) VALUES (?)",
                (usuario_id,)
            )
            carrinho_id = cursor.lastrowid

        conexao.commit()
        conexao.close()
        return {
            "sucesso": True,
            "mensagem": f"Login realizado com sucesso! Bem-vindo, {usuario}."
        }

    return {
        "sucesso": False,
        "mensagem": "Usuário ou senha incorretos!"
    }



@app.post("/adicionar_carrinho")
def adicionar_carrinho(
    request: Request,
    tamanho_id: Optional[int] = Form(None),
    produto_id: Optional[int] = Form(None),
    cremes: List[int] = Form([]),
    frutas: List[int] = Form([]),
    complementos: List[int] = Form([])
    ):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return {
            "sucesso": False,
            "mensagem": "Faça login para adicionar algum produto ao carrinho."
        }

    if tamanho_id is None and produto_id is None:
        return {
            "sucesso": False,
            "mensagem": "Nenhum produto foi informado."
        }
    
    if tamanho_id is not None and produto_id is not None:
        return {
            "sucesso": False,
            "mensagem": "Informe apenas um tipo de produto."
        }
    
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()

    if produto_id is not None:
            cursor.execute(
                "SELECT id FROM produtos WHERE id = ?",
                (produto_id,)
            )

            resultado_produto = cursor.fetchone()

            if not resultado_produto:
                return {
                    "sucesso": False,
                    "mensagem": "Produto não encontrado."
                }
    
    cursor.execute(
        "SELECT id FROM carrinho WHERE usuario_id = ?",
        (usuario_id,)
    )
    resultado_addCarinho = cursor.fetchone()

    carrinho_id = resultado_addCarinho[0]

    if tamanho_id is not None:
        cursor.execute(
            "SELECT id FROM tamanhos WHERE id = ?",
            (tamanho_id,)
        )
        resultado_tamanho = cursor.fetchone()

        if not resultado_tamanho:
            return {
                "sucesso": False,
                "mensagem": "Tamanho não encontrado."
            }
    
    if len(cremes) > 2:
        return {
            "sucesso": False,
            "mensagem": "Máximo de 2 cremes permitidos."
        }

    if len(frutas) > 3: 
        return{
            "sucesso": False,
            "mensagem": "Máximo de 3 frutas permitidas."
        }

    if len(complementos) > 4:
        return{
            "sucesso": False,
            "mensagem": "Máximo de 4 complementos permitidos."
        }

    for creme_id in cremes:
        cursor.execute(
            "SELECT id FROM cremes WHERE id = ?",
            (creme_id,)
        )   
        resultado_creme = cursor.fetchone()

        if not resultado_creme:
            return {
                "sucesso": False,
                "mensagem": "Creme não encontrado."
            }

    for fruta_id in frutas:
        cursor.execute(
            "SELECT id FROM frutas WHERE id = ?",
            (fruta_id,)
        )   
        resultado_fruta = cursor.fetchone()

        if not resultado_fruta:
            return {
                "sucesso": False,
                "mensagem": "Fruta não encontrada."
            }

    for complemento_id in complementos:
        cursor.execute(
            "SELECT id FROM complementos WHERE id = ?",
            (complemento_id,)
        )
        resultado_complemento = cursor.fetchone()

        if not resultado_complemento:
            return {
                "sucesso": False,
                "mensagem": "Complemento não encontrado."
            }

    if produto_id is not None:
        cursor.execute("""
            SELECT id, quantidade
            FROM itens_carrinho
            WHERE carrinho_id = ? AND produto_id = ?
        """,
        (carrinho_id, produto_id)
        )
        produto_existente = cursor.fetchone()

        if produto_existente:
            item_id = produto_existente[0]
            quantidade_atual = produto_existente[1]

            nova_quantidade = quantidade_atual + 1

            cursor.execute("""
                UPDATE itens_carrinho SET quantidade = ? WHERE id = ?
                """,
                (nova_quantidade, item_id)
            )

            conexao.commit()
            conexao.close()

            return {
                "sucesso": True,
                "mensagem": "Quantidade do produto atualizada."
            }
        
    cursor.execute("""
            INSERT INTO itens_carrinho
            (carrinho_id, tamanho_id, produto_id, quantidade)
            VALUES (?, ?, ?, ?)
        """,
        (carrinho_id, tamanho_id, produto_id, 1)
    )
    item_id = cursor.lastrowid
    
    for creme_id in cremes:
        cursor.execute(
            "INSERT INTO item_cremes (item_id, creme_id) VALUES (?, ?)",
            (item_id, creme_id,)
        )

    for fruta_id in frutas:
        cursor.execute(
            "INSERT INTO item_frutas (item_id, fruta_id) VALUES (?, ?)",
            (item_id, fruta_id,)
        )

    for complemento_id in complementos:
        cursor.execute(
            "INSERT INTO item_complementos (item_id, complemento_id) VALUES (?, ?)",
            (item_id, complemento_id,)
        )

    conexao.commit()
    conexao.close()
    
    return {
    "sucesso": True,
    "mensagem": "Item adicionado ao carrinho.",
    "carrinho_id": carrinho_id,
    "item_id": item_id
    }

@app.get("/ver_carrinho")
def ver_carrinho(request: Request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return {
            "sucesso": False,
            "mensagem": "Faça login para ver o carrinho."
        }

    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id FROM carrinho WHERE usuario_id = ?",
        (usuario_id,)
    )
    resultado_carrinho = cursor.fetchone()

    carrinho_id = resultado_carrinho[0]

    cursor.execute(
        "SELECT id, tamanho_id, produto_id, quantidade FROM itens_carrinho WHERE carrinho_id = ?",
        (carrinho_id,)
    )

    itens = cursor.fetchall()

    carrinho = []

    for item in itens:
        item_id = item[0]
        tamanho_id = item[1]
        produto_id = item[2]
        quantidade = item[3]

        if tamanho_id is not None:
            cursor.execute(
                "SELECT tamanho, preco FROM tamanhos WHERE id = ?",
                (tamanho_id,)
            )
            resultado_tamanho = cursor.fetchone()

            nome_tamanho = resultado_tamanho[0]
            preco_tamanho = resultado_tamanho[1]

        else:
            cursor.execute(
                "SELECT nome, preco FROM produtos WHERE id = ?",
                (produto_id,)
            )
            resultado_produto = cursor.fetchone()

            nome_produto = resultado_produto[0]
            preco_produto = resultado_produto[1]

        cursor.execute(
            "SELECT creme_id FROM item_cremes WHERE item_id = ?",
            (item_id,)
        )
        cremes = cursor.fetchall()

        cremes_detalhes = []
        
        for creme in cremes:
            creme_id = creme[0]

            cursor.execute(
                "SELECT nome, preco FROM cremes WHERE id = ?",
                (creme_id,)
            )
            resultado_creme = cursor.fetchone()

            cremes_detalhes.append(resultado_creme)

        cursor.execute(
            "SELECT fruta_id FROM item_frutas WHERE item_id = ?",
            (item_id,)
        )
        frutas = cursor.fetchall()

        frutas_detalhes = []

        for fruta in frutas:
            fruta_id = fruta[0]

            cursor.execute(
                "SELECT nome, preco FROM frutas WHERE id = ?",
                (fruta_id,)
            )
            resultado_frutas = cursor.fetchone()

            frutas_detalhes.append(resultado_frutas)

        cursor.execute(
            "SELECT complemento_id FROM item_complementos WHERE item_id = ?",
            (item_id,)
        )
        complementos = cursor.fetchall()

        complementos_detalhes = []

        for complemento in complementos:
            complemento_id = complemento[0]

            cursor.execute(
                "SELECT nome, preco FROM complementos WHERE id = ?",
                (complemento_id,)
            )
            resultado_complementos = cursor.fetchone()

            complementos_detalhes.append(resultado_complementos)

        if tamanho_id is not None:
            item_carrinho = {
                "item_id": item_id,
                "tipo": "personalizado",
                "tamanho": {
                    "nome": nome_tamanho,
                    "preco": preco_tamanho
                },
                "quantidade": quantidade,
                "cremes": cremes_detalhes,
                "frutas": frutas_detalhes,
                "complementos": complementos_detalhes
            }
        else:
            item_carrinho = {
                "item_id": item_id,
                "tipo": "pronto",
                "produto": {
                    "nome": nome_produto,
                    "preco": preco_produto
                },
                "quantidade": quantidade
            }    

        carrinho.append(item_carrinho)

    conexao.close()

    return {
        "sucesso": True,
        "carrinho": carrinho
    }

@app.post("/excluir_item")
def excluir_item(
    request: Request,
    item_id: int = Form(...)
):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return {
            "sucesso": False,
            "mensagem": "Faça login para excluir um produto."
        }

    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id FROM carrinho WHERE usuario_id = ?",
        (usuario_id,)
    )

    resultado_carrinho = cursor.fetchone()

    carrinho_id = resultado_carrinho[0]

    cursor.execute(
        "SELECT id FROM itens_carrinho WHERE id = ? AND carrinho_id = ?",
        (item_id, carrinho_id,)
    )   

    resultado_item = cursor.fetchone()

    if not resultado_item:
        return {
            "sucesso": False,
            "mensagem": "Item não encontrado no seu carrinho."
        }

    cursor.execute(
        "DELETE FROM item_cremes WHERE item_id = ?",
        (item_id,)
    )
    cursor.execute(
        "DELETE FROM item_frutas WHERE item_id = ?",
        (item_id,)
    )
    cursor.execute(
        "DELETE FROM item_complementos WHERE item_id = ?",
        (item_id,)
    )
    cursor.execute(
        "DELETE FROM itens_carrinho WHERE id = ?",
        (item_id,)
    )

    conexao.commit()
    conexao.close()

    return {
        "sucesso": True,
        "mensagem": "Item deletado com sucesso"
    }

@app.post("/alterar_quantidade")
def alterar_quantidade(
    request: Request,
    item_id: int = Form(...),
    quantidade: int = Form(...)
):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return {
            "sucesso": False,
            "mensagem": "Faça login para alterar a quantidade do produto."
        }

    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()
    
    cursor.execute(
        "SELECT id FROM carrinho WHERE usuario_id = ?",
        (usuario_id,)
    )

    resultado_carrinho = cursor.fetchone()
    
    carrinho_id = resultado_carrinho[0]

    cursor.execute(
        "SELECT id FROM itens_carrinho WHERE id = ? AND carrinho_id = ?",
        (item_id, carrinho_id)
    )

    resultado_item = cursor.fetchone()

    if not resultado_item:
        return {
            "sucesso": False,
            "mensagem": "Item não encontrado no seu carrinho."
        }

    cursor.execute(
        "UPDATE itens_carrinho SET quantidade = ? WHERE id = ?",
        (quantidade, item_id)
    )

    conexao.commit()
    conexao.close()

    return {
        "sucesso": True,
        "mensagem": "Quantidade alterada com sucesso."
    }

@app.get("/usuario_logado")
def usuario_logado(request: Request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return {
            "logado": False
        }

    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()
        
    cursor.execute(
        "SELECT usuario, gmail FROM usuarios WHERE id = ?",
        (usuario_id,)
    )
    resultado_usuario = cursor.fetchone()

    conexao.close()

    return{
        "logado": True,
        "usuario": resultado_usuario[0],
        "gmail": resultado_usuario[1]
    }


@app.post("/logout")
def logout(request: Request):
    request.session.clear()

    return {
        "sucesso": True,
        "mensagem": "Logout realizado com sucesso."
    }

@app.post("/alterar_perfil")
def alterar_perfil(
    request: Request,
    usuario: Optional[str] = Form(None),
    email: Optional[str] = Form(None)
):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return {
            "sucesso": False,
            "mensagem": "Usuário não está logado."
        }

    if usuario is None and email is None:
        return {
            "sucesso": False,
            "mensagem": "Nenhuma alteração foi informada."
        }

    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT usuario, gmail FROM usuarios WHERE id = ?",
        (usuario_id,)
    )

    resultado_usuario = cursor.fetchone()

    if resultado_usuario is None:
        conexao.close()

        return{
            "sucesso": False,
            "mensagem": "Usuário não encontrado."
        }

    if usuario is None:
        usuario = resultado_usuario[0]

    if email is None:
        email = resultado_usuario[1]

    if usuario == resultado_usuario[0] and email == resultado_usuario[1]:
        conexao.close()

        return {
            "sucesso": False,
            "mensagem": "Nenhuma alteração foi feita."
        }

    cursor.execute(
        "UPDATE usuarios SET usuario = ?, gmail = ? WHERE id = ?",
        (usuario, email, usuario_id)
    )

    conexao.commit()
    conexao.close()

    return {
        "sucesso": True,
        "mensagem": "Perfil alterado com sucesso."
    }

@app.post("/excluir_conta")
def excluir_conta(request: Request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return {
            "sucesso": False,
            "mensagem": "Usuário não está logado."
        }
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id FROM usuarios WHERE id = ?",
        (usuario_id,)
    )
    resultado_usuario = cursor.fetchone()

    if not resultado_usuario:
        conexao.close()

        return {
            "sucesso": False,
            "mensagem": "Usuário não encontrado."
        }

    cursor.execute(
        "SELECT id FROM carrinho WHERE usuario_id = ?",
        (usuario_id,)
    )
    resultado_carrinho = cursor.fetchone()

    if resultado_carrinho:
        carrinho_id = resultado_carrinho[0]

        cursor.execute(
            "SELECT id FROM itens_carrinho where carrinho_id = ?",
            (carrinho_id,)
        )
        itens = cursor.fetchall()

        for item in itens:
            item_id = item[0]
            cursor.execute(
                "DELETE FROM item_cremes WHERE item_id = ?",
                (item_id,)
            )
            cursor.execute(
                "DELETE FROM item_frutas WHERE item_id = ?",
                (item_id,)
            )
            cursor.execute(
                "DELETE FROM item_complementos WHERE item_id = ?",
                (item_id,)
            )

        cursor.execute(
            "DELETE FROM itens_carrinho WHERE carrinho_id = ?",
            (carrinho_id,)
        )

        cursor.execute(
            "DELETE FROM carrinho WHERE id = ?",
            (carrinho_id,)
        )

    cursor.execute(
        "DELETE FROM usuarios WHERE id = ?",
        (usuario_id,)
    )

    conexao.commit()
    conexao.close()

    request.session.clear()

    return {
        "sucesso": True,
        "mensagem": "Sua conta e todos os dados associados foram excluídos com sucesso."
    }


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)