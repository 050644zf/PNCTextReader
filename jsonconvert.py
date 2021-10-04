from os import read
import lupa
from pathlib import Path
import func
import re
import json

lua = lupa.LuaRuntime(unpack_returned_tuples=True)

langs = ['zh-CN']

jsonDataPath = Path('PNCStoryJson')
dataPath = Path('GFLPNCData')

stRe  = r"cpt(?P<chapter>\d+)_(?P<mode>\w)_(?P<part>\d+)_(?P<section>\d+)"


avgPath = Path('lua/AvgConfig')
locPath = Path('lua/LuaConfigs/locale_text.lua')
avgListPath = Path('lua/LuaConfigs/story_avg.lua')
charPath = Path('lua/LuaConfigs/avg_character.lua')
contentTypePath = Path('lua/Game/Avg/Enum/eAvgContentType.lua')

prop = {1:'Subtitle', 2:'name', 3:'name', 4:'name',5:'name'}
modeDict = {'e':'标准', 'h':'暗域'}



def reader(avgcfg, avglang):
    storyDict = {}

    for idx in list(avgcfg):
        if isinstance(idx, int):
            line = avgcfg[idx]
            lineDict = {}
            lineDict['id'] = f'node{idx}'
            lineDict['attributes'] = {}
            if line['contentType']:
                ct = line['contentType']
                lineDict['prop'] = prop[ct]
                if ct in (2,5):
                    lineDict['attributes']['name'] = ''
                elif ct == 3:
                    lineDict['attributes']['name'] = locTable[charTable[line['speakerHeroId']]['name']]
                elif ct == 4:
                    lineDict['attributes']['name'] = avglang[line['speakerName']]
                
                lineDict['attributes']['content'] = avglang[line['content']]

            
            if line['branch']:
                lineDict['prop'] = 'Decision'
                values = [f"option{value}" for value in list(line['branch']) if isinstance(value, int)]
                options = ';'.join([avglang[line['branch'][value]['content']] for value in list(line['branch'])  if isinstance(value, int)])
                lineDict['attributes']['values'] = values
                lineDict['attributes']['options'] = options
                lineDict['targetLine'] = {f"option{value}":line['branch'][value]['jumpAct'] for value in list(line['branch'])  if isinstance(value, int)}
                if line['branch']['disableSelected']:
                    line['disableSelected'] = True
                    lineDict['targetLine']['finalAct'] = line['branch']['finalAct']
                else:
                    line['disableSelected'] = False
                
            if line['nextId']:
                lineDict['nextId'] = line['nextId']
                storyDict[f'node{idx}'] = lineDict
            elif line['isEnd']:
                storyDict[f'node{idx}'] = lineDict
            else:
                lineDict['nextId'] = idx+1
                storyDict[f'node{idx}'] = lineDict

    return storyDict

        



if __name__ == '__main__':
    for lang in langs:

        charTable = func.loadLuaFile(dataPath/lang/charPath)
        charTable = charTable()

        locTable = func.loadLuaFile(dataPath/lang/locPath)
        locTable = locTable()

        menu = {}

        storyPathList = (dataPath/lang/avgPath).iterdir()

        for storyFolder in storyPathList:
            storyid = storyFolder.stem
            try:
                (chapter, mode, part, section) = re.match(stRe, storyid).group('chapter', 'mode', 'part', 'section')
            except AttributeError:
                continue
            if not f'Chapter {chapter}' in menu:
                menu[f'Chapter {chapter}'] = {}
            
            menu[f'Chapter {chapter}'][storyid] = {'name':f'{modeDict[mode]} {part}-{section}'}


            avgcfg = None
            avglang = None

            for luaFile in storyFolder.iterdir():
                if 'AvgCfg' in luaFile.stem:
                    avgcfg = func.loadLuaFile(luaFile)
                    avgcfg = avgcfg()
                elif 'AvgLang' in luaFile.stem:
                    avglang = func.loadLuaFile(luaFile)
                    avglang = avglang()

            storyJson = reader(avgcfg, avglang)

            jsonPath = jsonDataPath/storyFolder.relative_to(dataPath).parent/Path(str(storyid)+'.json')
            jsonPath.parent.mkdir(exist_ok=True, parents=True)
            with open(jsonPath, 'w', encoding='utf-8') as jsonFile:
                json.dump(storyJson, jsonFile, indent=4, ensure_ascii=False)

        with open(jsonDataPath/Path(lang)/Path('menu.json'),'w', encoding='utf-8') as jsonFile:
            json.dump(menu, jsonFile, indent=4, ensure_ascii=False)






