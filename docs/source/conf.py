import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

import _building

(project,
 pkg,
 release,
 author,
 copyright,

 extensions,
 templates_path,
 exclude_patterns,
 master_doc,
 html_theme,
 html_static_path,
) = _building.sphinx_confs("k3proc")
