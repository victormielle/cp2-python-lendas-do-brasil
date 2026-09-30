"""
Módulo dos monstros, inspirados no folclore brasileiro.

Monstro é a classe pai. Cada lenda tem sua própria lista de ataques e
sobrescreve atacar() e, em alguns casos, também escolher_alvo() ou
receber_dano() (polimorfismo).
"""
import random

from ataque import Ataque
from combatente import Combatente


class Monstro(Combatente):
    """Classe pai de todos os monstros."""

    def __init__(self, nome: str, hp: int, mp: int, speed: int, atk: int, matk: int,
                 defense: int, mdefense: int, lenda: str = ""):
        super().__init__(nome, hp, mp, speed, atk, matk, defense, mdefense)
        self.lenda = lenda

    def escolher_alvo(self, alvos: list) -> Combatente:
        """Instinto de caçador: 60% de chance de atacar o herói mais ferido."""
        if random.random() < 0.60:
            return min(alvos, key=lambda alvo: alvo.hp)
        return super().escolher_alvo(alvos)

    def apresentar(self) -> None:
        print(f"   📜 {self.nome}: {self.lenda}")

    def ficha(self) -> str:
        return super().ficha() + f"\n   Lenda: {self.lenda}"


class Lobisomem(Monstro):
    """Muito resistente. Abaixo de 50% do HP entra em fúria e aumenta o ATK."""

    ATAQUES = [
        Ataque("Garras", "fisico", 1.0, 0, "Ataque físico básico"),
        Ataque("Mordida Selvagem", "fisico", 1.2, 8, "Causa sangramento por 3 turnos"),
        Ataque("Salto Feroz", "fisico", 1.3, 12, "Salta sobre a presa com 1.3x o ATK"),
    ]

    def __init__(self, nome: str = "Lobisomem"):
        super().__init__(nome, hp=158, mp=30, speed=11, atk=28, matk=0,
                         defense=12, mdefense=6,
                         lenda="Homem amaldiçoado que vira lobo nas noites de lua cheia.")
        self._enfurecido = False

    def atacar(self, alvo: Combatente, ataque: Ataque = None) -> None:
        # Passiva: fúria da lua cheia
        if not self._enfurecido and self.hp < self.get_hp_max() / 2:
            self._enfurecido = True
            self.atk = int(self.atk * 1.3)
            print(f"   🌕 {self.nome} uiva para a lua cheia e entra em FÚRIA! (ATK {self.atk})")

        ataque = self.preparar_ataque(ataque)
        dano = self.golpe(ataque, alvo)
        if ataque.nome == "Mordida Selvagem" and dano > 0:
            self.envenenar(alvo, 6)


class Boitata(Monstro):
    """Serpente de fogo: especialista em ataques mágicos."""

    ATAQUES = [
        Ataque("Bote Flamejante", "fisico", 1.0, 0, "Ataque físico básico"),
        Ataque("Fogo Encantado", "magico", 1.0, 10, "Ataque mágico de fogo"),
        Ataque("Olhar Flamejante", "magico", 0.7, 12, "Ofusca o alvo; 35% de chance de atordoar"),
    ]

    def __init__(self, nome: str = "Boitatá"):
        super().__init__(nome, hp=150, mp=60, speed=9, atk=14, matk=36,
                         defense=12, mdefense=22,
                         lenda="Serpente de fogo que protege os campos de quem os incendeia.")

    def atacar(self, alvo: Combatente, ataque: Ataque = None) -> None:
        ataque = self.preparar_ataque(ataque)
        dano = self.golpe(ataque, alvo)
        if ataque.nome == "Olhar Flamejante" and dano > 0:
            self.tentar_atordoar(alvo, 0.35)


class Curupira(Monstro):
    """Muito veloz. Os pés virados para trás confundem os inimigos: 20% de esquiva."""

    CHANCE_ESQUIVA = 0.20
    ATAQUES = [
        Ataque("Armadilha da Mata", "fisico", 1.0, 0, "Ataque físico básico"),
        Ataque("Assobio Estridente", "magico", 1.0, 8, "25% de chance de atordoar"),
        Ataque("Cipó Venenoso", "fisico", 0.8, 10, "Envenena o alvo por 3 turnos"),
    ]

    def __init__(self, nome: str = "Curupira"):
        super().__init__(nome, hp=125, mp=30, speed=18, atk=28, matk=22,
                         defense=12, mdefense=12,
                         lenda="Guardião da mata com os pés virados para trás.")

    def receber_dano(self, dano: int) -> int:
        # Sobrescrita: antes de sofrer dano, o Curupira pode esquivar
        if random.random() < self.CHANCE_ESQUIVA:
            print(f"   🦶 Os pés virados confundem o atacante... {self.nome} esquivou!")
            return 0
        return super().receber_dano(dano)

    def atacar(self, alvo: Combatente, ataque: Ataque = None) -> None:
        ataque = self.preparar_ataque(ataque)
        dano = self.golpe(ataque, alvo)
        if ataque.nome == "Assobio Estridente" and dano > 0:
            self.tentar_atordoar(alvo, 0.25)
        elif ataque.nome == "Cipó Venenoso" and dano > 0:
            self.envenenar(alvo, 6)


class MulaSemCabeca(Monstro):
    """Mistura coices físicos e fogo mágico."""

    ATAQUES = [
        Ataque("Coice", "fisico", 1.0, 0, "Ataque físico básico"),
        Ataque("Labareda", "magico", 1.0, 8, "Fogo que sai do pescoço"),
        Ataque("Galope em Chamas", "fisico", 1.3, 14, "Atropela o alvo e o deixa em chamas"),
    ]

    def __init__(self, nome: str = "Mula sem Cabeça"):
        super().__init__(nome, hp=150, mp=28, speed=14, atk=29, matk=27,
                         defense=15, mdefense=12,
                         lenda="Mula que solta fogo pelo pescoço e galopa pelas noites.")

    def atacar(self, alvo: Combatente, ataque: Ataque = None) -> None:
        ataque = self.preparar_ataque(ataque)
        dano = self.golpe(ataque, alvo)
        if ataque.nome == "Galope em Chamas" and dano > 0:
            self.envenenar(alvo, 5)  # queimadura funciona como veneno


class Saci(Monstro):
    """O mais rápido de todos. Mira em quem tem mais mana e rouba parte dela."""

    MANA_ROUBADA = 6
    ATAQUES = [
        Ataque("Redemoinho", "magico", 1.0, 0, "Ataque mágico que também rouba mana"),
        Ataque("Rasteira", "fisico", 1.0, 6, "30% de chance de atordoar"),
        Ataque("Fumaça do Cachimbo", "magico", 1.3, 12, "Fumaça encantada com 1.3x o MATK"),
    ]

    def __init__(self, nome: str = "Saci"):
        super().__init__(nome, hp=120, mp=30, speed=20, atk=20, matk=33,
                         defense=10, mdefense=18,
                         lenda="Travesso de uma perna só que surge nos redemoinhos de vento.")

    def escolher_alvo(self, alvos: list) -> Combatente:
        """Sobrescrita: o Saci persegue quem tem mais mana."""
        return max(alvos, key=lambda alvo: alvo.mp)

    def atacar(self, alvo: Combatente, ataque: Ataque = None) -> None:
        ataque = self.preparar_ataque(ataque)
        dano = self.golpe(ataque, alvo)
        if ataque.nome == "Rasteira" and dano > 0:
            self.tentar_atordoar(alvo, 0.30)
        elif ataque.nome == "Redemoinho" and alvo.esta_vivo():
            roubo = min(self.MANA_ROUBADA, alvo.mp)
            if roubo > 0:
                alvo.mp -= roubo
                print(f"   🌀 {self.nome} rouba {roubo} de MP de {alvo.nome} "
                      f"e esconde no gorro vermelho!")
