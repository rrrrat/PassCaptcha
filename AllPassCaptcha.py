import os
if os.path.dirname(__file__) != os.getcwd():
    from .handle.tx_captcha import TX
    from .handle.ali_captcha import ALI
else:
    from handle.tx_captcha import TX
    from handle.ali_captcha import ALI


__version__ = '0.0.3'

