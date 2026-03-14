"""
Consultas com relacionamento (equivalente a JOIN) via ORM.

Parte 4 dos requisitos:
  - Q1: listar jogos de um usuário trazendo título do jogo e nome da plataforma (JOIN)
  - Q2: listar usuários que jogaram um jogo específico por gênero (filtro em tabela relacionada)
  - Q3: top 10 jogos com maior média de avaliação, ordenados desc (filtro + ordenação)
"""
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import Usuario, Jogo, Plataforma, UsuarioJogo


def jogos_do_usuario(session: Session, id_usuario: int) -> list[dict]:
    STATUS_LABEL = {1: "Planejado", 2: "Jogando", 3: "Concluído"}

    resultados = (
        session.query(
            Jogo.titulo,
            Plataforma.nome.label("plataforma"),
            Jogo.genero,
            UsuarioJogo.avaliacao,
            UsuarioJogo.status,
            UsuarioJogo.data_inicio,
            UsuarioJogo.data_fim,
        )
        .join(UsuarioJogo, UsuarioJogo.id_jogo == Jogo.id_jogo)
        .join(Plataforma, Plataforma.id_plataforma == Jogo.id_plataforma)
        .filter(UsuarioJogo.id_usuario == id_usuario)
        .order_by(Jogo.titulo)
        .all()
    )

    return [
        {
            "titulo": r.titulo,
            "plataforma": r.plataforma,
            "genero": r.genero,
            "avaliacao": r.avaliacao,
            "status": STATUS_LABEL.get(r.status, str(r.status)),
            "data_inicio": r.data_inicio,
            "data_fim": r.data_fim,
        }
        for r in resultados
    ]


def usuarios_que_jogaram_genero(session: Session, genero: str) -> list[dict]:
    resultados = (
        session.query(
            Usuario.nome.label("usuario"),
            Usuario.login,
            Jogo.titulo,
            Jogo.genero,
            UsuarioJogo.avaliacao,
        )
        .join(UsuarioJogo, UsuarioJogo.id_usuario == Usuario.id_usuario)
        .join(Jogo, Jogo.id_jogo == UsuarioJogo.id_jogo)
        .filter(Jogo.genero.ilike(f"%{genero}%"))
        .order_by(Usuario.nome)
        .all()
    )

    return [
        {
            "usuario": r.usuario,
            "login": r.login,
            "jogo": r.titulo,
            "genero": r.genero,
            "avaliacao": r.avaliacao,
        }
        for r in resultados
    ]


def top10_jogos_mais_bem_avaliados(session: Session) -> list[dict]:
    resultados = (
        session.query(
            Jogo.titulo,
            Plataforma.nome.label("plataforma"),
            Jogo.genero,
            Jogo.ano_lancamento,
            func.round(func.avg(UsuarioJogo.avaliacao), 2).label("media_avaliacao"),
            func.count(UsuarioJogo.id_usuario).label("total_avaliacoes"),
        )
        .join(UsuarioJogo, UsuarioJogo.id_jogo == Jogo.id_jogo)
        .join(Plataforma, Plataforma.id_plataforma == Jogo.id_plataforma)
        .group_by(Jogo.id_jogo, Jogo.titulo, Plataforma.nome, Jogo.genero, Jogo.ano_lancamento)
        .order_by(func.avg(UsuarioJogo.avaliacao).desc())
        .limit(10)
        .all()
    )

    return [
        {
            "titulo": r.titulo,
            "plataforma": r.plataforma,
            "genero": r.genero,
            "ano": r.ano_lancamento,
            "media_avaliacao": float(r.media_avaliacao),
            "total_avaliacoes": r.total_avaliacoes,
        }
        for r in resultados
    ]
