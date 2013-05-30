import config
import os
from setuptools import setup, find_packages
from distutils.extension import Extension
from distutils.command.build_ext import build_ext
import numpy

# Adapted from Robert McGibbon's CUDA distutils setup provide in open source 
# form here: https://github.com/rmcgibbo/npcuda-example


# Obtain the numpy include directory
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()


if config.cpp_compiler == 'all':
    config.cpp_compiler = ['gcc', 'icpc']

if config.fp_precision == 'all':
    config.fp_precision = ['double', 'single']


extensions = []
extensions.append(Extension(name = '_openmoc', 
                    sources = config.sources['c++'], 
                    library_dirs = config.library_directories['gcc'], 
                    libraries = config.shared_libraries['gcc'],
                    extra_link_args = config.linker_flags['gcc'], 
                    include_dirs = config.include_directories['gcc'],
                    define_macros = config.macros['gcc']['double'],
                    swig_opts = config.swig_flags))
config.sources['c++'].remove('openmoc/openmoc.i')

if config.with_cuda:
    extensions.append(Extension(name = '_openmoc_cuda', 
                        sources = config.sources['cuda'], 
                        library_dirs = config.library_directories['nvcc'], 
                        libraries = config.shared_libraries['nvcc'],
                        extra_link_args = config.linker_flags['nvcc'], 
                        include_dirs = config.include_directories['nvcc'],
                        define_macros = config.macros['nvcc']['double'],
                        swig_opts = config.swig_flags,
                        export_symbols = ['init_openmoc']))
                      
    config.sources['cuda'].remove('openmoc/cuda/openmoc_cuda.i')


for fp in config.fp_precision:
    for cc in config.cpp_compiler:
        distro = 'openmoc_' + cc + '_' + fp 
        swig_interface_file = distro.replace('_', '/') + '/' + distro + '.i'
        config.sources['c++'].append(swig_interface_file)
        ext_name = '_' + distro.replace('.', '_')

        extensions.append(Extension(name = ext_name, 
                    sources = config.sources['c++'], 
                    library_dirs = config.library_directories[cc], 
                    libraries = config.shared_libraries[cc],
                    extra_link_args = config.linker_flags[cc], 
                    include_dirs = config.include_directories[cc],
                    define_macros = config.macros[cc][fp],
                    swig_opts = config.swig_flags))


def customize_compiler(self):
    """inject deep into distutils to customize how the dispatch
    to gcc/nvcc works.
    
    If you subclass UnixCCompiler, it's not trivial to get your subclass
    injected in, and still have the right customizations (i.e.
    distutils.sysconfig.customize_compiler) run on it. So instead of going
    the OO route, I have this. Note, it's kindof like a wierd functional
    subclassing going on."""
    
    # tell the compiler it can processes .cu
    self.src_extensions.append('.cu')

    # save references to the default compiler_so and _comple methods
    default_compiler_so = self.compiler_so
    super_compile = self._compile
    super_link = self.link

    # now redefine the _compile method. This gets executed for each
    # object but distutils doesn't have the ability to change compilers
    # based on source extension: we add it.
    def _compile(obj, src, openmoc, cc_args, extra_postargs, pp_opts):

        if '-DGNU' in pp_opts and os.path.splitext(src)[1] == '.cpp':
            self.set_executable('compiler_so', 'gcc')
            postargs = config.compiler_flags['gcc']

        elif '-DINTEL' in pp_opts and os.path.splitext(src)[1] == '.cpp':
            self.set_executable('compiler_so', 'icpc')
            postargs = config.compiler_flags['icpc']

        elif '-DCUDA' in pp_opts and os.path.splitext(src)[1] == '.cpp':
            if config.cpp_compiler == 'intel':
                self.set_executable('compiler_so', 'icpc')
                postargs = config.compiler_flags['icpc']
            # Default compiler for swigged cuda code file is gcc
            else:
                self.set_executable('compiler_so', 'gcc')
                postargs = config.compiler_flags['gcc']

        elif os.path.splitext(src)[1] == '.cu':
            self.set_executable('compiler_so', 'nvcc')
            postargs = config.compiler_flags['nvcc']

            for item in extra_postargs:
                if 'intel' in item:
                    cc_args.remove(item)

        else:
            raise EnvironmentError('Unable to compile ' + str(src))

        super_compile(obj, src, openmoc, cc_args, postargs, pp_opts)

        # reset the default compiler_so, which we might have changed for cuda
        self.compiler_so = default_compiler_so

    # inject our redefined _compile method into the class
    self._compile = _compile

    def link(target_desc, objects,
             output_filename, output_dir=None, libraries=None,
             library_dirs=None, runtime_library_dirs=None,
             export_symbols=None, debug=0, extra_preargs=None,
             extra_postargs=None, build_temp=None, target_lang=None):

        for obj in objects[:]:
            if '_intel' in obj and '_gnu' in output_filename:
                objects.remove(obj)
            elif '_gnu' in obj and '_intel' in output_filename:
                objects.remove(obj)
            elif '_single' in obj and '_double' in output_filename:
                objects.remove(obj)
            elif '_double' in obj and '_single' in output_filename:
                objects.remove(obj)

        if '-fopenmp' in extra_postargs:
            self.set_executable('linker_so', 'g++')
            self.set_executable('linker_exe', 'g++')

        elif '-openmp' in extra_postargs:
            self.set_executable('linker_so', 'icpc')
            self.set_executable('linker_exe', 'icpc')

        elif 'cuda' in output_filename:
            self.set_executable('linker_so', 'g++')
            self.set_executable('linker_exe', 'g++')

        else:
            raise EnvironmentError('Unable to find a linker')
           
        super_link(target_desc, objects,
                   output_filename, output_dir, libraries,
                   library_dirs, runtime_library_dirs,
                   export_symbols, debug, extra_preargs,
                   extra_postargs, build_temp)

    self.link = link


# run the customize_compiler
class custom_build_ext(build_ext):
    def build_extensions(self):
        customize_compiler(self.compiler)
        build_ext.build_extensions(self)



setup(name = config.package_name,
      version = '0.1',
      description = 'An open source method of characteristics code for ' + \
                    'solving the 2D neutron distribution in nuclear reactors]',
      author = 'Will Boyd',
      author_email = 'wboyd@mit.edu',
      url = 'https://github.com/mit-crpg/OpenMOC',

      # this is necessary so that the swigged python file gets picked up
      ext_modules = extensions,
      packages = find_packages(),

      # inject our custom trigger
      cmdclass={'build_ext': custom_build_ext},

      # since the package has c code, the egg cannot be zipped
      zip_safe=False)
