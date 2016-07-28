#encoding=utf-8

import codecs
import glob
from urlparse import urlparse
from os import path, makedirs
import pytoml as toml

from utils import RedIt


class ComakeParser:
    def __init__(self):
        self.comake = {}
        self.total_sources = set()
        self.total_headers = set()
        self.dep_include_list = []
        self.dep_library_list = []
        self.repo_path_dict = {}

    def Parse(self, path = 'COMAKE'):
        try:
            with codecs.open(path, 'r', 'utf-8') as f:
                comake = toml.load(f)
        except toml.TomlError as e:
            print RedIt("[ERROR] {} load failed".format(path))
        else:

            size = len(comake['output'])

            for i in range(size):
                sources_set = _parsePath(comake['output'][i]['sources'])
                comake['output'][i]['sources'] = ' '.join(sources_set)
                headers_set = _parsePath(comake['output'][i]['headers'])
                comake['output'][i]['headers'] = ' '.join(headers_set)
                comake['output'][i]['a'] = comake['output'][i]['a'].strip()
                comake['output'][i]['so'] = comake['output'][i]['so'].strip()
                self.total_sources.update(sources_set)
                self.total_headers.update(headers_set)

            comake['total_sources'] = ' '.join(self.total_sources)
            comake['total_headers'] = ' '.join(self.total_headers)

            comake['include_path'] = ' '.join(['-I' + s for s in comake['include_path'].split()])
            comake['library_path'] = ' '.join(['-L' + s for s in comake['library_path'].split()])
            self.comake = comake
            if 'use_local_makefile' not in self.comake.keys():
                self.comake['use_local_makefile'] = 0

            self._parseDepPath()

        return self.comake

    def _parseDepPath(self):
        deps = self.comake['dependency']
        for dep in deps:
            if len(dep["uri"]) == 0:
                continue
            url = urlparse(dep["uri"])
            if url == "file":
                pass
            else:
                local_path = [self.comake['repo_root'], url.netloc]
                local_path.extend([x for x in url.path.split('/') if x])
                local_path[-1] = local_path[-1].rstrip('.git')
                repo_path = path.sep.join(local_path)
                if not path.isdir(repo_path):
                    makedirs(repo_path)
                self.repo_path_dict[repo_path] = dep['uri']
                self.dep_include_list.append(path.sep.join([repo_path, 'output', 'include']))
                self.dep_library_list.append(path.sep.join([repo_path, 'output', 'library']))
        # add dep include and library path into comake
        self.comake['dep_include_path'] = ' \\\n'.join(['-I' + s for s in self.dep_include_list])
        self.comake['dep_library_path'] = ' \\\n'.join(['-L' + s for s in self.dep_library_list])

    def getComake(self):
        return self.comake

    def getDepRepoPath(self):
        return self.repo_path_dict


def _validateComake(comake):
    # TODO add COMAKE format validation check
    pass


def _parsePath(line):
    res = set()
    for token in line.split():
        if '*' in token:
            for path in glob.glob(token.strip()):
                res.add(path)
        else:
            res.add(token)
    return res