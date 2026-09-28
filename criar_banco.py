import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CAMINHO_BANCO = BASE_DIR / "banco.db"

conexao = sqlite3.connect(CAMINHO_BANCO)
cursor = conexao.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gmail TEXT UNIQUE NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS carrinho (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        
            FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id)
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tamanhos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tamanho INTEGER UNIQUE NOT NULL,
        preco DECIMAL NOT NULL
    );
''')
cursor.execute('''
    INSERT OR IGNORE INTO tamanhos (tamanho, preco)
    VALUES (300, 17.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO tamanhos (tamanho, preco)
    VALUES (500, 19.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO tamanhos (tamanho, preco)
    VALUES (700, 21.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO tamanhos (tamanho, preco)
    VALUES (1000, 23.00);
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS cremes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        preco DECIMAL NOT NULL
    );
''')
cursor.execute('''
    INSERT OR IGNORE INTO cremes (nome, preco)
    VALUES ('Nutella', 4.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO cremes (nome, preco)
    VALUES ('Creme de ninho', 4.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO cremes (nome, preco)
    VALUES ('Leite Condensado', 4.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO cremes (nome, preco)
    VALUES ('Chocolate ao leite', 4.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO cremes (nome, preco)
    VALUES ('Chocolate meio amargo', 4.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO cremes (nome, preco)
    VALUES ('Chocolate branco', 4.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO cremes (nome, preco)
    VALUES ('Ovomaltine', 4.00);
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS frutas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        preco DECIMAL NOT NULL
    );
''')
cursor.execute('''
    INSERT OR IGNORE INTO frutas (nome, preco)
    VALUES ('Morango', 2.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO frutas (nome, preco)
    VALUES ('Banana', 2.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO frutas (nome, preco)
    VALUES ('Kiwi', 2.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO frutas (nome, preco)
    VALUES ('Manga', 2.00);
''')
cursor.execute('''
    INSERT OR IGNORE INTO frutas (nome, preco)
    VALUES ('Uva verde', 2.00);
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS complementos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        preco DECIMAL NOT NULL
    );
''')
cursor.execute('''
    INSERT OR IGNORE INTO complementos (nome, preco)
    VALUES ('Gotas de chocolate', 3.50);
''')
cursor.execute('''
    INSERT OR IGNORE INTO complementos (nome, preco)
    VALUES ('Granola', 3.50);
''')
cursor.execute('''
    INSERT OR IGNORE INTO complementos (nome, preco)
    VALUES ('Canudos de chocolate', 3.50);
''')
cursor.execute('''
    INSERT OR IGNORE INTO complementos (nome, preco)
    VALUES ('Paçoca', 3.50);
''')
cursor.execute('''
    INSERT OR IGNORE INTO complementos (nome, preco)
    VALUES ('Confeitos', 3.50);
''')
cursor.execute('''
    INSERT OR IGNORE INTO complementos (nome, preco)
    VALUES ('Raspas de chocolate', 3.50);
''')
cursor.execute('''
    INSERT OR IGNORE INTO complementos (nome, preco)
    VALUES ('Bombom', 3.50);
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS itens_carrinho (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        carrinho_id INTEGER NOT NULL,
        tamanho_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER NOT NULL CHECK (quantidade > 0),

        FOREIGN KEY (carrinho_id)
            REFERENCES carrinho(id),

        FOREIGN KEY (tamanho_id)
            REFERENCES tamanhos(id),

        FOREIGN KEY (produto_id)
            REFERENCES produtos(id)
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_cremes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        creme_id INTEGER NOT NULL,

        UNIQUE (item_id, creme_id),

        FOREIGN KEY (item_id)
            REFERENCES itens_carrinho(id),

        FOREIGN KEY (creme_id)
            REFERENCES cremes(id)
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_frutas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        fruta_id INTEGER NOT NULL,

        UNIQUE (item_id, fruta_id),

        FOREIGN KEY (item_id)
            REFERENCES itens_carrinho(id),

        FOREIGN KEY (fruta_id)
            REFERENCES frutas(id)
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_complementos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        complemento_id INTEGER NOT NULL,

        UNIQUE (item_id, complemento_id),

        FOREIGN KEY (item_id)
            REFERENCES itens_carrinho(id),

        FOREIGN KEY (complemento_id)
            REFERENCES complementos(id)
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        preco DECIMAL NOT NULL
    )
''')

cursor.execute('''
    DELETE FROM produtos
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM produtos
        GROUP BY nome
    )
''')

conexao.commit()
conexao.close()
print(" Banco atualizado ")