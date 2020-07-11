import requests
from bs4 import BeautifulSoup
from json import loads
from config import DEF_API_KEY

class Translate:

    """
    Errors:
        400: Something went wrong.
        404: Nothing Found.
    """

    def __init__(self, language):
        self.language = language
        self.url = 'https://www.google.com/search?q='
        self.def_url = 'https://dictionaryapi.com/api/v3/references/thesaurus/json/$word$?key=' + DEF_API_KEY # api key from dictionaryapi.com

    def translate(self, text):
        data = requests.get(self.url + text.replace(' ', '+') + ' meaning in ' + self.language)
        print(data.text)
        if data.status_code not in (200, 201):
            return 400

        soup = BeautifulSoup(data.text, 'html.parser')

        parent_1 = soup.find('div', {'class':['BNeawe', 'iBp4i', 'AP7Wnd']})

        # using the resolveType because what if soup returns None instead of the BeautifulSoup instance; so then soup must be the instace not None
        parent_2 = self.resolveType(parent_1).find('div', {'class':['BNeawe', 'iBp4i', 'AP7Wnd']})
        output = self.resolveType(parent_2).find('span', {'dir': 'rtl'})

        return output.string if output else parent_2.string if parent_2 else 404 # sometimes result exists in parent_2 so that is why condintion_2

    def definition(self, word):
        url = self.def_url.replace('$word$', word)
        response = requests.get(url)

        if response.status_code not in (200, 201):
            return 400

        try:
            response = loads(response.text) # loading the json data
            if not response:
                return 404

            response = self.getValidateResponse(response, [[0, dict]])[0] # getting the first item of response and accessing zero key of the object cause' of the function behaveour
            response = self.getValidateResponse(response,
                [['meta', dict],['stems', list]],
                [['meta', dict],['syns', list]],
                [['meta', dict],['ants', list]],
                [['fl', str]],
                [['shortdef', list]],
                [['def', list], [0, dict], ['sseq', list], [0, list], [0, list], [1, dict], ['dt', list], [1, list], [1, list], [0, dict], ['t', str]]
            )
        except:
            response = 400

        return response

    def getValidateResponse(self, data, *args, start=0):
        if start == len(args): return {} # termunating comdition

        arg = args[start] # getting the arg as per recurssion: start gets incremented after every recursive call to access the next item from the args.
        temp = data # temp data to manage multiple lists in the arg; every loop below is changing the temp according to the lists inside the arg; so it means next list will use the previous list(temp) to validate and generate new list(temp)

        for item in arg:
            name_pos, item_type = item[0], item[1] # first index for accessing the the data [could be a key for objects and index number for lists]; item_type for validation purpose
            is_type = lambda: type(temp[name_pos]) == item_type # just to minimize the same code(a condition): getting utilized below

            if type(name_pos) == str: # if name_pos is a key_name of the object; so it means in this iteration the temp is an object
                temp =  temp[name_pos] if name_pos in temp and is_type() and temp[name_pos] else item_type()
            else: # if name_pos is an index_number
                temp = temp[name_pos] if len(temp) > name_pos and is_type() else item_type()

        return {name_pos: temp, **self.getValidateResponse(data, *args, start=start+1)} #setting the name_pos as a key because 1st index of the last list in the arg is a final requirement; and the name_pos is being used here instead of arg[-1][0] because the last iteration above == arg[-1]; and yes temp is the final data
        # then the recurssion happening

    def resolveType(self, html):
        if html:
            return html

        return BeautifulSoup('', 'html.parser')

instance = Translate('Turkish')

while True:
    user = input(':')
    print(instance.translate(user))
    print(instance.definition(user))