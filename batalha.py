"""
Módulo com os sistemas de batalha 1v1 e 3v3.

As funções tratam heróis e monstros da mesma forma: chamam escolher_alvo()
e atacar() sem saber a classe exata de quem está agindo (polimorfismo).
"""
import time

from personagens import Personagem

PAUSA = 0.4            # segundos entre as ações (deixa o combate legível)
LIMITE_RODADAS = 50    # evita batalhas infinitas


# ----------------------------------------------------------------------
# Funções auxiliares
# ----------------------------------------------------------------------
def pausar() -> None:
    if PAUSA > 0:
        time.sleep(PAUSA)


def titulo(texto: str) -> None:
    print("\n" + "=" * 64)
    print(f"{texto:^64}")
    print("=" * 64)


def vivos(equipe: list) -> list:
    return [membro for membro in equipe if membro.esta_vivo()]


def time_derrotado(equipe: list) -> bool:
    """Um time perde quando todos os membros estão com hp <= 0."""
    return len(vivos(equipe)) == 0


def ler_opcao(mensagem: str, minimo: int, maximo: int) -> int:
    """Lê um número inteiro do teclado, repetindo até a opção ser válida."""
    while True:
        entrada = input(mensagem).strip()
        if entrada.isdigit() and minimo <= int(entrada) <= maximo:
            return int(entrada)
        print(f"   Opção inválida! Digite um número entre {minimo} e {maximo}.")


def mostrar_times(herois: list, monstros: list) -> None:
    print("\n   HERÓIS")
    for heroi in herois:
        print(f"   {heroi}")
    print("   MONSTROS")
    for monstro in monstros:
        print(f"   {monstro}")


# ----------------------------------------------------------------------
# Turnos
# ----------------------------------------------------------------------
def escolher_ataque_manual(heroi: Personagem):
    """Lista os ataques do herói e só aceita os que ele tem mana para usar."""
    print("     Escolha o ataque:")
    for i, ataque in enumerate(heroi.ATAQUES, start=1):
        aviso = "" if ataque.custo <= heroi.mp else "  [sem mana]"
        print(f"       {i} - {ataque}{aviso}")
    while True:
        ataque = heroi.ATAQUES[ler_opcao("     Ataque: ", 1, len(heroi.ATAQUES)) - 1]
        if ataque.custo <= heroi.mp:
            return ataque
        print(f"   Mana insuficiente! {ataque.nome} custa {ataque.custo} MP "
              f"e {heroi.nome} tem {heroi.mp} MP.")


def turno_manual(heroi: Personagem, alvos: list) -> None:
    """O jogador escolhe a ação, o ataque e o alvo do herói via input()."""
    print(f"\n   ▶ Vez de {heroi.nome} ({heroi.__class__.__name__}) — "
          f"HP {heroi.hp}/{heroi.get_hp_max()} | MP {heroi.mp}/{heroi.get_mp_max()}")
    print("     1 - Atacar")
    print(f"     2 - Usar poção ({heroi.get_pocoes()} restante(s))")
    acao = ler_opcao("     Escolha: ", 1, 2)

    if acao == 2:
        if heroi.usar_pocao():
            return
        print("   Então o herói parte para o ataque!")

    ataque = escolher_ataque_manual(heroi)

    # Ataques de cura não precisam de alvo inimigo
    if ataque.tipo == "cura" or len(alvos) == 1:
        alvo = alvos[0]
    else:
        print("     Escolha o alvo:")
        for i, alvo in enumerate(alvos, start=1):
            print(f"       {i} - {alvo.nome} ({alvo.hp}/{alvo.get_hp_max()} HP)")
        alvo = alvos[ler_opcao("     Alvo: ", 1, len(alvos)) - 1]

    heroi.atacar(alvo, ataque)


def executar_turno(atacante, inimigos: list, manual: bool = False) -> None:
    """Executa a ação de um combatente contra o time inimigo."""
    alvos = vivos(inimigos)
    if not atacante.esta_vivo() or not alvos:
        return

    # Veneno e atordoamento são aplicados no início do turno
    if not atacante.processar_efeitos():
        return

    if isinstance(atacante, Personagem):
        if manual:
            turno_manual(atacante, alvos)
            return
        if atacante.precisa_de_pocao():
            atacante.usar_pocao()
            return

    # Polimorfismo: cada classe escolhe o alvo, o ataque e ataca do seu jeito
    alvo = atacante.escolher_alvo(alvos)
    atacante.atacar(alvo)


def anunciar_resultado(herois: list, monstros: list) -> str:
    titulo("FIM DA BATALHA")
    if time_derrotado(monstros):
        print("🏆 VITÓRIA! As lendas foram derrotadas e a vila está a salvo.")
        resultado = "herois"
    elif time_derrotado(herois):
        print("💀 DERROTA... O folclore venceu desta vez.")
        resultado = "monstros"
    else:
        print(f"⏳ EMPATE: a batalha passou de {LIMITE_RODADAS} rodadas.")
        resultado = "empate"

    destaque = max(herois, key=lambda heroi: heroi.dano_causado)
    print(f"⭐ Destaque dos heróis: {destaque.nome}, com {destaque.dano_causado} "
          f"de dano causado.")
    return resultado


# ----------------------------------------------------------------------
# Sistemas de batalha
# ----------------------------------------------------------------------
def batalha_1v1(heroi: Personagem, monstro, manual: bool = False) -> str:
    """Combate por turnos entre um herói e um monstro. A speed define quem começa."""
    titulo("BATALHA 1v1")
    print(f"{heroi.nome} ({heroi.__class__.__name__})  VS  {monstro.nome}")
    monstro.apresentar()

    if heroi.speed >= monstro.speed:
        primeiro, segundo = heroi, monstro
    else:
        primeiro, segundo = monstro, heroi

    if heroi.speed == monstro.speed:
        print(f"\n⚡ Velocidades empatadas ({heroi.speed}): o herói tem a iniciativa!")
    else:
        print(f"\n⚡ {primeiro.nome} (SPD {primeiro.speed}) é mais rápido que "
              f"{segundo.nome} (SPD {segundo.speed}) e ataca primeiro!")

    rodada = 1
    while heroi.esta_vivo() and monstro.esta_vivo() and rodada <= LIMITE_RODADAS:
        print(f"\n── Rodada {rodada} " + "─" * 40)
        for atacante, defensor in ((primeiro, segundo), (segundo, primeiro)):
            executar_turno(atacante, [defensor], manual)
            pausar()
        mostrar_times([heroi], [monstro])
        rodada += 1

    return anunciar_resultado([heroi], [monstro])


def batalha_3v3(herois: list, monstros: list, manual: bool = False) -> str:
    """Combate em equipe: a cada rodada todos agem em ordem de speed (maior primeiro)."""
    titulo("BATALHA 3v3")
    print("Heróis:   " + ", ".join(f"{h.nome} ({h.__class__.__name__})" for h in herois))
    print("Monstros: " + ", ".join(m.nome for m in monstros))
    print()
    for monstro in monstros:
        monstro.apresentar()

    rodada = 1
    while (not time_derrotado(herois) and not time_derrotado(monstros)
           and rodada <= LIMITE_RODADAS):
        print(f"\n── Rodada {rodada} " + "─" * 40)
        # sorted() é estável: em caso de empate de speed, os heróis agem antes
        ordem = sorted(vivos(herois) + vivos(monstros),
                       key=lambda combatente: combatente.speed, reverse=True)
        print("   Ordem: " + " → ".join(c.nome for c in ordem) + "\n")

        for atacante in ordem:
            if time_derrotado(herois) or time_derrotado(monstros):
                break
            inimigos = monstros if isinstance(atacante, Personagem) else herois
            executar_turno(atacante, inimigos, manual)
            pausar()

        mostrar_times(herois, monstros)
        rodada += 1

    return anunciar_resultado(herois, monstros)
