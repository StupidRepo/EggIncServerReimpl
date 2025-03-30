class Proxy:
	def __init__(self):
		pass

	def request(self, flow):
		req = flow.request

		# pass
		if req.host == 'www.auxbrain.com':
			flow.request.scheme = 'http'
			flow.request.host = 'localhost'
			flow.request.port = 5000

addons = [
    Proxy()
]