from datetime import date
from sqlalchemy.orm import Session
from models import Plataforma, Usuario, Jogo, Colecao, UsuarioJogo


# ──────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────

def criar_plataforma(session: Session, nome: str, descricao: str = None, observacao: str = None) -> Plataforma:
    plataforma = Plataforma(nome=nome, descricao=descricao, observacao=observacao)
    session.add(plataforma)
    session.commit()
    session.refresh(plataforma)
    return plataforma


def criar_usuario(session: Session, nome: str, login: str, senha: str) -> Usuario:
    usuario = Usuario(nome=nome, login=login, senha=senha)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def criar_jogo(session: Session, titulo: str, genero: str, id_plataforma: int, ano_lancamento: int) -> Jogo:
    jogo = Jogo(titulo=titulo, genero=genero, id_plataforma=id_plataforma, ano_lancamento=ano_lancamento)
    session.add(jogo)
    session.commit()
    session.refresh(jogo)
    return jogo


def criar_colecao(session: Session, nome: str, descricao: str, id_usuario: int) -> Colecao:
    colecao = Colecao(nome=nome, descricao=descricao, id_usuario=id_usuario)
    session.add(colecao)
    session.commit()
    session.refresh(colecao)
    return colecao


def adicionar_jogo_usuario(
    session: Session,
    id_usuario: int,
    id_jogo: int,
    avaliacao: int,
    status: int,
    data_inicio: date = None,
    data_fim: date = None,
) -> UsuarioJogo:
    uj = UsuarioJogo(
        id_usuario=id_usuario,
        id_jogo=id_jogo,
        avaliacao=avaliacao,
        status=status,
        data_inicio=data_inicio or date.today(),
        data_fim=data_fim or date.today(),
    )
    session.add(uj)
    session.commit()
    session.refresh(uj)
    return uj


# ──────────────────────────────────────────────
# READ
# ──────────────────────────────────────────────

def listar_jogos(session: Session, offset: int = 0, limit: int = 10) -> list[Jogo]:
    """Lista jogos com paginação simples, ordenados por título."""
    return (
        session.query(Jogo)
        .order_by(Jogo.titulo)
        .offset(offset)
        .limit(limit)
        .all()
    )


def listar_usuarios(session: Session) -> list[Usuario]:
    return session.query(Usuario).order_by(Usuario.nome).all()


def buscar_jogo_por_id(session: Session, id_jogo: int) -> Jogo | None:
    return session.get(Jogo, id_jogo)


def buscar_usuario_por_id(session: Session, id_usuario: int) -> Usuario | None:
    return session.get(Usuario, id_usuario)


# ──────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────

def atualizar_avaliacao_jogo_usuario(
    session: Session, id_usuario: int, id_jogo: int, nova_avaliacao: int
) -> UsuarioJogo | None:
    uj = session.get(UsuarioJogo, (id_usuario, id_jogo))
    if uj:
        uj.avaliacao = nova_avaliacao
        session.commit()
        session.refresh(uj)
    return uj


def atualizar_status_jogo_usuario(
    session: Session, id_usuario: int, id_jogo: int, novo_status: int
) -> UsuarioJogo | None:
    uj = session.get(UsuarioJogo, (id_usuario, id_jogo))
    if uj:
        uj.status = novo_status
        session.commit()
        session.refresh(uj)
    return uj


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

def remover_jogo_da_biblioteca(session: Session, id_usuario: int, id_jogo: int) -> bool:
    """Remove o vínculo entre usuário e jogo respeitando a integridade referencial."""
    uj = session.get(UsuarioJogo, (id_usuario, id_jogo))
    if uj:
        session.delete(uj)
        session.commit()
        return True
    return False


def remover_colecao(session: Session, id_colecao: int) -> bool:
    colecao = session.get(Colecao, id_colecao)
    if colecao:
        session.delete(colecao)
        session.commit()
        return True
    return False
