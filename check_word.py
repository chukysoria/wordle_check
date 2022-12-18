import json
import re
from typing import Dict, Optional

import pandas as pd


class WordleSearch:
    def __init__(self) -> None:
        # Load Dictionary
        with open("dict.json", encoding="utf-8") as file:
            self.word_list: list[str] = json.load(file)

        self.palabra_objetivo: list[str] = [".", ".", ".", ".", "."]
        self.letras_incluidas: Dict[str, int] = dict()
        self.letras_excluidas: str = ""

    def nueva_palabra(self) -> None:
        self.palabra_objetivo = [".", ".", ".", ".", "."]
        self.letras_incluidas = dict()
        self.letras_excluidas = ""

    def create_pattern(self, palabra: str, colores: str) -> Optional[str]:
        letras_incluidas: list[str] = []
        letras_excluidas: list[str] = []
        for i in range(0, len(colores)):
            color = colores[i]
            if color == "G":
                letras_excluidas += palabra[i]
            elif color == "A":
                letras_incluidas += palabra[i]
                if self.palabra_objetivo[i] == ".":
                    self.palabra_objetivo[i] = f"[^{palabra[i]}]"
                else:
                    cond = self.palabra_objetivo[i]
                    self.palabra_objetivo[i] = (
                        cond[: (len(cond) - 1)] + palabra[i] + "]"
                    )
            elif color == "V":
                letras_incluidas += palabra[i]
                self.palabra_objetivo[i] = palabra[i]
            else:
                print(f"Color no reconodido: {color}")
                return
        # Evita añadir letras incluidas antes de salvar
        for letra_excluida in letras_excluidas:
            if letra_excluida not in letras_incluidas:
                self.letras_excluidas += letra_excluida
            else:
                for i in range(0, len(colores)):
                    if colores[i] != "V":
                        if self.palabra_objetivo[i] == ".":
                            self.palabra_objetivo[i] = f"[^{letra_excluida}]"
                        else:
                            cond = self.palabra_objetivo[i]
                            self.palabra_objetivo[i] = (
                                cond[: (len(cond) - 1)] + letra_excluida + "]"
                            )
        # Crea el pattern
        # (?=.o[^r]or)(?=([^r]*r){2,})(?=([^o]*o){2,})(?!.*[siapde].*)
        pattern = "(?=" + "".join(self.palabra_objetivo) + ")"
        if len(letras_incluidas) >= 1:
            unique_letters: list[str] = [*set(letras_incluidas)]
            for letter in unique_letters:
                letter_count = letras_incluidas.count(letter)
                pattern += "(?=([^%s]*%s){%i,})" % (letter, letter, letter_count)

        if len(self.letras_excluidas) >= 1:
            pattern += f"(?!.*[{self.letras_excluidas}].*)"

        return pattern

    def search_pattern(self, pattern: str) -> Optional[list[str]]:
        regex_pattern = re.compile(pattern)
        result = list(filter(regex_pattern.match, self.word_list))
        return result

    def best_words(
        self, palabra, possible_words: list[str], colores: str, pattern: str
    ) -> Optional[list[str]]:
        characters: list[str] = []
        letters_found = []
        for i in range(0, len(colores)):
            if colores[i] != "G":
                letters_found += palabra[i]

        for word in possible_words:
            for i in range(0, len(colores)):
                if colores[i] != "V":
                    characters += word[i]
        letters = pd.Series(characters).value_counts()

        # Letters to be found
        remaining_letters = colores.count("G")

        # Get top letters
        top_letters = letters.nlargest(remaining_letters).index.values.tolist()
        for i in range(0, remaining_letters):
            new_pattern = pattern
            for j in range(0, remaining_letters - i):
                letter = top_letters[j]
                occurreces = 1 + letters_found.count(letter)
                new_pattern += "(?=([^%s]*%s){%i})" % (letter, letter, occurreces)
            words_found = self.search_pattern(new_pattern)
            if words_found and (i == 0 or len(words_found) == len(possible_words)):
                return words_found
            elif words_found:
                # Re-iterate to find best within best
                return self.best_words(palabra, words_found, colores, new_pattern)
        return possible_words


wordle = WordleSearch()

encontrada = False
while not encontrada:
    # Ask word
    palabra = input("Entre palabra:").lower()
    colores = input("Entre colores (Verde, Gris, Amarillo):").upper()

    if len(palabra) != len(colores):
        print("Palabra y colores de distinta longitud")
        exit()

    pattern = wordle.create_pattern(palabra, colores)
    if pattern:
        result = wordle.search_pattern(pattern)
        if not result:
            print("No se han encontrado palabras")
        else:
            print(f"Se han encontrado {len(result)} palabras")
            print("Primeros resultados")
            print(str(result[:10]))
            print("Mejores palabras:")
            best_words = wordle.best_words(palabra, result, colores, pattern)
            print(str(best_words))

    continuar = input("¿Nueva palabra? (s/n):")
    if continuar == "s":
        wordle.nueva_palabra()
