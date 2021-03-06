import logging
import urlparse
from urllib import quote as urlquote

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web import proxy, server, resource
from twisted.web.server import NOT_DONE_YET

from YubiEncoder import YubiEncoder


class YubiReverseProxyClient(proxy.ProxyClient):
    def __init__(self, command, rest, version, headers, data, father):
        self.encoder = YubiReverseProxyClientFactory.encoder()
        self.encoder.modifyRequest(command, rest, father)
        proxy.ProxyClient.__init__(self, command, rest, version, headers, data, father)

    def handleResponsePart(self, buffer):
        logging.debug("Got Response Part: %d bytes." % len(buffer))
        buffer = self.encoder.modifyResponseBuffer(buffer)
        self.fixContentLength(buffer)
        proxy.ProxyClient.handleResponsePart(self, buffer)

    def handleStatus(self, version, code, message):
        logging.debug("Got status: %s - %s" % (str(code), message))
        self.father.setResponseCode(int(code), message)

    def fixContentLength(self, buffer):
        self.father.responseHeaders.setRawHeaders(b"Content-Length", [b"%s" % (len(buffer))])

class YubiReverseProxyClientFactory(proxy.ProxyClientFactory):
    protocol = YubiReverseProxyClient
    encoder = YubiEncoder

class YubiReverseProxy(proxy.ReverseProxyResource):
    proxyClientFactoryClass = YubiReverseProxyClientFactory


