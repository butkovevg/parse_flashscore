from enum import Enum


class ModeParseEnum(str, Enum):
    all_mode = "all_mode"
    main = "main"
    current = "current"
    analysis = "analysis"


class TypesOfSportsModel(Enum):
    all_types_of_sports: str = "ВCE"
    football: str = "ФУТБОЛ"
    volleyball: str = "ВОЛЕЙБОЛ"
    basketball: str = "БАСКЕТБОЛ"
    handball: str = "ГАНДБОЛ"
    tennis: str = "ТЕННИС"


# Фильтруем ModeParseEnum: исключаем 'all_mode'
list_mode_parse = [member.value for member in ModeParseEnum if member.name != "all_mode"]

# Фильтруем TypesOfSportsModel: исключаем 'all_types_of_sports'
filtered_members = [member for member in TypesOfSportsModel if member.name != "all_types_of_sports"]
rus_list_types_sports = [member.value for member in filtered_members]
english_list_types_sports = [member.name for member in filtered_members]
dct_rus_to_eng = {member.value: member.name for member in filtered_members}
