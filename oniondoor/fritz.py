# -*- coding: utf-8 -*-
import fritzconnection


class FritzWLAN(object):
    """Access count of associated devices from the Fritzbox"""

    def __init__(self,
                 fc=None,
                 address=fritzconnection.FRITZ_IP_ADDRESS,
                 port=fritzconnection.FRITZ_TCP_PORT,
                 user=fritzconnection.FRITZ_USERNAME,
                 password=''):
        super(FritzWLAN, self).__init__()
        if fc is None:
            fc = fritzconnection.FritzConnection(address, port, user, password)
        self.fc = fc

    def action(self, actionname, **kwargs):
        return self.fc.call_action('WLANConfiguration', actionname, **kwargs)

    @property
    def modelname(self):
        return self.fc.modelname

    @property
    def association_numbers(self):
        result = self.action('GetTotalAssociations')
        return result['NewHostNumberOfEntries']
