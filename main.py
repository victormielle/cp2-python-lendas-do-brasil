"""
CP2 Python — Lendas do Brasil: RPG de batalha por turnos com POO.

Execute com:  python main.py
"""
import random
import sys
from copy import deepcopy

from batalha import batalha_1v1, batalha_3v3, ler_opcao, titulo
from monstros import Boitata, Curupira, Lobisomem, MulaSemCabeca, Saci
from personagens import Arqueiro, Guerreiro, Mago, Paladino


# ----------------------------------------------------------------------
# Instanciação dos objetos
# ----------------------------------------------------------------------
def criar_herois() -> list:
    return [
        Guerreiro("Bento Machado"),
        Mago("Celeste"),
        Arqueiro("Jacira"),
        Paladino("Frei Anselmo"),
    ]


def criar_monstros() -> list:
    return [Lobisomem(), Boitata(), Curupira(), MulaSemCabeca(), Saci()]


# ----------------------------------------------------------------------
# Menus de escolha
# ----------------------------------------------------------------------
def escolher_da_lista(mensagem: str, lista: list):
    print(f"\n{mensagem}")
    for i, item in enumerate(lista, start=1):
        print(f"  {i} - {item.nome} ({item.__class__.__name__})")
    return lista[ler_opcao("Escolha: ", 1, len(lista)) - 1]


def escolher_time(herois: list, tamanho: int = 3) -> list:
    disponiveis = list(herois)
    equipe = []
    while len(equipe) < tamanho:
        heroi = escolher_da_lista(f"Escolha o herói {len(equipe) + 1} de {tamanho}:",
                                  disponiveis)
        equipe.append(heroi)
        disponiveis.remove(heroi)
    return equipe


def mostrar_fichas(herois: list, monstros: list) -> None:
    titulo("FICHAS DOS HERÓIS")
    for heroi in herois:
        print(heroi.ficha() + "\n")
    titulo("FICHAS DOS MONSTROS")
    for monstro in monstros:
        print(monstro.ficha() + "\n")


# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # evita erro de emoji no Windows
    except AttributeError:
        pass

    # Catálogo "original". Cada batalha usa deepcopy() dele, assim os
    # objetos originais continuam intactos (HP e MP cheios) para a próxima luta.
    herois = criar_herois()
    monstros = criar_monstros()

    titulo("⚔  LENDAS DO BRASIL — RPG DE TURNOS  ⚔")
    print("Criaturas do folclore invadiram a vila. Monte sua equipe e defenda-a!")

    while True:
        print("\n----------------- MENU -----------------")
        print("1 - Batalha 1v1 (automática)")
        print("2 - Batalha 1v1 (você controla o herói)")
        print("3 - Batalha 3v3 (automática)")
        print("4 - Batalha 3v3 (você controla os heróis)")
        print("5 - Ver fichas de heróis e monstros")
        print("0 - Sair")
        opcao = ler_opcao("Opção: ", 0, 5)

        if opcao in (1, 2):
            heroi = deepcopy(escolher_da_lista("Escolha seu herói:", herois))
            monstro = deepcopy(escolher_da_lista("Escolha o monstro:", monstros))
            batalha_1v1(heroi, monstro, manual=(opcao == 2))
        elif opcao in (3, 4):
            equipe = deepcopy(escolher_time(herois))
            inimigos = deepcopy(random.sample(monstros, 3))  # 3 monstros sorteados
            batalha_3v3(equipe, inimigos, manual=(opcao == 4))
        elif opcao == 5:
            mostrar_fichas(herois, monstros)
        else:
            print("Até a próxima aventura!")
            break


if __name__ == "__main__":
    main()
