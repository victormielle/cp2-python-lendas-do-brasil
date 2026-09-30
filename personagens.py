"""
Módulo dos heróis jogáveis.

Personagem é a classe pai dos heróis. Guerreiro e Mago são obrigatórias;
Arqueiro e Paladino são as classes inéditas do grupo. Cada uma tem sua
própria lista de ataques e sobrescreve o método atacar() (polimorfismo).
"""
import random

from ataque import Ataque
from combatente import Combatente


class Personagem(Combatente):
    """Classe pai de todos os heróis jogáveis."""

    LIMITE_POCAO = 0.30  # no modo automático, bebe poção abaixo de 30% do HP
    CURA_POCAO = 0.35    # a poção recupera 35% do HP máximo

    def __init__(self, nome: str, hp: int, mp: int, speed: int, atk: int, matk: int,
                 defense: int, mdefense: int, pocoes: int = 1):
        super().__init__(nome, hp, mp, speed, atk, matk, defense, mdefense)
        self.__pocoes = pocoes  # privado (name mangling): só muda pelos métodos

    # ------------------------------------------------------------------
    # Encapsulamento das poções (getter e setter)
    # ------------------------------------------------------------------
    def get_pocoes(self) -> int:
        return self.__pocoes

    def set_pocoes(self, quantidade: int) -> None:
        if quantidade >= 0:
            self.__pocoes = quantidade
        else:
            print("A quantidade de poções não pode ser negativa.")

    def usar_pocao(self) -> bool:
        if self.__pocoes <= 0:
            print(f"   {self.nome} procura uma poção, mas a bolsa está vazia!")
            return False
        if self.hp == self.get_hp_max():
            print(f"   {self.nome} está com a vida cheia e guarda a poção.")
            return False
        self.__pocoes -= 1
        curado = self.curar(int(self.get_hp_max() * self.CURA_POCAO))
        print(f"   🧪 {self.nome} bebe uma poção e recupera {curado} HP "
              f"({self.hp}/{self.get_hp_max()})")
        return True

    def precisa_de_pocao(self) -> bool:
        return self.__pocoes > 0 and self.hp < self.get_hp_max() * self.LIMITE_POCAO

    # ------------------------------------------------------------------
    # Sobrescritas
    # ------------------------------------------------------------------
    def escolher_ataque(self) -> Ataque:
        """Heróis usam o ataque ofensivo mais poderoso (mais caro) que conseguem pagar."""
        ofensivos = [a for a in self.ataques_disponiveis() if a.tipo != "cura"]
        return max(ofensivos, key=lambda ataque: ataque.custo)

    def escolher_alvo(self, alvos: list) -> Combatente:
        """Heróis são estratégicos: focam no inimigo com menos HP."""
        return min(alvos, key=lambda alvo: alvo.hp)

    def ficha(self) -> str:
        return super().ficha() + f"\n   Poções: {self.__pocoes}"


class Guerreiro(Personagem):
    """Tanque de linha de frente: muito HP, muita defesa e dano físico alto."""

    ATAQUES = [
        Ataque("Espadada", "fisico", 1.0, 0, "Ataque físico básico"),
        Ataque("Investida", "fisico", 1.2, 6, "Avança com o escudo; 30% de chance de atordoar"),
        Ataque("Golpe Brutal", "fisico", 1.6, 12, "Golpe devastador com 1.6x o ATK"),
    ]

    def __init__(self, nome: str):
        super().__init__(nome, hp=150, mp=30, speed=8, atk=26, matk=5,
                         defense=16, mdefense=8)

    def atacar(self, alvo: Combatente, ataque: Ataque = None) -> None:
        ataque = self.preparar_ataque(ataque)
        dano = self.golpe(ataque, alvo)
        if ataque.nome == "Investida" and dano > 0:
            self.tentar_atordoar(alvo, 0.30)


class Mago(Personagem):
    """Frágil, mas com o maior ataque mágico. Começa com 2 poções."""

    ATAQUES = [
        Ataque("Golpe de Cajado", "fisico", 1.0, 0, "Ataque físico fraco, para quando a mana acaba"),
        Ataque("Bola de Fogo", "magico", 1.0, 10, "Ataque mágico básico"),
        Ataque("Raio Congelante", "magico", 0.8, 14, "Congela o alvo; 40% de chance de atordoar"),
        Ataque("Meteoro", "magico", 1.4, 24, "Magia mais poderosa, com 1.4x o MATK"),
    ]

    def __init__(self, nome: str):
        super().__init__(nome, hp=95, mp=90, speed=10, atk=8, matk=42,
                         defense=8, mdefense=18, pocoes=2)

    def atacar(self, alvo: Combatente, ataque: Ataque = None) -> None:
        ataque = self.preparar_ataque(ataque)
        dano = self.golpe(ataque, alvo)
        if ataque.nome == "Raio Congelante" and dano > 0:
            self.tentar_atordoar(alvo, 0.40)


class Arqueiro(Personagem):
    """Classe inédita: o mais rápido do time, perfura armaduras e pode atirar duas vezes."""

    CHANCE_DISPARO_DUPLO = 0.25
    ATAQUES = [
        Ataque("Flecha Comum", "fisico", 1.0, 0, "Ataque físico básico"),
        Ataque("Flecha Perfurante", "fisico", 1.0, 8, "Ignora metade da defesa física do alvo"),
        Ataque("Flecha Envenenada", "fisico", 0.8, 10, "Envenena o alvo por 3 turnos"),
    ]

    def __init__(self, nome: str):
        super().__init__(nome, hp=110, mp=40, speed=16, atk=27, matk=6,
                         defense=11, mdefense=11)

    def atacar(self, alvo: Combatente, ataque: Ataque = None) -> None:
        ataque = self.preparar_ataque(ataque)
        reducao = 0.5 if ataque.nome == "Flecha Perfurante" else 0.0
        dano = self.golpe(ataque, alvo, reducao)
        if ataque.nome == "Flecha Envenenada" and dano > 0:
            self.envenenar(alvo, 7)

        # Passiva: qualquer flecha tem chance de sair um disparo extra
        if alvo.esta_vivo() and random.random() < self.CHANCE_DISPARO_DUPLO:
            print("   🏹 Disparo duplo!")
            self.golpe(self.ATAQUES[0], alvo)


class Paladino(Personagem):
    """Classe inédita: guerreiro sagrado que mistura dano físico e mágico e sabe se curar."""

    ATAQUES = [
        Ataque("Martelada", "fisico", 1.0, 0, "Ataque físico básico"),
        Ataque("Golpe Sagrado", "fisico", 1.0, 10, "Dano físico + metade do dano mágico"),
        Ataque("Julgamento Divino", "magico", 1.3, 16, "Luz sagrada com 1.3x o MATK"),
        Ataque("Luz Curativa", "cura", 0.30, 15, "Recupera 30% do HP máximo"),
    ]

    def __init__(self, nome: str):
        super().__init__(nome, hp=135, mp=55, speed=7, atk=23, matk=22,
                         defense=18, mdefense=16)

    def escolher_ataque(self) -> Ataque:
        """Sobrescrita: se estiver ferido (abaixo de 40%) e tiver mana, prefere se curar."""
        cura = self.ATAQUES[3]
        if self.hp < self.get_hp_max() * 0.40 and cura.custo <= self.mp:
            return cura
        return super().escolher_ataque()

    def atacar(self, alvo: Combatente, ataque: Ataque = None) -> None:
        ataque = self.preparar_ataque(ataque)
        if ataque.nome == "Luz Curativa":
            curado = self.curar(int(self.get_hp_max() * ataque.poder))
            print(f"   ✨ {self.nome} invoca Luz Curativa e recupera {curado} HP "
                  f"({self.hp}/{self.get_hp_max()})")
        elif ataque.nome == "Golpe Sagrado":
            dano = (self.calcular_dano(self.atk, alvo.defense)
                    + self.calcular_dano(self.matk, alvo.mdefense) // 2)
            self._golpear(alvo, dano, ataque.nome)
        else:
            self.golpe(ataque, alvo)
