from enum import Enum


class ModeEnum(str, Enum):
    main = "main"
    current = "current"
    analysis = "analysis"

class TypesOfSportsModel(Enum):
    football: str = "ФУТБОЛ"
    volleyball: str = "ВОЛЕЙБОЛ"
    basketball: str = "БАСКЕТБОЛ"
    handball: str = "ГАНДБОЛ"
    tennis: str = "ТЕННИС"


rus_types_sports = [member.value for member in TypesOfSportsModel]
english_types_sports = [member.name for member in TypesOfSportsModel ]
dct_rus_to_eng = {member.value: member.name for member in TypesOfSportsModel}
