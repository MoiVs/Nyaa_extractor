import json
import requests
import re

from NyaaPy.nyaa import Nyaa

JSON_FILE_NAME: str = "parameters.json"
PATH = "./data"

class RegularSearch:
    # handles search on the nyaa.si website and return a Torrent object

    # TODO : add a season attribute
    # TODO : add an analyzer (with regex ?) to be sure ep and season number are not random numbers
    def __init__(
            self,
            name: str,
            episode: int,
            season: int,
            quality: str = "",
            translate_team: str = ""
    ):
        self._name = name.lower()
        self._episode = str(episode)
        self._season = str(season)
        self._quality = quality.lower()
        self._translate_team = translate_team.lower()

    def search(self) -> object:
        # searches a torrent on nyaa.si from the parameters it was specified
        nyaa = Nyaa()
        results = nyaa.search(keyword=" ".join([self._name, self._episode, self._translate_team, self._quality]))

        # no results
        if len(results) == 0:
            return None
        else:
            return self.search_result(results)

    def search_result(self, results: list) -> object:
        # checks if the ep number and season check a certain pattern with regex
        len_results = len(results)
        i = 0
        regex = "".join(["(- 0{0,1}", self._episode, ")|(S0{0,1}1E0{0,1}", self._season, ")"])
        while i < len_results:
            if re.search(regex, results[i].name):
                return results[i]
            else:
                i += 1

        # The good torrent name wasn't found in any
        return None


class ParameterJson:
    def __init__(self):
        self._torrent_list: list = []
        self._json_dic: dict = {}

    def read_json(self):
        # Reads a JSON file to extract all of its entry
        # Gets all episodes available from the ep number in JSON file to the newest

        with open(JSON_FILE_NAME, 'r') as json_file:
            self._json_dic = json.load(json_file)

        for entry in self._json_dic['entry']:
            self.process_entry(entry)

        # Writes Json File with updated episode number
        with open(JSON_FILE_NAME, 'w') as json_file:
            json.dump(self._json_dic, json_file)

    def process_entry(self, entry: dict):
        # process one entry of the JSON file

        name = entry["name"]
        episode = entry["episode"]
        season = entry["season"]
        translate_team = entry["translate_team"]
        quality = entry["quality"]

        # while a new episode might be available
        has_new_episode = True
        while has_new_episode:
            regular_search = RegularSearch(name, episode, season, translate_team, quality)
            result = regular_search.search()

            # there is no episode available
            if result is None:
                has_new_episode = False
            # there is an episode available
            # increment the episode number to search for the next one
            else:
                print(episode)
                episode = int(int(episode) + 1)
                self._torrent_list.append(result)

        # update episode entry with the episode that isn't yet available
        entry["episode"] = episode

    def download_torrent(self):
        # downloads torrent from the torrent list
        for torrent in self._torrent_list:
            download_url = torrent.download_url
            r = requests.get(download_url, allow_redirects=True)
            open(PATH + "/" + torrent.name + ".torrent", 'wb').write(r.content) # TODO variable global avec PATH
            print('"' + torrent.name + '" downloaded', sep="")


parameter_json = ParameterJson()
parameter_json.read_json()
parameter_json.download_torrent()
