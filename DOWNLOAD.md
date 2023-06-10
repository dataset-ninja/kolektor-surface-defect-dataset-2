Dataset **Kolektor Surface-Defect** can be downloaded in Supervisely format:

 [Download](https://assets.supervise.ly/supervisely-supervisely-assets-public/teams_storage/s/r/P1/JrEfJCgcRmLOTMVAwQ3SidwXmswQV8mbXSupoN995fDqyrwczLAUuE7Mx10HsMuEP6ObS11f6nbUilKUNqADIKVnbKn3CGFJPAe3lFf1LpDqtuNUbRbCIOdDnhAn.tar)

As an alternative, it can be downloaded with dataset-tools package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='Kolektor Surface-Defect', dst_dir='~/dtools/datasets/Kolektor Surface-Defect')
```
The data in original format can be :link: [downloaded here](https://go.vicos.si/kolektorsdd2)