"""
Módulo com a classe Ataque.

Cada herói e monstro possui uma lista de objetos Ataque (composição).
O Ataque guarda apenas os dados da habilidade; quem decide o que ela faz
é o método atacar() de cada classe (polimorfismo).
"""


class Ataque:
    """Representa uma habilidade de combate."""

    TIPOS_VALIDOS = ("fisico", "magico", "cura")

    def __init__(self, nome: str, tipo: str, poder: float = 1.0, custo: int = 0,
                 descricao: str = ""):
        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError(f"Tipo de ataque inválido: {tipo}")
        self.nome = nome
        self.tipo = tipo            # "fisico" usa atk x defense; "magico" usa matk x mdefense
        self.poder = poder          # multiplicador aplicado ao atk ou matk
        self.custo = custo          # mana gasta
        self.descricao = descricao

    def __str__(self) -> str:
        custo = "sem custo" if self.custo == 0 else f"{self.custo} MP"
        return f"{self.nome} ({custo}) - {self.descricao}"

    def __repr__(self) -> str:
        return (f"Ataque(nome='{self.nome}', tipo='{self.tipo}', "
                f"poder={self.poder}, custo={self.custo})")
