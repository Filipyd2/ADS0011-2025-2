"""CRUD interativo via console — Biblioteca de Jogos"""
from datetime import date
from database import Session
from crud import (
    criar_plataforma, criar_usuario, criar_jogo, criar_colecao,
    adicionar_jogo_usuario, listar_jogos, listar_usuarios,
    atualizar_avaliacao_jogo_usuario, atualizar_status_jogo_usuario,
    remover_jogo_da_biblioteca, remover_colecao,
    buscar_jogo_por_id, buscar_usuario_por_id,
)
from queries import jogos_do_usuario, usuarios_que_jogaram_genero, top10_jogos_mais_bem_avaliados
from models import Plataforma, Colecao, UsuarioJogo

STATUS_LABEL = {1: "Planejado", 2: "Jogando", 3: "Concluído"}


# ── helpers ────────────────────────────────────────────────────────────────

def cabecalho(titulo: str) -> None:
    print(f"\n{'═'*55}")
    print(f"  {titulo}")
    print('═'*55)

def pausar() -> None:
    input("\n  [Enter para continuar]")

def ler_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  Digite um número inteiro válido.")

def ler_data(prompt: str) -> date:
    while True:
        s = input(prompt + " (AAAA-MM-DD): ").strip()
        try:
            return date.fromisoformat(s)
        except ValueError:
            print("  Formato inválido. Use AAAA-MM-DD.")

def menu(titulo: str, opcoes: list[str]) -> str:
    cabecalho(titulo)
    for op in opcoes:
        print(f"  {op}")
    return input("\n  Opção: ").strip()


# ── plataformas ────────────────────────────────────────────────────────────

def menu_plataformas(session) -> None:
    while True:
        op = menu("PLATAFORMAS", [
            "1. Listar", "2. Inserir", "3. Remover", "0. Voltar",
        ])

        if op == "1":
            cabecalho("Listar Plataformas")
            rows = session.query(Plataforma).order_by(Plataforma.nome).all()
            if not rows:
                print("  Nenhuma plataforma cadastrada.")
            for p in rows:
                print(f"  [{p.id_plataforma}] {p.nome} — {p.descricao or '-'}")
            pausar()

        elif op == "2":
            cabecalho("Inserir Plataforma")
            nome      = input("  Nome: ").strip()
            descricao = input("  Descrição (opcional): ").strip() or None
            obs       = input("  Observação (opcional): ").strip() or None
            try:
                p = criar_plataforma(session, nome, descricao, obs)
                print(f"  Criada: {p}")
            except Exception as e:
                session.rollback()
                print(f"  Erro: {e}")
            pausar()

        elif op == "3":
            cabecalho("Remover Plataforma")
            id_ = ler_int("  ID da plataforma: ")
            p = session.get(Plataforma, id_)
            if not p:
                print("  Plataforma não encontrada.")
            else:
                confirma = input(f"  Remover '{p.nome}'? (s/n): ").strip().lower()
                if confirma == "s":
                    try:
                        session.delete(p)
                        session.commit()
                        print("  Removida com sucesso.")
                    except Exception as e:
                        session.rollback()
                        print(f"  Erro: {e}")
            pausar()

        elif op == "0":
            break


# ── usuários ───────────────────────────────────────────────────────────────

def menu_usuarios(session) -> None:
    while True:
        op = menu("USUÁRIOS", [
            "1. Listar", "2. Inserir", "3. Atualizar nome/senha", "4. Remover", "0. Voltar",
        ])

        if op == "1":
            cabecalho("Listar Usuários")
            for u in listar_usuarios(session):
                print(f"  [{u.id_usuario}] {u.nome}  |  login: {u.login}")
            pausar()

        elif op == "2":
            cabecalho("Inserir Usuário")
            nome  = input("  Nome completo: ").strip()
            login = input("  Login: ").strip()
            senha = input("  Senha: ").strip()
            try:
                u = criar_usuario(session, nome, login, senha)
                print(f"  Criado: {u}")
            except Exception as e:
                session.rollback()
                print(f"  Erro: {e}")
            pausar()

        elif op == "3":
            cabecalho("Atualizar Usuário")
            id_ = ler_int("  ID do usuário: ")
            u = buscar_usuario_por_id(session, id_)
            if not u:
                print("  Usuário não encontrado.")
            else:
                print(f"  Usuário atual: {u.nome} | login: {u.login}")
                novo_nome = input(f"  Novo nome [{u.nome}]: ").strip() or u.nome
                nova_senha = input("  Nova senha (deixe em branco para manter): ").strip()
                u.nome = novo_nome
                if nova_senha:
                    u.senha = nova_senha
                try:
                    session.commit()
                    print("  Atualizado com sucesso.")
                except Exception as e:
                    session.rollback()
                    print(f"  Erro: {e}")
            pausar()

        elif op == "4":
            cabecalho("Remover Usuário")
            id_ = ler_int("  ID do usuário: ")
            u = buscar_usuario_por_id(session, id_)
            if not u:
                print("  Usuário não encontrado.")
            else:
                confirma = input(f"  Remover '{u.nome}'? Isso apagará suas coleções e biblioteca. (s/n): ").strip().lower()
                if confirma == "s":
                    try:
                        session.delete(u)
                        session.commit()
                        print("  Removido com sucesso.")
                    except Exception as e:
                        session.rollback()
                        print(f"  Erro: {e}")
            pausar()

        elif op == "0":
            break


# ── jogos ──────────────────────────────────────────────────────────────────

def menu_jogos(session) -> None:
    while True:
        op = menu("JOGOS", [
            "1. Listar", "2. Inserir", "3. Atualizar horas jogadas", "4. Remover", "0. Voltar",
        ])

        if op == "1":
            cabecalho("Listar Jogos")
            offset = 0
            while True:
                jogos = listar_jogos(session, offset=offset, limit=10)
                if not jogos:
                    print("  Sem mais jogos.")
                    break
                for j in jogos:
                    print(f"  [{j.id_jogo}] {j.titulo} ({j.ano_lancamento}) | {j.genero} | Plat: {j.id_plataforma}")
                if len(jogos) < 10:
                    break
                continuar = input("\n  Próxima página? (s/n): ").strip().lower()
                if continuar != "s":
                    break
                offset += 10
            pausar()

        elif op == "2":
            cabecalho("Inserir Jogo")
            titulo = input("  Título: ").strip()
            genero = input("  Gênero: ").strip()
            id_plat = ler_int("  ID da plataforma: ")
            ano = ler_int("  Ano de lançamento: ")
            try:
                j = criar_jogo(session, titulo, genero, id_plat, ano)
                print(f"  Criado: {j}")
            except Exception as e:
                session.rollback()
                print(f"  Erro: {e}")
            pausar()

        elif op == "3":
            cabecalho("Atualizar Horas Jogadas")
            id_ = ler_int("  ID do jogo: ")
            j = buscar_jogo_por_id(session, id_)
            if not j:
                print("  Jogo não encontrado.")
            else:
                print(f"  Jogo: {j.titulo} | Horas atuais: {j.horas_jogadas}")
                try:
                    horas = float(input("  Horas a adicionar: "))
                    j.horas_jogadas = float(j.horas_jogadas or 0) + horas
                    session.commit()
                    print(f"  Atualizado. Total: {j.horas_jogadas}h")
                except Exception as e:
                    session.rollback()
                    print(f"  Erro: {e}")
            pausar()

        elif op == "4":
            cabecalho("Remover Jogo")
            id_ = ler_int("  ID do jogo: ")
            j = buscar_jogo_por_id(session, id_)
            if not j:
                print("  Jogo não encontrado.")
            else:
                confirma = input(f"  Remover '{j.titulo}'? (s/n): ").strip().lower()
                if confirma == "s":
                    try:
                        session.delete(j)
                        session.commit()
                        print("  Removido com sucesso.")
                    except Exception as e:
                        session.rollback()
                        print(f"  Erro: {e}")
            pausar()

        elif op == "0":
            break


# ── coleções ───────────────────────────────────────────────────────────────

def menu_colecoes(session) -> None:
    while True:
        op = menu("COLEÇÕES", [
            "1. Listar", "2. Inserir", "3. Remover", "0. Voltar",
        ])

        if op == "1":
            cabecalho("Listar Coleções")
            rows = session.query(Colecao).order_by(Colecao.nome).all()
            if not rows:
                print("  Nenhuma coleção cadastrada.")
            for c in rows:
                print(f"  [{c.id_colecao}] {c.nome} | Usuário: {c.id_usuario} | Criada: {c.data_criacao}")
            pausar()

        elif op == "2":
            cabecalho("Inserir Coleção")
            nome      = input("  Nome: ").strip()
            descricao = input("  Descrição: ").strip()
            id_usu    = ler_int("  ID do usuário dono: ")
            try:
                c = criar_colecao(session, nome, descricao, id_usu)
                print(f"  Criada: {c}")
            except Exception as e:
                session.rollback()
                print(f"  Erro: {e}")
            pausar()

        elif op == "3":
            cabecalho("Remover Coleção")
            id_ = ler_int("  ID da coleção: ")
            if remover_colecao(session, id_):
                print("  Removida com sucesso.")
            else:
                print("  Coleção não encontrada.")
            pausar()

        elif op == "0":
            break


# ── biblioteca (usuário-jogo) ───────────────────────────────────────────────

def menu_biblioteca(session) -> None:
    while True:
        op = menu("BIBLIOTECA (Usuário ↔ Jogo)", [
            "1. Listar biblioteca de um usuário",
            "2. Adicionar jogo à biblioteca",
            "3. Atualizar avaliação",
            "4. Atualizar status",
            "5. Remover jogo da biblioteca",
            "0. Voltar",
        ])

        if op == "1":
            cabecalho("Biblioteca do Usuário")
            id_ = ler_int("  ID do usuário: ")
            itens = jogos_do_usuario(session, id_)
            if not itens:
                print("  Nenhum jogo na biblioteca.")
            for item in itens:
                print(f"  {item['titulo']} | {item['plataforma']} | "
                      f"Nota: {item['avaliacao']}/10 | Status: {item['status']} | "
                      f"Início: {item['data_inicio']} | Fim: {item['data_fim']}")
            pausar()

        elif op == "2":
            cabecalho("Adicionar Jogo à Biblioteca")
            id_usu  = ler_int("  ID do usuário: ")
            id_jogo = ler_int("  ID do jogo: ")
            aval    = ler_int("  Avaliação (0-10): ")
            print("  Status: 1-Planejado  2-Jogando  3-Concluído")
            status  = ler_int("  Status: ")
            data_inicio = ler_data("  Data de início")
            data_fim    = ler_data("  Data de fim (ou data futura se ainda jogando)")
            try:
                uj = adicionar_jogo_usuario(session, id_usu, id_jogo, aval, status, data_inicio, data_fim)
                print(f"  Adicionado: {uj}")
            except Exception as e:
                session.rollback()
                print(f"  Erro: {e}")
            pausar()

        elif op == "3":
            cabecalho("Atualizar Avaliação")
            id_usu  = ler_int("  ID do usuário: ")
            id_jogo = ler_int("  ID do jogo: ")
            nova    = ler_int("  Nova avaliação (0-10): ")
            uj = atualizar_avaliacao_jogo_usuario(session, id_usu, id_jogo, nova)
            if uj:
                print(f"  Atualizado: {uj}")
            else:
                print("  Registro não encontrado.")
            pausar()

        elif op == "4":
            cabecalho("Atualizar Status")
            id_usu  = ler_int("  ID do usuário: ")
            id_jogo = ler_int("  ID do jogo: ")
            print("  1-Planejado  2-Jogando  3-Concluído")
            novo = ler_int("  Novo status: ")
            uj = atualizar_status_jogo_usuario(session, id_usu, id_jogo, novo)
            if uj:
                print(f"  Atualizado: {uj}")
            else:
                print("  Registro não encontrado.")
            pausar()

        elif op == "5":
            cabecalho("Remover Jogo da Biblioteca")
            id_usu  = ler_int("  ID do usuário: ")
            id_jogo = ler_int("  ID do jogo: ")
            if remover_jogo_da_biblioteca(session, id_usu, id_jogo):
                print("  Removido com sucesso.")
            else:
                print("  Registro não encontrado.")
            pausar()

        elif op == "0":
            break


# ── consultas ──────────────────────────────────────────────────────────────

def menu_consultas(session) -> None:
    while True:
        op = menu("CONSULTAS", [
            "1. Biblioteca completa de um usuário (JOIN Jogo + Plataforma)",
            "2. Usuários que jogaram determinado gênero",
            "3. Top 10 jogos por média de avaliação",
            "0. Voltar",
        ])

        if op == "1":
            cabecalho("Consulta Q1 — Biblioteca do Usuário")
            id_ = ler_int("  ID do usuário: ")
            itens = jogos_do_usuario(session, id_)
            if not itens:
                print("  Nenhum resultado.")
            for item in itens:
                print(f"  {item['titulo']:<45} {item['plataforma']:<20} "
                      f"Nota: {item['avaliacao']:>2}/10  Status: {item['status']}")
            pausar()

        elif op == "2":
            cabecalho("Consulta Q2 — Usuários por Gênero")
            genero = input("  Gênero: ").strip()
            itens = usuarios_que_jogaram_genero(session, genero)
            if not itens:
                print("  Nenhum resultado.")
            for item in itens:
                print(f"  {item['usuario']:<30} jogou '{item['jogo']}' — Nota: {item['avaliacao']}")
            pausar()

        elif op == "3":
            cabecalho("Consulta Q3 — Top 10 por Média de Avaliação")
            itens = top10_jogos_mais_bem_avaliados(session)
            if not itens:
                print("  Nenhum resultado.")
            for i, item in enumerate(itens, start=1):
                print(f"  {i:>2}. {item['titulo']:<45} Média: {item['media_avaliacao']:.2f} "
                      f"({item['total_avaliacoes']} aval.) | {item['plataforma']}")
            pausar()

        elif op == "0":
            break


# ── main ───────────────────────────────────────────────────────────────────

def main() -> None:
    session = Session()
    try:
        while True:
            op = menu("BIBLIOTECA DE JOGOS — MENU PRINCIPAL", [
                "1. Plataformas",
                "2. Usuários",
                "3. Jogos",
                "4. Coleções",
                "5. Biblioteca (Usuário ↔ Jogo)",
                "6. Consultas",
                "0. Sair",
            ])

            if op == "1":
                menu_plataformas(session)
            elif op == "2":
                menu_usuarios(session)
            elif op == "3":
                menu_jogos(session)
            elif op == "4":
                menu_colecoes(session)
            elif op == "5":
                menu_biblioteca(session)
            elif op == "6":
                menu_consultas(session)
            elif op == "0":
                print("\n  Encerrando. Até logo!\n")
                break
    finally:
        session.close()


if __name__ == "__main__":
    main()
