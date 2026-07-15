import asyncio
import logging

import time
from asyncua import Server, ua

from enums import Unit




async def startServer(endpoint, numVerticalROIs, numHorizontalROIs, VerticalROIs, HorizontalROIs, thermalFrameAvailableEvent, geometryLock, stopEvent, units = Unit.PIXELS):
    '''
    Starts the OPCUA server.
    '''
    if thermalFrameAvailableEvent is None or geometryLock is None or stopEvent is None:
        raise ValueError("One or more required arguments are None. Please provide valid threading.Event and threading.Lock objects.")
    _logger = logging.getLogger(__name__)
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint(endpoint)
    server.set_server_name("Geometry Measurement Server")
    server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
    server.set_security_IDs(["Anonymous"])
    
    # set up our own namespace, not really necessary but should as spec
    uri = "http://geometrymeasurement.io"
    idx = await server.register_namespace(uri)
    
    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    vertobj = await server.nodes.objects.add_object(idx, "verticalGeometryObject")
    vertvariables = []
    for i in range(numVerticalROIs):
        vertvariables.append(await vertobj.add_variable(idx, f"verticalROI{i+1}", i+1))
        await vertvariables[i].set_writable()
    horizobj = await server.nodes.objects.add_object(idx, "horizontalGeometryObject")
    horizvariables = []
    for i in range(numHorizontalROIs):
        horizvariables.append(await horizobj.add_variable(idx, f"horizontalROI{i+1}", 5+(i+1)))
        await horizvariables[i].set_writable()
        
    unitobj = await server.nodes.objects.add_object(idx, "unitObject")
        # Measurement value
    match unit:
        case Unit.PIXELS:
            units = ' pixels' 
        case Unit.MM:
            units = 'mm'
        case Unit.CM:
            units = 'cm'
        case _:
            units = 'units'
    unitvar = await unitobj.add_variable(idx, "unit", units)
        
    
    
    
    _logger.info("Starting server!")
    loops = 0
    startTime = time.time()
    async with server:
        for i in range(len(vertvariables)):
            old_val = await vertvariables[i].get_value()

            _logger.info("Initialise value of verticalROI %d to %.1f", i+1, old_val)

        for i in range(len(horizvariables)):
            old_val = await horizvariables[i].get_value()
            _logger.info("Initialise value of horizontalROI %d to %.1f", i+1, old_val)
            
        while True:
            loops += 1
            elapsedTime = time.time() - startTime
            if elapsedTime >= 10:
                endTime = time.time()
                elapsedTime = endTime - startTime
                print(f"Server processed {loops} frames in {elapsedTime:.2f} seconds. Average FPS: {loops / elapsedTime+0.0001:.2f}")
                startTime = time.time()
                loops = 0
            if not stopEvent.is_set():
                thermalFrameAvailableEvent.wait()  # Wait for the event to be set
                await updateServer(server, vertvariables, horizvariables, VerticalROIs, HorizontalROIs, geometryLock)
                thermalFrameAvailableEvent.clear()  # Clear the event for the next iteration
            else:
                _logger.info("Stop event set. Stopping server.")
                break
 

async def updateServer(server, vertvariables, horizvariables, VerticalROIs, HorizontalROIs, geometryLock):
    '''
    updates the values of the vertical and horizontal ROIs in the server with new values. Should be subscribed to the event where these values are calculated.
    '''
    _logger = logging.getLogger(__name__)
    if geometryLock is None:
        _logger.warning("Geometry lock is None. Cannot update server.")
        return
    with geometryLock:
        for i in range(len(vertvariables)):
            old_val = await vertvariables[i].get_value()
            _logger.info("Set value of verticalROI%d from %.1f to %.1f", i, type(old_val), type(VerticalROIs[i]))
            if not isinstance(VerticalROIs[i], (int, float)):
                await vertvariables[i].write_value(VerticalROIs[i].item())
            else:
                await vertvariables[i].write_value(VerticalROIs[i])
        for i in range(len(horizvariables)):
            old_val = await horizvariables[i].get_value()
            _logger.info("Set value of horizontalROI%d from %.1f to %.1f", i, old_val, HorizontalROIs[i])
            print(f"Set value of horizontalROI%d from %.1f to %.1f", i, old_val, HorizontalROIs[i])
            if not isinstance(HorizontalROIs[i], (int, float)):
                await horizvariables[i].write_value(HorizontalROIs[i].item())
            else:
                await horizvariables[i].write_value(HorizontalROIs[i])
    await asyncio.sleep(0.01)

    # while True:
    #     asyncio.run(updateServer(server, [random.uniform(0, 100) for _ in range(5)], [random.uniform(0, 100) for _ in range(5)]), debug=True)