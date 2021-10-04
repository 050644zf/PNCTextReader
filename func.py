import lupa
from pathlib import Path

lua = lupa.LuaRuntime(unpack_returned_tuples=True)

def loadLuaFile(filePath:Path):
    with open(filePath, encoding='utf-8') as luaFile:
        luaCode = luaFile.read()

    luaTable = lua.eval(f'''
        function()
            {luaCode}
        end''')
    
    return luaTable