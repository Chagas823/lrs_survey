from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import db
from datetime import datetime

# Tabela associativa para Grupo e Pesquisa (muitos para muitos)
grupo_pesquisa = db.Table('grupo_pesquisa',
    db.Column('grupo_id', db.Integer, db.ForeignKey('grupo.id'), primary_key=True),
    db.Column('pesquisa_id', db.Integer, db.ForeignKey('pesquisas.id'), primary_key=True)
)

class Participante(db.Model):
    __tablename__ = 'participantes'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    chave_publica = Column(String, nullable=False)

    grupos = db.relationship('Grupo', secondary='grupo_participante', back_populates='participantes')


class Grupo(db.Model):
    __tablename__ = 'grupo'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255))
    data_criacao = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento com Participante
    participantes = db.relationship('Participante', secondary='grupo_participante', back_populates='grupos')

    # Relacionamento com RespostaPesquisa
    respostas_pesquisa = relationship("RespostaPesquisa", back_populates="grupo")
    
    # Relacionamento muitos para muitos com Pesquisa
    pesquisas = db.relationship('Pesquisa', secondary='grupo_pesquisa', back_populates='grupos')


class Pesquisa(db.Model):
    __tablename__ = 'pesquisas'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento com Pergunta
    perguntas = relationship("Pergunta", back_populates="pesquisa")

    # Relacionamento muitos para muitos com Grupo
    grupos = db.relationship('Grupo', secondary='grupo_pesquisa', back_populates='pesquisas')


# Relação muitos para muitos entre Participante e Grupo
grupo_participante = db.Table('grupo_participante',
    db.Column('grupo_id', db.Integer, db.ForeignKey('grupo.id'), primary_key=True),
    db.Column('participante_id', db.Integer, db.ForeignKey('participantes.id'), primary_key=True)
)


class Pergunta(db.Model):
    __tablename__ = 'perguntas'
    
    id = Column(Integer, primary_key=True)
    texto = Column(String, nullable=False)
    tipo = Column(String, nullable=False)

    # Relacionamento com Pesquisa
    pesquisa_id = Column(Integer, ForeignKey('pesquisas.id'))
    pesquisa = relationship("Pesquisa", back_populates="perguntas")

    # Relacionamento com Respostas
    respostas = relationship("Resposta", back_populates="pergunta")


class Resposta(db.Model):
    __tablename__ = 'respostas'
    
    id = Column(Integer, primary_key=True)
    conteudo = Column(String, nullable=False)

    # Relacionamento com Pergunta
    pergunta_id = Column(Integer, ForeignKey('perguntas.id'))
    pergunta = relationship("Pergunta", back_populates="respostas")
    
    # Relacionamento com RespostaPesquisa
    resposta_pesquisa_id = Column(Integer, ForeignKey('resposta_pesquisa.id'))
    resposta_pesquisa = relationship("RespostaPesquisa", back_populates="respostas")


class Assinatura(db.Model):
    __tablename__ = 'assinaturas'
    
    id = Column(Integer, primary_key=True)
    y0 = Column(String, nullable=False)  # Altere o tipo de acordo com sua necessidade
    s_values = Column(String, nullable=False)  # Altere o tipo de acordo com sua necessidade
    c_values = Column(String, nullable=False)  # Altere o tipo de acordo com sua necessidade
    r = Column(String, nullable=False)  # Altere o tipo de acordo com sua necessidade

    # Relacionamento com RespostaPesquisa
    resposta_pesquisa = relationship("RespostaPesquisa", back_populates="assinatura")


class RespostaPesquisa(db.Model):
    __tablename__ = 'resposta_pesquisa'

    id = Column(Integer, primary_key=True)
    assinatura_id = Column(Integer, ForeignKey('assinaturas.id'))  # Nova coluna para referência
    assinatura = relationship("Assinatura", back_populates="resposta_pesquisa")

    # Relacionamento com Respostas
    respostas = relationship("Resposta", back_populates="resposta_pesquisa")
    
    # Relacionamento com Grupo
    grupo_id = Column(Integer, ForeignKey('grupo.id'))
    grupo = relationship("Grupo", back_populates="respostas_pesquisa")

    # Nova coluna pesquisa_id
    pesquisa_id = Column(Integer, ForeignKey('pesquisas.id'))

    # Relacionamento com Pesquisa
    pesquisa = relationship("Pesquisa")  # Removemos o back_populates para evitar o erro


class Link(db.Model):
    __tablename__ = 'links'
    
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    utilizado = Column(Boolean, default=False)

    # Relacionamento com Participante
    participante_id = Column(Integer, ForeignKey('participantes.id'))
    participante = relationship("Participante")


class ModeloChave(db.Model):
    __tablename__ = 'modelos_chave'
    
    id = Column(Integer, primary_key=True)
    chave_privada = Column(String, nullable=False)
    chave_publica = Column(String, nullable=False)

    # Relacionamento com Participante
    participante_id = Column(Integer, ForeignKey('participantes.id'))
    participante = relationship("Participante")
