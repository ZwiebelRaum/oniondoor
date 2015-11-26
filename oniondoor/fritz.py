# -*- coding: utf-8 -*-
import fritzconnection.fritzconnection as fritzconn


class FritzWLAN(object):
    """Access count of associated devices from the Fritzbox"""

    def __init__(self,
                 fc=None,
                 address=fritzconn.FRITZ_IP_ADDRESS,
                 port=fritzconn.FRITZ_TCP_PORT,
                 user=fritzconn.FRITZ_USERNAME,
                 password=''):
        super(FritzWLAN, self).__init__()
        if fc is None:
            fc = fritzconn.FritzConnection(address, port, user, password)
        self.fc = fc

    def action(self, actionname, **kwargs):
        return self.fc.call_action('WLANConfiguration', actionname, **kwargs)

    @property
    def modelname(self):
        return self.fc.modelname

    @property
    def associated_devices(self):
        result = self.action('GetTotalAssociations')
        return result['NewTotalAssociations']
