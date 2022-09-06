import os
if os.path.dirname(__file__) != os.getcwd():
    from .handle.tx_capcha import TX
else:
    from handle.tx_capcha import TX


__version__ = '0.0.1'
