##
# @file materialize.py
# @package openmoc.materialize
# @brief The materialize module provides utility functions to read and write
#        multi-group materials cross-section data from HDF5 binary file format.
# @author William Boyd (wboyd@mit.edu)
# @date April 23, 2013

from log import *
import sys

if 'openmoc.gnu.double' in sys.modules:
    openmoc = sys.modules['openmoc.gnu.double']
elif 'openmoc.gnu.single' in sys.modules:
    openmoc = sys.modules['openmoc.gnu.single']
elif 'openmoc.icpc.double' in sys.modules:
    openmoc = sys.modules['openmoc.icpc.double']
elif 'openmoc.icpc.single' in sys.modules:
    openmoc = sys.modules['openmoc.icpc.single']
elif 'openmoc.bgxlc.double' in sys.modules:
    openmoc = sys.modules['openmoc.bgxlc.double']
elif 'openmoc.bgxlc.single' in sys.modules:
    openmoc = sys.modules['openmoc.bgxlc.single']
else:
    from openmoc import *

##
# @brief
# @param filename
# @return a list of materials for OpenMOC
def materialize(filename):

    xs_types = ['Total XS', 'Absorption XS', 'Scattering XS', \
                    'Fission XS', 'Nu Fission XS', 'Chi',\
                    'Diffusion Coefficient']
    materials = {}

    # Check that the filename is a string
    if not isinstance(filename, str):
        py_printf('ERROR', 'Unable to materialize using filename %s ' + \
                      'since it is not a string', str(filename))


    ############################################################################
    #                               HDF5 DATA FILES
    ############################################################################
    if filename.endswith('.hdf5'):

        import h5py
        import numpy as np

        # Create a h5py file handle for the file
        f = h5py.File(filename)

        # Check that the file has an 'energy groups' attribute
        if not 'Energy Groups' in f.attrs:
            py_printf('ERROR', 'Unable to materialize file %s since it ' + \
                          'does not contain an \'Energy Groups\' attribute', \
                          filename)
    
        num_groups = f.attrs['Energy Groups']

        # Check that the number of energy groups is an integer
        if not isinstance(num_groups, int):
            py_printf('ERROR', 'Unable to materialize file %s since the ' + \
                          'number of energy groups %s is not an integer', \
                          filename, str(num_groups))

        material_names = list(f)

        # Loop over each material and 
        for name in material_names:

            py_printf('INFO', 'Importing material %s', str(name))

            new_material = openmoc.Material(openmoc.material_id())
            new_material.setNumEnergyGroups(int(num_groups))

            # Retrieve and load the cross-section data into the material object


            if 'Total XS' in f[name]:
                new_material.setSigmaT(f[name]['Total XS'][...])

            if 'Scattering XS' in f[name]:
                new_material.setSigmaS(f[name]['Scattering XS'][...])
            
            if 'Fission XS' in f[name]:
                new_material.setSigmaF(f[name]['Fission XS'][...])
            
            if 'Nu Fission XS' in f[name]:
                new_material.setNuSigmaF(f[name]['Nu Fission XS'][...])
            
            if 'Chi' in f[name]:
                new_material.setChi(f[name]['Chi'][...])

            if 'Diffusion Coefficient' in f[name]:
                new_material.setDifCoef(f[name]['Diffusion Coefficient'][...])

            if 'Buckling' in f[name]:
                new_material.setBuckling(f[name]['Buckling'][...])

            if 'Absorption XS' in f[name]:
                new_material.setSigmaA(f[name]['Absorption XS'][...])

            new_material.checkSigmaT()

            # Add this material to the list
            materials[name] = new_material


    ############################################################################
    #                      PYTHON DICTIONARY DATA FILES
    ############################################################################
    elif filename.endswith('.py'):

        import imp
        data = imp.load_source(filename, filename).dataset

        # Check that the file has an 'energy groups' attribute
        if not 'Energy Groups' in data.keys():
            py_printf('ERROR', 'Unable to materialize file %s since it ' + \
                      'does not contain an \'Energy Groups\' attribute', \
                      filename)
    
        num_groups = data['Energy Groups']

        # Check that the number of energy groups is an integer
        if not isinstance(num_groups, int):
            py_printf('ERROR', 'Unable to materialize file %s since the ' + \
                          'number of energy groups %s is not an integer', \
                          filename, str(num_groups))

        data = data['Materials']
        material_names = data.keys()

        # Loop over each material and 
        for name in material_names:

            py_printf('INFO', 'Importing material %s', str(name))

            new_material = openmoc.Material(openmoc.material_id())
            new_material.setNumEnergyGroups(int(num_groups))
            
            if 'Total XS' in data[name].keys():
                new_material.setSigmaT(data[name]['Total XS'])
                                    
            if 'Scattering XS' in data[name].keys():
                new_material.setSigmaS(data[name]['Scattering XS'])

            if 'Fission XS' in data[name].keys():
                new_material.setSigmaF(data[name]['Fission XS'])

            if 'Nu Fission XS' in data[name].keys():
                new_material.setNuSigmaF(data[name]['Nu Fission XS'])

            if 'Chi' in data[name].keys():
                new_material.setChi(data[name]['Chi'])
              
            if 'Diffusion Coefficient' in data[name].keys():
                new_material.setDifCoef(data[name]['Diffusion Coefficient'])

            if 'Buckling' in data[name].keys():
                new_material.setBuckling(data[name]['Buckling'])

            if 'Absorption XS' in data[name].keys():
                new_material.setSigmaA(data[name]['Absorption XS'])

            # Add this material to the list
            materials[name] = new_material


    ############################################################################
    #                      UNSUPPORTED DATA FILE TYPES
    ############################################################################
    else:
        py_printf('ERROR', 'Unable to materialize using filename %s ' + \
                      'since it has an unkown extension. Supported ' + \
                      'extension types are .hdf5 and .py', filename)



    # Return the list of materials
    return materials
