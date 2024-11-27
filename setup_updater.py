from cx_Freeze import setup, Executable
import sys
import os

# Definir a base como None, pois updater.py é um script em terminal
base = None

# Nome do executável de saída
target_name = "updater.exe"

# Definir arquivos adicionais que devem ser incluídos no build (se necessário)
include_files = ["version.json"]

# Pacotes necessários que o updater.py utiliza
packages = [
    "os",
    "sys",
    "requests",
    "logging",
    "json",
    "shutil",
    "packaging",
    "tqdm",
    "psutil",
    "encodings",
]

# Bibliotecas e pacotes específicos que devem ser incluídos no build
includes = [
    "requests",
    "logging",
    "json",
    "shutil",
    "packaging",
    "tqdm",
    "psutil",
    "encodings",
]

setup(
    name="updater",
    version="1.0.0",
    description="Atualizador - Encaminha Diligência",
    options={
        "build_exe": {
            "packages": packages,
            "includes": includes,
            "include_msvcr": True,
            "include_files": include_files,
            "optimize": 2,
        }
    },
    executables=[Executable("updater.py", base=base, target_name=target_name)]
)
