import abc
import geopandas as gpd
import ndjson
import pandas as pd
import requests
from requests.exceptions import HTTPError
from shapely.geometry import Point

class DataEntityInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'getData') and 
                callable(subclass.getDataRaw) or 
                NotImplemented)

    @abc.abstractmethod
    def getData(self,query=None,isVerify=True):
        """Get data from API"""
        raise NotImplementedError

class DataEntityBase(DataEntityInterface):
    """Base class for data entity"""
    def __init__(self,urlAPI):
        self.urlAPI = urlAPI

    def getData(self,query=None,isVerify=True):
        """Get data from API"""
        try:
            response = requests.request("GET", self.urlAPI,json=query,verify=isVerify)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        return response

    def convertToJson(self,data,jsonCls=None):
        responseJSON = data.json(cls=jsonCls)
        return responseJSON

class SDR(DataEntityBase):
    def __init__(self, urlAPI):
        super().__init__(urlAPI)
        self.suffix = '_sdr'
        self.exceptColmns = ['node','plugin','sensor']
        self.timeColumn = 'timestamp'
        self.renameColumns = {'meta.node_sdr':'nodeID','meta.plugin_sdr':'pluginID'}
        self.splitDelimName = '-'
        self.splitDelimVersion = ':'

    def getSDRData(self,query,jsonCls=ndjson.Decoder,isVerify=False):
        pluginData = self.getData(query,isVerify)
        pluginDataJson = self.convertToJson(pluginData,jsonCls)
        pluginDataDF = pd.DataFrame(pluginDataJson)

        pluginDataDF[self.timeColumn] = pd.to_datetime(pluginDataDF[self.timeColumn])
        meta = pd.DataFrame(pluginDataDF["meta"].tolist())
        meta.rename({c: "meta." + c for c in meta.columns}, axis="columns", inplace=True)
        pluginDataDF = pluginDataDF.join(meta)
        pluginDataDF.drop(columns=["meta"], inplace=True)
        # pluginDataDF = pluginDataDF.drop('meta',1).join(pd.DataFrame.from_dict(pluginDataDF.meta.to_dict(),orient='index'))
        pluginDataDF.columns = pluginDataDF.columns.map(lambda x : x+self.suffix if x not in self.exceptColmns else x)
        pluginDataDF.rename(columns=self.renameColumns,inplace=True)
        pluginDataDF[['pluginID', 'pluginVersion_sdr']] = pluginDataDF['pluginID'].str.split(self.splitDelimVersion, 1, expand=True)
        pluginDataDF.pluginID = pluginDataDF.pluginID.str.split(self.splitDelimName)
        pluginDataDF.pluginID = pluginDataDF.pluginID.str.get(1)
        return pluginDataDF

class Nodes(DataEntityBase):
    def __init__(self, urlAPI):
        super().__init__(urlAPI)
        self.suffix = '_node'
        self.exceptColmns = ['nodeID','geometry']
        self.epsg = "EPSG:4326"
        self.renameColumns = {'id':'nodeID'}

    def getNodeData(self):
        nodeData = self.getData()
        nodeDataJson = self.convertToJson(nodeData)
        nodeDataDF = pd.DataFrame.from_dict(nodeDataJson['data'], orient='columns')
        nodeDataDF['lon'] = pd.to_numeric(nodeDataDF['lon'],errors='coerce')
        nodeDataDF['lat'] = pd.to_numeric(nodeDataDF['lat'],errors='coerce')
        nodeDataDF.rename(columns=self.renameColumns,inplace=True)
        nodeDataDF.nodeID = nodeDataDF.nodeID.str.lower()

        geometry = [Point(xy) for xy in zip(nodeDataDF.lon, nodeDataDF.lat)]
        nodeDataGDF = gpd.GeoDataFrame(nodeDataDF.drop(['lon', 'lat'], axis=1), crs=self.epsg, geometry=geometry)
        nodeDataGDF.columns = nodeDataGDF.columns.map(lambda x : x+self.suffix if x not in self.exceptColmns else x)
        return nodeDataGDF

class Sensors(DataEntityBase):
    def __init__(self, urlAPI):
        super().__init__(urlAPI)
        self.exceptColmns = ['product_name']
        self.suffix = '_sensor'
        self.renameColumns = {'product_name':'sensor'}

    def getSensorHardwareData(self):
        sensorData = self.getData()
        sensorDataJSON = self.convertToJson(sensorData)
        sensorDataDf = pd.DataFrame.from_dict(sensorDataJSON['data'], orient='columns')
        sensorDataDf.columns = sensorDataDf.columns.map(lambda x : x+self.suffix if x not in self.exceptColmns else x)
        sensorDataDf.rename(columns=self.renameColumns,inplace=True)
        return sensorDataDf

class ECR(DataEntityBase):
    def __init__(self, urlAPI):
        super().__init__(urlAPI)
        self.exceptColmns = ['name']
        self.suffix = '_ecr'
        self.sagePortalEndpoint = 'https://portal.sagecontinuum.org/apps/app/'
        self.renameColumns = {'name':'pluginID'}

    def getECRData(self):
        ecrData = self.getData()
        ecrDataJSON = self.convertToJson(ecrData)
        ecrDataDf = pd.DataFrame.from_dict(ecrDataJSON['data'], orient='columns')
        ecrDataDf.drop('source',1).join(pd.DataFrame.from_dict(ecrDataDf.source.to_dict(),orient='index'))
        ecrDataDf.columns = ecrDataDf.columns.map(lambda x : x+self.suffix if x not in self.exceptColmns else x)
        ecrDataDf.rename(columns=self.renameColumns,inplace=True)
        ecrDataDf['app_endpoint_ecr'] = self.sagePortalEndpoint + ecrDataDf.namespace_ecr + '/' + ecrDataDf.pluginID
        return ecrDataDf