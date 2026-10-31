from dataclasses import dataclass

from model.album import Album


@dataclass
class Arco:
    a1: Album
    a2: Album
    peso: int