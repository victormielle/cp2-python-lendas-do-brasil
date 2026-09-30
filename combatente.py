"""
Módulo com a classe base Combatente.

Heróis (Personagem) e monstros (Monstro) herdam desta classe, que reúne
os atributos obrigatórios do CP2: hp, mp, speed, atk, matk, defense e mdefense.
"""
import random

from ataque import Ataque


class Combatente:
    """Representa qualquer ser que participa de uma batalha (herói ou monstro)."""

    CHANCE_CRITICO = 0.10        # 10% de chance de acerto crítico
    MULTIPLICADOR_CRITICO = 1.5  # crítico causa 50% a mais de dano
    TURNOS_VENENO = 3            # duração padrão do veneno/sangramento

    # Cada subclasse define a sua própria lista de ataques
    ATAQUES = [Ataque("Ataque", "fisico", 1.0, 0, "Ataque físico básico")]

    def __init__(self, nome: str, hp: int, mp: int, speed: int, atk: int,
                 matk: int, defense: int, mdefense: int):
        self.nome = nome
        self.hp = hp                # vida
        self.mp = mp                # mana
        self.speed = speed          # velocidade (define quem age primeiro)
        self.atk = atk              # ataque físico
        self.matk = matk            # ataque mágico
        self.defense = defense      # defesa física
        self.mdefense = mdefense    # defesa mágica
        self._hp_max = hp           # protegido: usado em curas e na barra de vida
        self._mp_max = mp           # protegido
        self.dano_causado = 0       # estatística para o "destaque da batalha"
        # efeitos de status
        self.atordoado = False
        self.veneno_turnos = 0
        self.veneno_dano = 0

    # ------------------------------------------------------------------
    # Getters (encapsulamento dos valores máximos)
    # ------------------------------------------------------------------
    def get_hp_max(self) -> int:
        return self._hp_max

    def get_mp_max(self) -> int:
        return self._mp_max

    # ------------------------------------------------------------------
    # Estado do combatente
    # ------------------------------------------------------------------
    def esta_vivo(self) -> bool:
        return self.hp > 0

    def receber_dano(self, dano: int) -> int:
        """Reduz o hp (sem deixar negativo) e devolve o dano efetivamente recebido."""
        self.hp = max(0, self.hp - dano)
        return dano

    def curar(self, valor: int) -> int:
        """Recupera hp sem ultrapassar o máximo e devolve quanto foi curado."""
        hp_antes = self.hp
        self.hp = min(self._hp_max, self.hp + valor)
        return self.hp - hp_antes

    def processar_efeitos(self) -> bool:
        """Aplica veneno e atordoamento no início do turno.
        Retorna True se o combatente pode agir neste turno."""
        if self.veneno_turnos > 0:
            self.veneno_turnos -= 1
            self.hp = max(0, self.hp - self.veneno_dano)
            print(f"   ☣  {self.nome} sofre {self.veneno_dano} de dano por veneno "
                  f"({self.hp}/{self._hp_max} HP)")
            if not self.esta_vivo():
                print(f"   ☠  {self.nome} não resistiu ao veneno!")
                return False
        if self.atordoado:
            self.atordoado = False
            print(f"   💫 {self.nome} está atordoado e perde a vez!")
            return False
        return True

    # ------------------------------------------------------------------
    # Escolha de ataques
    # ------------------------------------------------------------------
    def ataques_disponiveis(self) -> list:
        """Ataques que o combatente tem mana suficiente para usar."""
        return [ataque for ataque in self.ATAQUES if ataque.custo <= self.mp]

    def escolher_ataque(self) -> Ataque:
        """Por padrão, sorteia um ataque disponível. Subclasses podem sobrescrever."""
        return random.choice(self.ataques_disponiveis())

    def preparar_ataque(self, ataque: Ataque = None) -> Ataque:
        """Define o ataque do turno (escolhendo um, se necessário) e gasta a mana."""
        if ataque is None or ataque.custo > self.mp:
            ataque = self.escolher_ataque()
        self.mp -= ataque.custo
        return ataque

    def escolher_alvo(self, alvos: list) -> "Combatente":
        """Por padrão, escolhe um alvo vivo aleatório. Subclasses podem sobrescrever."""
        return random.choice(alvos)

    # ------------------------------------------------------------------
    # Combate
    # ------------------------------------------------------------------
    @staticmethod
    def calcular_dano(ataque: int, defesa: int) -> int:
        """Cálculo simples: ataque - defesa, com dano mínimo de 1."""
        return max(1, ataque - defesa)

    def golpe(self, ataque: Ataque, alvo: "Combatente", reducao_defesa: float = 0.0) -> int:
        """Aplica um ataque físico (atk - defense) ou mágico (matk - mdefense).
        reducao_defesa permite ignorar parte da defesa do alvo (0.5 = metade)."""
        if ataque.tipo == "magico":
            valor, defesa = self.matk, alvo.mdefense
        else:
            valor, defesa = self.atk, alvo.defense
        dano = self.calcular_dano(int(valor * ataque.poder),
                                  int(defesa * (1 - reducao_defesa)))
        return self._golpear(alvo, dano, ataque.nome)

    def atacar(self, alvo: "Combatente", ataque: Ataque = None) -> None:
        """Ataque genérico. As subclasses sobrescrevem (polimorfismo)."""
        ataque = self.preparar_ataque(ataque)
        self.golpe(ataque, alvo)

    def _golpear(self, alvo: "Combatente", dano: int, habilidade: str) -> int:
        """Aplica o dano no alvo, com chance de crítico, exibe e devolve o dano causado."""
        print(f"   {self.nome} usa {habilidade} em {alvo.nome}!")
        if random.random() < self.CHANCE_CRITICO:
            dano = int(dano * self.MULTIPLICADOR_CRITICO)
            print("   💥 ACERTO CRÍTICO!")
        dano_real = alvo.receber_dano(dano)
        self.dano_causado += dano_real
        if dano_real > 0:
            print(f"   → {alvo.nome} sofre {dano_real} de dano "
                  f"({alvo.hp}/{alvo.get_hp_max()} HP)")
        if not alvo.esta_vivo():
            print(f"   ☠  {alvo.nome} foi derrotado!")
        return dano_real

    # ------------------------------------------------------------------
    # Efeitos especiais usados pelas subclasses
    # ------------------------------------------------------------------
    def tentar_atordoar(self, alvo: "Combatente", chance: float) -> None:
        if alvo.esta_vivo() and random.random() < chance:
            alvo.atordoado = True
            print(f"   💫 {alvo.nome} ficou atordoado e vai perder a próxima vez!")

    def envenenar(self, alvo: "Combatente", dano_por_turno: int) -> None:
        if alvo.esta_vivo():
            alvo.veneno_turnos = self.TURNOS_VENENO
            alvo.veneno_dano = dano_por_turno
            print(f"   ☣  {alvo.nome} foi envenenado! ({dano_por_turno} de dano por "
                  f"{self.TURNOS_VENENO} turnos)")

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------
    def barra_hp(self, tamanho: int = 20) -> str:
        cheio = round(tamanho * self.hp / self._hp_max)
        return "█" * cheio + "░" * (tamanho - cheio)

    def ficha(self) -> str:
        """Ficha com atributos e ataques (usada no menu 'Ver fichas')."""
        linhas = [f"{self.nome} ({self.__class__.__name__})",
                  f"   HP {self._hp_max} | MP {self._mp_max} | SPD {self.speed}",
                  f"   ATK {self.atk} | MATK {self.matk} | "
                  f"DEF {self.defense} | MDEF {self.mdefense}",
                  "   Ataques:"]
        linhas += [f"     - {ataque}" for ataque in self.ATAQUES]
        return "\n".join(linhas)

    def __str__(self) -> str:
        status = ""
        if not self.esta_vivo():
            status = "  ☠"
        else:
            if self.veneno_turnos > 0:
                status += " [ENVENENADO]"
            if self.atordoado:
                status += " [ATORDOADO]"
        return (f"{self.nome:<16} [{self.barra_hp()}] "
                f"HP {self.hp:>3}/{self._hp_max:<3} MP {self.mp:>2}/{self._mp_max}{status}")

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(nome='{self.nome}', hp={self.hp}, mp={self.mp}, "
                f"speed={self.speed}, atk={self.atk}, matk={self.matk}, "
                f"defense={self.defense}, mdefense={self.mdefense})")
