class ValidatorInfo:
    """
    Klasa przechowująca podstawowe informacje o walidatorze PoS:
    - name: nazwa walidatora
    - stake: liczba posiadanych tokenów
    """
    def __init__(self, name: str, stake: float):
        self.name = name
        self.stake = stake

    def __repr__(self):
        return f"ValidatorInfo(name={self.name}, stake={self.stake})"
