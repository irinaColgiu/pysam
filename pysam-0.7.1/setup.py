#!/usr/bin/python
'''

pysam
*****

'''

import os, sys, glob, shutil, hashlib, re, fnmatch
import platform

name = "pysam"

# collect pysam version
sys.path.insert( 0, "pysam")
import version

version = version.__version__

samtools_exclude = ( "bamtk.c", "razip.c", "bgzip.c", 
                     "main.c", "calDepth.c", "bam2bed.c",
                     "wgsim.c", "md5fa.c", "maq2sam.c",)
samtools_dest = os.path.abspath( "samtools" )
tabix_exclude = ( "main.c", )
tabix_dest = os.path.abspath( "tabix" )

def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
       for filename in fnmatch.filter(files, pattern):
          yield os.path.join(path, filename)

def _update_pysam_files(cf, destdir):
    '''update pysam files applying redirection of ouput'''
    for filename in cf:
        if not filename: continue
        dest = filename + ".pysam.c"
        with open( filename ) as infile:
            with open( dest, "w" ) as outfile:
                outfile.write( '#include "pysam.h"\n\n' )
                outfile.write( re.sub( "stderr", "pysamerr", "".join(infile.readlines()) ) )
            with open( os.path.join( destdir, "pysam.h" ), "w" )as outfile:
                outfile.write ("""#ifndef PYSAM_H
#define PYSAM_H
#include "stdio.h"
extern FILE * pysamerr;
#endif
""")

# copy samtools source
if len(sys.argv) >= 2 and sys.argv[1] == "import":
   if len(sys.argv) < 3: raise ValueError("missing PATH to samtools source directory")
   if len(sys.argv) < 4: raise ValueError("missing PATH to tabix source directory")

   for destdir, srcdir, exclude in zip( 
      (samtools_dest, tabix_dest), 
      sys.argv[2:4],
      (samtools_exclude, tabix_exclude)):

      srcdir = os.path.abspath( srcdir )
      if not os.path.exists( srcdir ): raise IOError( "samtools src dir `%s` does not exist." % srcdir )

      cfiles = locate( "*.c", srcdir )
      hfiles = locate( "*.h", srcdir )
      ncopied = 0
      
      def _compareAndCopy( src, srcdir, destdir, exclude ):

         d, f = os.path.split(src)
         if f in exclude: return None
         common_prefix = os.path.commonprefix( (d, srcdir ) )
         subdir = re.sub( common_prefix, "", d )[1:]
         targetdir = os.path.join( destdir, subdir )
         if not os.path.exists( targetdir ):
            os.makedirs( targetdir )
         old_file = os.path.join( targetdir, f )
         if os.path.exists( old_file ):
            md5_old = hashlib.md5("".join(open(old_file,"r").readlines())).digest()
            md5_new = hashlib.md5("".join(open(src,"r").readlines())).digest()
            if md5_old != md5_new:
               raise ValueError( "incompatible files for %s and %s" % (old_file, src ))

         shutil.copy( src, targetdir )
         return old_file

      for src_file in hfiles:
         _compareAndCopy( src_file, srcdir,destdir, exclude )
         ncopied += 1

      cf = []
      for src_file in cfiles:
         cf.append( _compareAndCopy( src_file, srcdir, destdir, exclude ) )
         ncopied += 1
         
      sys.stdout.write("installed latest source code from %s: %i files copied" % (srcdir, ncopied))
      # redirect stderr to pysamerr and replace bam.h with a stub.
      sys.stdout.write("applying stderr redirection")
     
      _update_pysam_files(cf, destdir)
      

   sys.exit(0)

if len(sys.argv) >= 2 and sys.argv[1] == "refresh":
    sys.stdout.write("refreshing latest source code from .c to .pysam.c")
# redirect stderr to pysamerr and replace bam.h with a stub.
    sys.stdout.write("applying stderr redirection")
    for destdir in ('samtools', 'tabix'):
        pysamcfiles = locate( "*.pysam.c", destdir )
        for f in pysamcfiles: os.remove(f)
        cfiles = locate( "*.c", destdir )
        _update_pysam_files(cfiles, destdir)

    sys.exit(0)

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import Extension, setup

#######################################################
#######################################################
try:
    from Cython.Distutils import build_ext
except ImportError:
    # no Cython available - use existing C code
    cmdclass = { }
    csamtools_sources = [ "pysam/csamtools.c" ]
    tabix_sources = [ "pysam/tabix.c" ]
    tabproxies_sourcess = ["pysam/TabProxies.c" ]
    cvcf_sources = ["pysam/cvcf.c" ]
else:
    cmdclass = { 'build_ext' : build_ext }
    csamtools_sources = [ "pysam/csamtools.pyx" ]
    tabix_sources = [ "pysam/ctabix.pyx" ]
    tabproxies_sources = ["pysam/TabProxies.pyx" ]
    cvcf_sources = ["pysam/cvcf.pyx" ]

#######################################################
classifiers = """
Development Status :: 2 - Alpha
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows :: Windows NT/2000
Operating System :: OS Independent
Operating System :: POSIX
Operating System :: POSIX :: Linux
Operating System :: Unix
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Bioinformatics
"""

#######################################################
## Windows compatibility
if platform.system()=='Windows':
    include_os = ['win32']
    os_c_files = ['win32/getopt.c']
else:
    include_os = []
    os_c_files = []

#######################################################
samtools = Extension(
    "csamtools",              
    csamtools_sources +\
        [ "pysam/%s" % x for x in (
                "pysam_util.c", )] +\
        glob.glob( os.path.join( "samtools", "*.pysam.c" )) +\
        os_c_files + \
        glob.glob( os.path.join( "samtools", "*", "*.pysam.c" ) ),
    library_dirs=[],
    include_dirs=[ "samtools", "pysam" ] + include_os,
    libraries=[ "z", ],
    language="c",
    define_macros = [('_FILE_OFFSET_BITS','64'),
                     ('_USE_KNETFILE','')], 
    )

tabix = Extension(
    "ctabix",                   
    tabix_sources +\
       [ "pysam/%s" % x for x in ( "tabix_util.c", )] +\
        os_c_files + \
       glob.glob( os.path.join( "tabix", "*.pysam.c" ) ),
    library_dirs=[],
    include_dirs=[ "tabix", "pysam" ] + include_os,
    libraries=[ "z", ],
    language="c",
    define_macros = [('_FILE_OFFSET_BITS','64'),
                     ('_USE_KNETFILE','')], 
    )

tabproxies = Extension(
    "TabProxies",               
    tabproxies_sources + os_c_files,
    library_dirs=[],
    include_dirs= include_os,
    libraries=[ "z", ],
    language="c",
    )

cvcf = Extension(
    "cvcf",                   
    cvcf_sources + os_c_files,
    library_dirs=[],
    include_dirs= ["tabix",] + include_os,
    libraries=[ "z", ],
    language="c",
    )

metadata = {
    'name': name,
    'version': version,
    'description': "pysam", 
    'long_description': __doc__,
    'author': "Andreas Heger",
    'author_email': "andreas.heger@gmail.com",
    'license': "MIT",
    'platforms': "ALL",
    'url': "http://code.google.com/p/pysam/",
    'py_modules': [
      "pysam/__init__", 
      "pysam/Pileup", 
      "pysam/version" ],
    # cython larger that 0.16 for yield support
    'requires' : ['cython (>=0.16)'],
    'ext_modules': [samtools, tabix, tabproxies, cvcf ],
    'cmdclass' : cmdclass,
    'install_requires' : ['cython>=0.12.1',], 
    # do not pack in order to permit linking to csamtools.so
    'zip_safe' :False,
    'use_2to3': True,
    }

if sys.version_info[0] < 3:
    metadata['py_modules'].append("pysam/namedtuple")

if __name__=='__main__':
   dist = setup(**metadata)
