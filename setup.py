from cx_Freeze import setup, Executable
import sys
import os

base = None
target_name = "encaminha_diligencia.exe"
include_files = ["protocolos.xlsx"]

packages = [
    "os",
    "sys",
    "selenium",
    "chromedriver_autoinstaller",
    "openpyxl",
    "requests",
    "urllib3",
    "colorama",
    "packaging",
    "idna",
    "certifi",
    "charset_normalizer",
    "encodings", 
]

includes = [
    "selenium",
    "chromedriver_autoinstaller",
    "openpyxl",
    "requests",
    "urllib3",
    "colorama",
    "packaging",
    "idna",
    "certifi",
    "chardet",
    "charset_normalizer",
]

setup(
    name="encaminha_diligencia",
    version="1.0.8",
    description="Robô - Encaminha Diligência",
    options={
        "build_exe": {
            "packages": packages,
            "includes": includes,            
            "include_msvcr": True,  
            "include_files": include_files,                   
            "optimize": 2,            
        }
    },
    executables=[Executable("main.py", base=base, target_name=target_name)]
)
