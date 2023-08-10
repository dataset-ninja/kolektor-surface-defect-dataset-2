Dataset **KolektorSDD2** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/8/u/Oh/cO5QalJxzvpdj5tpeqfFMMsYzFW6DHL37W7mjk0JxaX72ttzfuaIx9llySJ4O3e9pc9G8MGcgtu2CQQQFZBbm1TNN4m1ih5kmfaCr0d06LzX2Z3TOJyQ3of4HFDa.tar)

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

The data in original format can be [downloaded here](https://go.vicos.si/kolektorsdd2)