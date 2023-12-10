import sys
from pathlib import Path
import shutil

# М'який знак ("ь"), російський твердий знак ("ъ") та апостроф ("'")
# латиницею не відтворюються, тому їх відповідник - це ""

CYRILLIC_SYMBOLS = ("а", "б", "в", "г", "ґ", "д", "е", "є", "ж", "з", "и",
                    "і", "ї", "й", "к", "л", "м", "н", "о", "п", "р", "с",
                    "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ь", "ю", "я",
                    "ъ", "ы", "э", "ё", "'")

TRANSLIT_SYMBOLS = ("a", "b", "v", "h", "g", "d", "e", "ie", "zh", "z", "y",
                    "i", "i", "i", "k", "l", "m", "n", "o", "p", "r", "s",
                    "t", "u", "f", "kh", "ts", "ch", "sh", "shch", "", "iu", "ia",
                    "", "y", "e", "ie", "")

SPECIFIC_CYRILLIC_SYMBOLS_WORD_START_WITH = ("є", "ї", "й", "ю", "я")

SPECIFIC_TRANSLIT_SYMBOLS_WORD_START_WITH = ("ye", "yi", "y", "yu", "ya")

SORT_FILE_SETTINGS = {
    "images": ('JPEG', 'PNG', 'JPG', 'SVG'),
    "video": ('AVI', 'MP4', 'MOV', 'MKV'),
    "documents": ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
    "audio": ('MP3', 'OGG', 'WAV', 'AMR'),
    "archives": ('ZIP', 'GZ', 'TAR'),
    "other": (),
}

log_output = ""


def log(input_str: str, new_line_count: int = 1):
    global log_output
    log_output += input_str + "\n" * new_line_count


def convert_to_str(input_data, shift: int = 0):
    # ToDo: type(input) = set(), type(input) = tuple()

    res = ""
    prefix = " " * shift

    if type(input_data) is dict:
        res += prefix + "{\n"
        for key, value in input_data.items():
            res += prefix + " " * 2 + str(key) + ":\n"
            res += convert_to_str(value, shift + 2)
        res += prefix + "}\n"
    elif type(input_data) is list:
        res += prefix + "[\n"
        for element in input_data:
            res += convert_to_str(element, shift + 2)
        res += prefix + "]\n"
    else:
        res += prefix + str(input_data) + "\n"

    return res


def make_translit_dictionary(cyrillic_symbols: tuple, translit_symbols: tuple):

    translit_dictionary = {}

    for c_symbol, t_symbol in zip(cyrillic_symbols,  translit_symbols):

        translit_dictionary[ord(c_symbol)] = t_symbol

        translit_dictionary[ord(c_symbol.upper())] = t_symbol.capitalize()

    return translit_dictionary


def make_transliteration(input_str: str):

    common_translit_dictionary = make_translit_dictionary(
        CYRILLIC_SYMBOLS, TRANSLIT_SYMBOLS)

    first_letter_translit_dictionary = make_translit_dictionary(SPECIFIC_CYRILLIC_SYMBOLS_WORD_START_WITH,
                                                                SPECIFIC_TRANSLIT_SYMBOLS_WORD_START_WITH)

    # Буквосполучення "зг" відтворюється латиницею як "zgh"
    # (наприклад,  Згорани - Zghorany, Розгон - Rozghon) на
    # відміну від "zh" -  відповідника  української  літери
    # "ж".

    input_str = input_str.replace("зг", "zgh").replace("Зг", "Zgh")\
        .replace("ЗГ", "ZGh").replace("зГ", "zGh")

    result = ""

    prev_char = ""

    for char in input_str:
        if char.lower() not in CYRILLIC_SYMBOLS:
            result += char
        else:
            if char.lower() in SPECIFIC_CYRILLIC_SYMBOLS_WORD_START_WITH and prev_char == " ":
                result += char.translate(first_letter_translit_dictionary)
            else:
                result += char.translate(common_translit_dictionary)
        prev_char = char

    return result


def prepare_file_or_folder_name(input_str: str):

    result = ""

    input_str = make_transliteration(input_str)

    for char in input_str:
        result += char if char.isalnum() else "_"

    return result


def init():

    log_file_name = sys.argv[0].replace(".py", ".log")

    if len(sys.argv) == 1:
        log("[ERRO] There is no path to folder for sorting. The script stops working!")
        return "", log_file_name

    folder_path = sys.argv[1]

    # folder_path = "D:\\projects\\goit\\python_developer\\homeworks\\homework_6\\folder_for_sorting"

    folder_pointer = Path(folder_path)

    if not folder_pointer.exists():
        log(f"[ERRO] {folder_path} does not exist. The script stops working!")
        return "", log_file_name

    if not folder_pointer.is_dir():
        log(f"[ERRO] {folder_path} is not a folder. The script stops working!")
        return "", log_file_name

    log(f"[INFO] Script starts working with the folder: {folder_path}.", 2)
    return folder_pointer, log_file_name


def prepare_folder_structure(path_pointer: Path):

    specific_folders = dict()

    log("[INFO] >> Creating specific folders or skipping, if they already exists.", 2)

    for category in SORT_FILE_SETTINGS.keys():
        p = Path(path_pointer, category)
        try:
            p.mkdir(exist_ok=True)
        except:
            log(
                f"[ERRO] >> An exception occurred when creating folder: {p}", 2)
            return {}
        else:
            log(f"[INFO] >> Folder: {p}", 2)
            specific_folders[category] = p

    return specific_folders


def if_file_exists(path_pointer: Path):
    """ Функція приймає вказівник на файл/директорію.
        Далі в циклі перевіряємо, чи він/вона існує.
        Якщо так, то додаємо до імені файлу/директорії 
        індекс (1, 2, 3, ...) і повторюємо цикл.
        Якщо ні, то повертаємо останній опрацьований вказівник 
        на файл/директорію. 
    """
    f_name_origin = path_pointer.stem
    f_number = 1

    while path_pointer.exists():
        log("{:40}: {}".format(
            "[WARN] >> File/folder already exists", path_pointer))

        f_name = f_name_origin + "_" + str(f_number)
        path_pointer = path_pointer.with_stem(f_name)
        f_number += 1
    else:
        return path_pointer


def normalize(path_pointer: Path):

    log("{:40}: {}".format(
        "[INFO] >> Original file/folder name", path_pointer))

    f_name = path_pointer.stem

    new_f_name = prepare_file_or_folder_name(f_name)

    if new_f_name == f_name:
        log("[INFO] >> No need to rename", 2)
    else:
        new_path_pointer = path_pointer.with_stem(new_f_name)

        # Можлива ситуація, коли ми нормалізували ім'я файлу/теки,
        # але такий файл/тека вже існує.
        # Наприклад, в теці знаходяться 2 файли: nnn.txt та ннн.txt
        # Обходимо цю ситуацію викликом функції if_file_exists()

        new_path_pointer = if_file_exists(new_path_pointer)

        try:
            path_pointer = path_pointer.replace(new_path_pointer)
        except:
            log(
                f"[WARN] >> An exception occurred when renaming {path_pointer}. Skipping!", 2)
        else:
            log("{:40}: {}".format(
                "[INFO] >> Renamed file/folder name", new_path_pointer), 2)

    return path_pointer


def processing_folder(
        path_pointer: Path,
        ignored_folders: dict = {},
        need_normalize_itself: bool = True,
        folder_processing_data: dict = {
            "known_file_extens": [],
            "unknown_file_extens": [],
            "files_by_categories": {},
        }):

    if not path_pointer.is_dir():
        return {}

    elif path_pointer.is_dir() and path_pointer in ignored_folders.values():
        # Якщо директорія в словнику ignore_list, то ігноруємо її.
        log("{:40}: {}".format("[INFO] >> Skip this folder", path_pointer), 2)

    elif path_pointer.is_dir() and not list(path_pointer.iterdir()):
        # Директорія порожня. Зразу видаляємо її.
        try:
            path_pointer.rmdir()
        except:
            log(
                f"[WARN] >> An exception occurred when removing empty folder {path_pointer}. Skipping!", 2)
        else:
            log("{:40}: {}".format(
                "[INFO] >> Remove empty folder", path_pointer), 2)

    else:
        path_pointer = normalize(
            path_pointer) if need_normalize_itself else path_pointer
        for item in path_pointer.iterdir():
            if item.is_dir():
                processing_folder(item, ignored_folders,
                                  True, folder_processing_data)
            else:
                normalize_file = normalize(item)

                f_exten = normalize_file.suffix.upper().replace(".", "")

                # Формуємо folder_processing_data
                if f_exten:
                    if f_exten not in folder_processing_data["known_file_extens"] and \
                            f_exten not in folder_processing_data["unknown_file_extens"]:
                        for category in SORT_FILE_SETTINGS.keys():
                            if f_exten in SORT_FILE_SETTINGS[category]:
                                folder_processing_data["known_file_extens"].append(
                                    f_exten)
                                folder_processing_data["files_by_categories"].setdefault(
                                    category, []).append(normalize_file)
                                break
                        else:
                            folder_processing_data["unknown_file_extens"].append(
                                f_exten)
                            folder_processing_data["files_by_categories"].setdefault(
                                "other", []).append(normalize_file)
                    elif f_exten in folder_processing_data["known_file_extens"]:
                        for category in SORT_FILE_SETTINGS.keys():
                            if f_exten in SORT_FILE_SETTINGS[category]:
                                folder_processing_data["files_by_categories"][category].append(
                                    normalize_file)
                    elif f_exten in folder_processing_data["unknown_file_extens"]:
                        folder_processing_data["files_by_categories"]["other"].append(
                            normalize_file)
                else:
                    folder_processing_data["files_by_categories"].setdefault(
                        "other", []).append(normalize_file)

    return folder_processing_data


def move_processed_files(input_data: dict, folders_for_sorting: dict):
    for category, files in input_data["files_by_categories"].items():
        for file in files:
            log("{:40}: {}".format("[INFO] >> Move file name", file))
            new_file = Path(folders_for_sorting[category], file.name)

            # Якщо файл з таким ім'ям вже є в теці призначення, то
            # обходимо цю ситуацію викликом функції if_file_exists().
            new_file = if_file_exists(new_file)

            try:
                file = file.replace(new_file)
            except:
                log("[WARN] >> An exception occurred when moving file. Skipping!", 2)
            else:
                log("{:40}: {}".format("[INFO] >> To file name", new_file), 2)

            if category == "archives":
                log("{:40}: {}".format("[INFO] >> Unpack archive name", file))
                path_to_unpack = Path(
                    folders_for_sorting["archives"], file.stem)

                if path_to_unpack.exists():
                    # Якщо тека, в яку ми збираємось розпакувати архів,
                    # вже присутня, то архів не розпакрвуємо.
                    log("{:40}: {}".format(
                        "[INFO] >> To folder name", path_to_unpack))
                    log("[WARN] >> Folder already exists. Skipping!", 2)
                else:
                    try:
                        shutil.unpack_archive(file, str(path_to_unpack))
                    except:
                        log("[WARN] >> Damaged archive. Remove it!", 2)
                        file.unlink()
                    else:
                        log("{:40}: {}".format(
                            "[INFO] >> To folder name", path_to_unpack), 2)


def build_folders_tree(path_pointer: Path, ignored_folders: dict = {}, data: dict = {}):

    if not path_pointer.is_dir():
        return {}

    elif path_pointer.is_dir() and path_pointer in ignored_folders.values():
        pass

    elif path_pointer.is_dir() and not list(path_pointer.iterdir()):
        data.setdefault(path_pointer, [])

    else:
        for item in path_pointer.iterdir():
            if item.is_dir():
                data.setdefault(path_pointer, []).append(item)
                build_folders_tree(item, ignored_folders, data)
            else:
                data.setdefault(path_pointer, []).append(item)
                continue
    return data


def remove_empty_folders(folders_tree: dict):

    flag = True

    while flag:

        for folder in folders_tree.keys():

            if len(folders_tree[folder]) == 0:

                log("{:40}: {}".format(
                    "[INFO] >> Remove empty folder", folder), 2)
                parent_folder = Path(folder).parent

                try:
                    Path(folder).rmdir()
                except:
                    log("[WARN] >> An exception occurred when removing empty folder. Skipping!", 2)
                    folders_tree[folder].append("Removing exception")
                else:
                    folders_tree.pop(folder)
                    folders_tree[parent_folder].remove(folder)

                    break

        else:
            flag = False


def main():

    folder_pointer, log_file_name = init()

    if folder_pointer:
        log("[INFO] > Prepare folder structure.", 2)
        folders_for_sorting = prepare_folder_structure(folder_pointer)
        if folders_for_sorting:
            log("[INFO] > Done.", 2)

            log("[INFO] > Start processing folder.", 2)
            folder_processing_data = processing_folder(folder_pointer,
                                                       ignored_folders=folders_for_sorting,
                                                       need_normalize_itself=False)
            log("[INFO] > Done.", 2)

            log(f"folder_processing_data =\n{convert_to_str(folder_processing_data)}")

            log("[INFO] > Start move/unpack files according to folder_processing_data.", 2)
            move_processed_files(folder_processing_data, folders_for_sorting)
            log("[INFO] > Done.", 2)

            log("[INFO] > Start remove empty folders.", 2)
            folders_tree = build_folders_tree(
                folder_pointer, ignored_folders=folders_for_sorting)
            remove_empty_folders(folders_tree)
            log("[INFO] > Done.", 2)
        else:
            log("[ERRO] The script could not create folders for sorting files. The script stops working!", 2)

    # В директорії, з якої запускається скрипт, створюється
    # файл з ім'ям скрипта та розширенням .log, в який
    # записуються результати роботи скрипта.
    with open(log_file_name, "w", encoding='utf-8') as fd:
        fd.writelines(log_output)

    exit()


if __name__ == '__main__':
    main()
