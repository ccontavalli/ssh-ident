# this is a namespace package
import pkg_resources
from ssh_ident import VERSION

pkg_resources.declare_namespace(__name__)

__version__ = VERSION
