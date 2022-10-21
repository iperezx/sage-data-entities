# sage-data-entities
This python package is meant to combine all the different data entities of Sage.
## Build python package
Build process:
```
python3 setup.py bdist_wheel
```
Install package:
```
pip3 install dist/sage_data_entities-0.1.0-py3-none-any.whl
```
Uninstall package:
```
rm -rf dist build sage_data_entities.egg-info && pip3 uninstall sage_data_entities -y
```

## Walkthrough

For basic usage with no transformations on the data:
```
import sage_data_entities.data_entities as sdt
url = 'https://sage-data-api.nrp-nautilus.io/api/v1/sensor-hardware-data'
data_entity = sdt.DataEntityBase(url)
data = data_entity.getData()
data
```

The current Sage Data Entities and supported are the following:
- Nodes
- Sensors
- Edge Code Repository (ECR)
- Sage Data Repository (SDR)
- Edge Scheduler (ES)

For adding another data entity of the Sage ecosystem, a user will need to use `DataEntityBase` and then write their own `get_{ENTITY}_Data` function to perform the needed data transformation. For further details, any of the child classes in [data_entities](./sage_data_entities/data_entities.py) will be great references.

For more detail walkthrough, reference the [walkthrough notebook](/docs/notebooks/walkthrough.ipynb)

## Merge
For each data entity, there are both a primary key (maybe a tuple of keys) and a foreign key.

Primary keys:
- Nodes: `nodeID`
- Sensors: `sensorID`
- Edge Code Repository (ECR): `TBD`
- Sage Data Repository (SDR): (`timestamp`,`name`) 
- Edge Scheduler (ES): `TBD`

We will start with SDR as the source for the merges because that is the location of the plugins outputted data.

Merge different data entitites (starting with SDR):
- SDR with Nodes: `nodeID`
- SDR+Nodes with Sensors: `sensor`
- SDR+Nodes+Sensor with ECR: `pluginID`
- SDR+Nodes+Sensor+ECR with ES: `id`

Other possible merges if a user is not interested in looking at the plugins data as the starting point or not joining all the data entities (not an exhaustive list):
- Nodes with Sensors, key=`sensors`: shows the sensors that are available on the node
- ECR with ES, key=`id`: shows plugin runtime performance, comparisons between different versions of a plugin, or what runtime input parameters were used.
- SDR with ES, key=`TBD`: similar to above but now seeing the data directly