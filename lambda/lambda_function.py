import json
import time
import uuid

def get_uuid():
    return str(uuid.uuid4())

def get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))    

def loadcams():
    with open('config.json') as f:
        cameras = json.loads(f.read())
    return cameras
    
def lambda_handler(event, context):
    print(event)
    print(context)
    print("\nSTART PROC")
    if event["directive"]['header']['namespace'] == "Alexa.Discovery":
        return handleDiscovery(context, event)
    elif event["directive"]['header']['namespace'] == 'Alexa.CameraStreamController':
        return handleCameraStreamController(context, event)
    elif event["directive"]['header']['namespace'] == 'Alexa':
        return handleAlexa(context, event)


def handleAlexa(context, event):
    cameras= loadcams()
    message_id = event["directive"]['header']['messageId']
    correlationToken = event["directive"]['header']['correlationToken']
    if event["directive"]['header']['name'] == 'ReportState':
        endpointId = event["directive"]['endpoint']['endpointId']
        if cameras[endpointId] is not None:
          header = {
            "namespace": "Alexa",
            "name": "StateReport",
            "messageId": get_uuid(),
            "payloadVersion": "3"
          }
          if correlationToken is not None:
            header['correlationToken'] = correlationToken
          endpoint = {
            "scope": {
              "type": "BearerToken",
              "token": event["directive"]['endpoint']['scope']['token']
            },
            "endpointId": endpointId,
            "cookie": {}
          }
          event ={
            'header': header,
            'endpoint': endpoint,
            'payload':{}
          }
          ctxt ={
            "properties": [
              {
                "namespace": "Alexa.EndpointHealth",
                "name": "connectivity",
                "value": {
                  "value": "OK"
                },
                "timeOfSample": get_utc_timestamp(),
                "uncertaintyInMilliseconds": 0
              }
            ]
          }
          response = {'event': event, 'context': ctxt}
          print(response)
          return response
    return None


def handleDiscovery(context, event):
    cameras= loadcams()
    message_id = event["directive"]['header']['messageId']
    header = {
        "namespace":"Alexa.Discovery",
        "name":"Discover.Response",
        "payloadVersion": "3",
        "messageId": get_uuid()
        }
    if event["directive"]['header']['name'] == 'Discover':
        endpoints = []
        for c in cameras:
            endpoint = {
                      "endpointId": c,
                      "manufacturerName": cameras[c]['manufacturerName'],
                      "manufacturerId" : cameras[c]['manufacturerId'],
                      "description": cameras[c]['manufacturerId'],
                      "friendlyName": cameras[c]['friendlyName'],
                      "displayCategories": ["CAMERA"],
                      "cookie": {
                        
                      },
                      "capabilities": [
                        {
                          "type": "AlexaInterface",
                          "interface": "Alexa.CameraStreamController",
                          "version": "3",
                          "cameraStreamConfigurations" : [
                              {
                                "protocols": ["RTSP"],
                                "resolutions": [{"width":800, "height":440}],
                                "authorizationTypes": ["NONE"],
                                "videoCodecs": ["H264"],
                                "audioCodecs": ["G711"]
                              }
                          ]
                        },
                        {
                        "type": "AlexaInterface",
                        "interface": "Alexa.EndpointHealth",
                        "version": "3",
                        "properties": {
                        "supported": [
                              {
                                "name":"connectivity"
                              }],
                            "proactivelyReported": True,
                            "retrievable": True
                          }
                        },
                        {
                          "type": "AlexaInterface",
                          "interface": "Alexa",
                          "version": "3"
                        }
                      ]                 

                   }
            endpoints.append(endpoint)
        payload = {"endpoints": endpoints}
        response = {'event': { 'header': header, 'payload': payload }}
        print(response)
        return response
    return { 'header': header}


def handleCameraStreamController(context, event):
    cameras= loadcams()
    message_id = event['header']['messageId']
    header =    {
                "namespace": "Alexa.CameraStreamController",
                "name": "Response",
                "messageId": "message_id",
                "payloadVersion": "3",
                "namespace":"Alexa.CameraStreamController",
                "name":"Discover.Response",
                "payloadVersion": "3",
                "messageId": get_uuid()
                }
    if event['header']['correlationToken'] is not None:
        header["correlationToken"] = event['header']['correlationToken']
        
    if event['header']['name'] == 'InitializeCameraStreams':
        endpoint = event["endpoint"].deepcopy()
        del endpoint['cookie']
        
        camera = cameras[endpoint["endpointId"]]
        cameraStreams = []
        cameraStream = {
              "uri" : camera["uri"],
              "idleTimeoutSeconds": camera["idleTimeoutSeconds"],
              "protocol": camera["protocol"],
              "resolution": camera["resolution"],
              "authorizationType": camera["authorizationType"],
              "videoCodec": camera["videoCodec"],
              "audioCodec": camera["audioCodec"],
              "expirationTime": "2073-02-03T16:20:50.52Z"
        }
        cameraStreams.append(cameraStream)
        imageUri = camera["imageUri"]
        payload = {"cameraStreams": cameraStreams, "imageUri": imageUri}
        
        ctxt ={
                    "properties": [
                      {
                        "namespace": "Alexa.EndpointHealth",
                        "name": "connectivity",
                        "value": {
                          "value": "OK"
                        },
                        "timeOfSample": get_utc_timestamp(),
                        "uncertaintyInMilliseconds": 0
                      }
                    ]
                  }
        response = {'event':{ 'header': header,'endpoint': endpoint, 'payload': payload },
        'context':ctxt}
        print(response)
    return response