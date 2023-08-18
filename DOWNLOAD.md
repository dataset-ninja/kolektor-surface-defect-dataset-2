Dataset **KolektorSDD2** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/C/G/ZF/9TTjWYXwMwrpsucVTLE6haAzRWg6pLtiAQLpkDBv1DQka4p6uClOX6417Q9byIJuyHtcyViHAG5eKj1qBn7EewCtzExChwu7Ta7jD2eifK6m8EeLtIA79cvHNjVW.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='KolektorSDD2', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](https://go.vicos.si/kolektorsdd2).