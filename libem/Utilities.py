import sys
import os
import pkg_resources

def GetResource(frozen_loc,resource_loc,resource_name):
    ''' Get resource by location and name. This will compensate for frozen or not.
    
    args:
        frozen_loc: location of resource when frozen
        resource_loc: location of resource in package (not frozen)
        resource_name: name of the file
    returns:
        location: The abs location
    '''
    location = None
    
    if getattr(sys,'frozen',False):
        location = os.path.join(sys._MEIPASS,frozen_loc)
        location = os.path.join(location,resource_name)
        location = os.path.abspath(location)
    else:
        location = os.path.abspath(
            pkg_resources.resource_filename(
               resource_loc,
                resource_name
            )
        )
        
    return location