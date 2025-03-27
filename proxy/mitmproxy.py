class Proxy:
	def __init__(self):
		pass

	def request(self, flow):
		req = flow.request

		if req.host == 'www.auxbrain.com':
			# change host to http://localhost:5000
			# pass
			flow.request.scheme = 'http'
			flow.request.host = 'localhost'
			flow.request.port = 5000

addons = [
    Proxy()
]