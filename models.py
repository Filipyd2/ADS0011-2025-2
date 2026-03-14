from datetime import date
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Plataforma(Base):
    __tablename__ = "plataforma"
    __table_args__ = (UniqueConstraint("nome", name="uq_plataforma_nome"),)

    id_plataforma = Column(Integer, primary_key=True, autoincrement=True)
    nome          = Column(String(50), nullable=False)
    descricao     = Column(String(50))
    observacao    = Column(String(50))

    jogos = relationship("Jogo", back_populates="plataforma")

    def __init__(self, nome, descricao=None, observacao=None):
        self.nome = nome
        self.descricao = descricao
        self.observacao = observacao

    def __repr__(self):
        return f"<Plataforma(id={self.id_plataforma}, nome='{self.nome}')>"


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (UniqueConstraint("login", name="uq_usuario_login"),)

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nome       = Column(String(150), nullable=False)
    login      = Column(String(50), nullable=False)
    senha      = Column(String(50), nullable=False)

    colecoes      = relationship("Colecao", back_populates="usuario", cascade="all, delete-orphan")
    usuario_jogos = relationship("UsuarioJogo", back_populates="usuario", cascade="all, delete-orphan")

    def __init__(self, nome, login, senha):
        self.nome = nome
        self.login = login
        self.senha = senha

    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, login='{self.login}')>"


class Jogo(Base):
    __tablename__ = "jogo"
    __table_args__ = (
        CheckConstraint("ano_lancamento > 1950", name="chk_ano_lancamento"),
    )

    id_jogo        = Column(Integer, primary_key=True, autoincrement=True)
    titulo         = Column(String(150), nullable=False)
    genero         = Column(String(50), nullable=False)
    id_plataforma  = Column(Integer, ForeignKey("plataforma.id_plataforma", ondelete="RESTRICT"), nullable=False)
    ano_lancamento = Column(Integer, nullable=False)
    horas_jogadas  = Column(Numeric(5, 2), default=0)

    plataforma    = relationship("Plataforma", back_populates="jogos")
    usuario_jogos = relationship("UsuarioJogo", back_populates="jogo", cascade="all, delete-orphan")

    def __init__(self, titulo, genero, id_plataforma, ano_lancamento, horas_jogadas=0):
        self.titulo = titulo
        self.genero = genero
        self.id_plataforma = id_plataforma
        self.ano_lancamento = ano_lancamento
        self.horas_jogadas = horas_jogadas

    def __repr__(self):
        return f"<Jogo(id={self.id_jogo}, titulo='{self.titulo}')>"


class Colecao(Base):
    __tablename__ = "colecao"

    id_colecao   = Column(Integer, primary_key=True, autoincrement=True)
    nome         = Column(String(150), nullable=False)
    descricao    = Column(String(255), nullable=False)
    data_criacao = Column(Date, default=date.today)
    id_usuario   = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False)

    usuario = relationship("Usuario", back_populates="colecoes")

    def __init__(self, nome, descricao, id_usuario, data_criacao=None):
        self.nome = nome
        self.descricao = descricao
        self.id_usuario = id_usuario
        self.data_criacao = data_criacao or date.today()

    def __repr__(self):
        return f"<Colecao(id={self.id_colecao}, nome='{self.nome}')>"


class UsuarioJogo(Base):
    __tablename__ = "usuario_jogo"
    __table_args__ = (
        CheckConstraint("avaliacao BETWEEN 0 AND 10", name="chk_avaliacao"),
        CheckConstraint("status IN (1, 2, 3)", name="chk_status"),
    )

    id_usuario  = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)
    id_jogo     = Column(Integer, ForeignKey("jogo.id_jogo", ondelete="CASCADE"), primary_key=True)
    data_inicio = Column(Date, default=date.today)
    data_fim    = Column(Date)
    avaliacao   = Column(Integer, nullable=False)
    status      = Column(Integer, nullable=False)

    usuario = relationship("Usuario", back_populates="usuario_jogos")
    jogo    = relationship("Jogo", back_populates="usuario_jogos")

    def __init__(self, id_usuario, id_jogo, avaliacao, status, data_inicio=None, data_fim=None):
        self.id_usuario = id_usuario
        self.id_jogo = id_jogo
        self.avaliacao = avaliacao
        self.status = status
        self.data_inicio = data_inicio or date.today()
        self.data_fim = data_fim

    def __repr__(self):
        return f"<UsuarioJogo(usuario={self.id_usuario}, jogo={self.id_jogo}, status={self.status})>"
