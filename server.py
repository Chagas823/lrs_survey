from database import db, create_app
from model.models import Participante, Pesquisa, Pergunta, Resposta, Link, ModeloChave, RespostaPesquisa

with create_app().app_context():
    db.create_all()  # Cria as tabelas no banco de dados
