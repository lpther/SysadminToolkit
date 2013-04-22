from sysadmintoolkit import exception


class Plugin(object):
    '''
    '''

    def __init__(self, name):
        '''
        '''
        if isinstance(name, str):
            self.name = name
        else:
            raise exception.CommandPromptError('Error initializing plugin : Plugin name requires a string (1st arg)', errno=302)

        # Plugin's current mode
        self.currentmode = None

    def register_labels(self, mode):
        '''
        '''
        pass

    def enter_mode(self, mode):
        '''
        '''
        self.register_labels(mode)

    def leave_mode(self, mode):
        '''
        '''
        pass

    def get_name(self):
        '''
        '''
        return self.name

    def get_current_mode(self):
        '''
        '''
        return self.currentmode

    def get_dynamic_keyword_list(self, keyword):
        '''
        '''
        return []
