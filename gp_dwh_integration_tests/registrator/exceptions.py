class RegistrationError(Exception):
    '''Base exception for checks registration process'''
    pass


class RegistrationLoopError(RegistrationError):
    '''Excepton on loop in checks dependencies'''
    pass


class DuplicateCheckIdsError(RegistrationError):
    '''Exception on duplicating checks ids'''
    pass


class GetProcessingError(Exception):
    '''Esception for get processing'''
    pass