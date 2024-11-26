from cx_Freeze import setup, Executable

setup(
    name="atualizador",
    version="1.0.0",
    description="Atualizador Automático",
    options={
        "build_exe": {
            "packages": ["os", "sys", "requests", "packaging", "json", "subprocess", "logging"],
            "includes": ["packaging.version", "packaging.specifiers"],
            "include_msvcr": True,
            "optimize": 2,
        }
    },
    executables=[Executable("atualizador.py", base=None, target_name="atualizador.exe")]
)
